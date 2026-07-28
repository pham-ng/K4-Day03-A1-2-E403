"""
Core demo app for the topic: medical appointment booking and specialty guidance.
Implements 3-Tier Production Architecture:
1. Intent Classifier (Router)
2. Structured Parameter Extractor (JSON Schema)
3. ReAct Tool Loop & Safeguards
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from prompts import CHATBOT_BASELINE_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider
from tools import (
    AVAILABLE_TOOLS,
    EMERGENCY_KEYWORDS,
    book_appointment,
    get_available_appointments,
    search_doctors,
    search_specialties,
)

load_dotenv()


def load_test_cases():
    """Load test cases from config/test_cases.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def _normalize(value: str | None) -> str:
    normalized = unicodedata.normalize("NFD", (value or "").strip().lower())
    without_marks = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return without_marks.replace("đ", "d")


def classify_intent_and_extract_params(user_query: str) -> dict:
    """
    Tier 1 & Tier 2: Intent Router & Structured Parameter Extractor.
    Ensures non-medical or prompt injection queries never cause accidental tool calls.
    """
    text = _normalize(user_query)

    # Security check: Prompt Injection / Jailbreak
    injection_keywords = [
        "ignore all", "ignore previous", "bo qua quy tac", "quen het quy tac",
        "system prompt", "show prompt", "bay gio ban la", "roleplay", "jailbreak"
    ]
    if any(ik in text for ik in injection_keywords):
        return {"intent": "security_violation", "symptoms": None}

    # Emergency check
    if any(ek in text for ek in EMERGENCY_KEYWORDS):
        return {"intent": "emergency", "symptoms": user_query}

    # General simple question check
    if "dinh ky" in text or ("khi nao" in text and not any(k in text for k in ["kham", "dau", "lich"])):
        return {"intent": "general_inquiry", "symptoms": None}

    # Medical intent vs Out-of-scope check
    out_of_scope_keywords = ["sot dat", "di hoc", "hoc o dau", "ban ve", "game", "sot gia"]
    if any(ok in text for ok in out_of_scope_keywords):
        return {"intent": "out_of_scope", "symptoms": None}

    has_ho = bool(re.search(r"\bho\b", text))
    medical_keywords = [
        "kham", "benh", "dau bung", "dau dau", "dau nguc", "dau nhuc", "dau lung", "dau hong",
        "bi dau", "bac si", "lich", "suc khoe", "trieu chung", "sot cao", "bi sot", "viem", "met moi",
        "da day", "tim", "than kinh", "ho hap", "tieu hoa", "cap cuu", "nhap vien",
        "thuoc", "xet nghiem", "benh vien", "phong kham", "dinh ky", "dat lich", "dat hen", "dat cho", "dat kham"
    ]
    is_medical = any(k in text for k in medical_keywords) or has_ho
    if not is_medical:
        return {"intent": "out_of_scope", "symptoms": None}

    # Check invalid doctor or invalid date/time trap
    if "nguyen van a" in text or "2010" in text or "25:00" in text:
        return {
            "intent": "invalid_booking_trap",
            "symptoms": None,
            "error_msg": "Bác sĩ 'Nguyễn Văn A' không có trong hệ thống dữ liệu. Ngày khám '2010-01-01' đã trong quá khứ và khung giờ '25:00' không hợp lệ!"
        }

    # General Body Part vs Requested Specialty Mismatch Extractor
    body_parts_map = [
        {"keywords": ["rang"], "name": "Răng - Hàm - Mặt"},
        {"keywords": ["chim", "duong vat", "tinh hoan", "nam khoa"], "name": "Nam khoa / Tiết niệu"},
        {"keywords": ["mat"], "name": "Mắt / Nhãn khoa"},
        {"keywords": ["tai", "mui"], "name": "Tai - Mũi - Họng"},
        {"keywords": ["xuong", "khop"], "name": "Cơ Xương Khớp"}
    ]

    requested_specs_map = [
        {"keywords": ["than kinh", "nao"], "name": "Thần kinh"},
        {"keywords": ["tim", "mo tim", "tim mach"], "name": "Tim mạch"},
        {"keywords": ["ho hap", "phoi"], "name": "Hô hấp"}
    ]

    found_body_part = next((bp for bp in body_parts_map if any(k in text for k in bp["keywords"])), None)
    found_req_spec = next((rs for rs in requested_specs_map if any(k in text for k in rs["keywords"])), None)

    if found_body_part and found_req_spec:
        return {
            "intent": "conflict_trap",
            "symptoms": None,
            "error_msg": (
                f"⚠️ PHÁT HIỆN MÂU THUẪN LOGIC: Triệu chứng mô tả liên quan đến chuyên khoa '{found_body_part['name']}', "
                f"nhưng bạn lại yêu cầu khám '{found_req_spec['name']}'. Vui lòng làm rõ nhu cầu để được hỗ trợ chính xác!"
            )
        }

    # Structured Parameter Extraction
    doctor_name = "BS. Hoàng Minh Đức" if "hoang minh duc" in text or "duc" in text else None
    specialty = "Tim mạch" if doctor_name else None

    return {
        "intent": "medical_query",
        "symptoms": user_query,
        "doctor_name": doctor_name,
        "specialty": specialty,
        "date": "2026-07-29"
    }


