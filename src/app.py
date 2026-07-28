"""
Core demo app for the topic: medical appointment booking and specialty guidance.
"""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from prompts import CHATBOT_BASELINE_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider
from tools import get_available_appointments, search_doctors, search_specialties

load_dotenv()


def load_test_cases():
    """Load test cases from config/test_cases.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


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
    return "Noi tong quat"


def _extract_first_doctor(tool_output: str) -> str:
    for line in tool_output.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and ". " in line:
            return line.split(". ", 1)[1].split(" | ", 1)[0].strip()
    return "BS. Vu Thanh Mai"


def run_react_agent(user_query: str):
    """Run a deterministic ReAct-style demo using the standardized tools."""
    print(f"\n[REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    completed = False

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        if step == 1:
            print("Thought: Cần đọc triệu chứng để gợi ý chuyên khoa phù hợp trước.")
            print(f"Action: search_specialties['{user_query}']")
            specialty_result = search_specialties(user_query)
            print(f"Observation: {specialty_result}")

            if specialty_result.startswith(("KHAN CAP", "KHẨN CẤP")):
                print("Thought: Tôi đã có đủ thông tin để trả lời.")
                print(
                    "Final Answer: Triệu chứng có dấu hiệu khẩn cấp. "
                    "Bạn nên đến khoa cấp cứu gần nhất hoặc gọi hỗ trợ y tế ngay, "
                    "không nên chờ lịch khám thông thường."
                )
                completed = True
                break

            specialty_name = _extract_specialty_name(specialty_result)

        elif step == 2:
            print("Thought: Đã có chuyên khoa gợi ý, giờ cần tìm bác sĩ phù hợp.")
            print(f"Action: search_doctors[specialty='{specialty_name}']")
            doctors_result = search_doctors(specialty=specialty_name)
            print(f"Observation: {doctors_result}")
            selected_doctor = _extract_first_doctor(doctors_result)

        elif step == 3:
            print("Thought: Cần tra cứu lịch khám còn trống của bác sĩ ưu tiên.")
            print(
                "Action: get_available_appointments"
                f"[doctor_name='{selected_doctor}', date='2026-07-29']"
            )
            appointments_result = get_available_appointments(
                doctor_name=selected_doctor,
                date="2026-07-29",
            )
            print(f"Observation: {appointments_result}")

        else:
            print("Thought: Tôi đã có đủ thông tin để trả lời.")
            print(
                "Final Answer: Dựa trên triệu chứng bạn mô tả, chuyên khoa phù hợp để "
                f"khám ban đầu là {specialty_name}. Đây không phải chẩn đoán bệnh. "
                f"Tôi tìm thấy {selected_doctor} còn lịch vào ngày 2026-07-29. "
                "Bạn có thể chọn một khung giờ còn trống trong phần quan sát để sang bước đặt lịch."
            )
            completed = True
            break

    if not completed and step >= MAX_ITERATIONS:
        print(
            f"GUARDRAIL: Đã chạm giới hạn {MAX_ITERATIONS} vòng lặp. "
            "Dừng để tránh lặp vô hạn."
        )


if __name__ == "__main__":
    print("==================================================")
    print("LAB 3 - CHATBOT VS REACT AGENT")
    print("Chu de: Dat Lich Kham Benh & Tu Van Chuyen Khoa")
    print("==================================================")

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "mock-offline")
    print(f"LLM Provider: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"Da tai {len(tests)} test cases tu config/test_cases.json")

    sample_query = tests[3]["question"]

    print("\n--- DEMO 1: BASELINE CHATBOT ---")
    run_baseline_chatbot(sample_query, provider)

    print("\n--- DEMO 2: REACT AGENT ---")
    run_react_agent(sample_query)