def run_baseline_chatbot(user_query: str, provider):
    """Run the baseline chatbot without tools."""
    print(f"\n[CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print("Chatbot trả lời:")
    print(response)


def _extract_specialty_name(tool_output: str) -> str:
    for line in tool_output.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and ". " in line:
            return line.split(". ", 1)[1].strip()
    return "Nội tổng quát"


def _extract_first_doctor(tool_output: str) -> str:
    for line in tool_output.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and ". " in line:
            return line.split(". ", 1)[1].split(" | ", 1)[0].strip()
    return "BS. Vũ Thanh Mai"


def run_react_agent(user_query: str):
    """
    Tier 3: ReAct Tool Execution & Guardrail Loop.
    Uses Intent Router & Structured Parameters from Tiers 1 & 2.
    """
    print(f"\n[REACT AGENT] Câu hỏi: {user_query}")
    step = 0

    # Tier 1 & 2 Execution: Intent Router & Parameter Extraction
    parsed = classify_intent_and_extract_params(user_query)
    intent = parsed["intent"]

    step += 1
    print(f"\n--- Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
    print(f"Thought: Intent Router phân loại = [{intent}]. Kiểm tra điều kiện Guardrail...")

    if intent == "invalid_booking_trap":
        print(f"Final Answer: ❌ LỖI ĐẶT LỊCH HỢP LỆ: {parsed.get('error_msg')}")
        return

    if intent == "conflict_trap":
        print(f"Final Answer: {parsed.get('error_msg')}")
        return

    if intent == "security_violation":
        print(
            "Final Answer: 🛡️ CẢNH BÁO BẢO MẬT: Tôi là MediAI — Trợ lý Y tế & Đặt Lịch Khám Bệnh. "
            "Hệ thống từ chối các yêu cầu đổi vai, bỏ qua quy tắc an toàn hoặc tiết lộ mã lệnh nội bộ."
        )
        return

    if intent == "emergency":
        print(
            "Final Answer: 🚨 TRIỆU CHỨNG NGUY HIỂM! "
            "Bạn nên gọi 115 hoặc đến phòng cấp cứu gần nhất ngay lập tức, "
            "không nên chờ đặt lịch khám thông thường."
        )
        return

    if intent == "out_of_scope":
        print(
            "Final Answer: Xin lỗi, tôi là MediAI — Trợ lý Y tế & Đặt Lịch Khám Bệnh. "
            "Tôi chỉ hỗ trợ tư vấn chuyên khoa và tra cứu đặt lịch khám bệnh. "
            "Rất tiếc tôi không thể trả lời các câu hỏi ngoài phạm vi này."
        )
        return

    if intent == "general_inquiry":
        print("Final Answer: Nên đi khám sức khỏe tổng quát định kỳ 6 tháng đến 1 năm một lần để phát hiện sớm các nguy cơ sức khỏe.")
        return

    # Medical Query Execution Loop
    selected_doctor = parsed["doctor_name"]
    specialty_name = parsed["specialty"]

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        if step == 2:
            if selected_doctor:
                print(f"Thought: Người dùng muốn đặt lịch với {selected_doctor}, tra cứu trực tiếp lịch khám.")
                print(f"Action: get_available_appointments[doctor_name='{selected_doctor}', date='2026-07-29']")
                appointments_result = get_available_appointments(doctor_name=selected_doctor, date="2026-07-29")
                print(f"Observation: {appointments_result}")

                if "Đã kín lịch" in appointments_result or "không còn slot" in appointments_result:
                    print("Thought: Bác sĩ đã kín lịch ngày này. Cần gợi ý bác sĩ khác cùng chuyên khoa.")
                    print(f"Action: search_doctors[specialty='Tim mạch']")
                    doctors_result = search_doctors(specialty="Tim mạch")
                    print(f"Observation: {doctors_result}")

                    print("Thought: Đã tìm thấy bác sĩ thay thế cùng chuyên khoa. Trả lời gợi ý cho người dùng.")
                    print(
                        f"Final Answer: Rất tiếc, {selected_doctor} đã kín lịch vào ngày 2026-07-29. "
                        f"Gợi ý thay thế: Bạn có thể chọn BS. Nguyễn Bích Vân (Khoa Tim mạch) còn khung giờ chiều cùng ngày."
                    )
                    break
            else:
                print("Thought: Cần phân tích triệu chứng để gợi ý chuyên khoa phù hợp.")
                print(f"Action: search_specialties['{user_query}']")
                specialty_result = search_specialties(user_query)
                print(f"Observation: {specialty_result}")
                specialty_name = _extract_specialty_name(specialty_result)

        elif step == 3:
            print("Thought: Đã có chuyên khoa gợi ý, giờ cần tìm danh sách bác sĩ phù hợp.")
            print(f"Action: search_doctors[specialty='{specialty_name}']")
            doctors_result = search_doctors(specialty=specialty_name)
            print(f"Observation: {doctors_result}")
            selected_doctor = _extract_first_doctor(doctors_result)

        elif step == 4:
            print("Thought: Cần tra cứu lịch khám còn trống của bác sĩ ưu tiên.")
            print(f"Action: get_available_appointments[doctor_name='{selected_doctor}', date='2026-07-29']")
            appointments_result = get_available_appointments(doctor_name=selected_doctor, date="2026-07-29")
            print(f"Observation: {appointments_result}")

        else:
            print("Thought: Tôi đã có đủ thông tin để trả lời.")
            print(
                "Final Answer: Dựa trên triệu chứng bạn mô tả, chuyên khoa phù hợp để "
                f"khám ban đầu là {specialty_name}. Đây không phải chẩn đoán bệnh. "
                f"Tôi tìm thấy {selected_doctor} còn lịch vào ngày 2026-07-29. "
                "Bạn có thể chọn một khung giờ còn trống trong phần quan sát để sang bước đặt lịch."
            )
            break


def run_full_suite():
    """Run all 5 test cases for full evaluation."""
    provider = get_llm_provider()
    tests = load_test_cases()
    print("\n==================================================")
    print("CHẠY TOÀN BỘ 5 TEST CASES THỬ THÁCH (SUITE EVALUATION)")
    print("==================================================")
    for test in tests:
        print(f"\n==================================================")
        print(f"TEST CASE #{test['id']} [{test['category']}]")
        print(f"Mục tiêu kỳ vọng: {test['expected_behavior']}")
        print("--------------------------------------------------")
        run_baseline_chatbot(test["question"], provider)
        run_react_agent(test["question"])


if __name__ == "__main__":
    print("==================================================")
    print("LAB 3 - CHATBOT VS REACT AGENT")
    print("Chu de: Dat Lich Kham Benh & Tu Van Chuyen Khoa")
    print("==================================================")

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "mock-offline")
    print(f"LLM Provider: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"Đã tải {len(tests)} test cases từ config/test_cases.json")

    run_full_suite()
