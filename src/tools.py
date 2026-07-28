"""
Standardized tool registry for medical appointment booking and specialty guidance.

The tools only support:
- suggesting suitable specialties from symptoms
- looking up doctors and appointment slots
- booking appointments

They do not diagnose diseases or provide treatment advice.
"""

from __future__ import annotations


EMERGENCY_KEYWORDS = [
    "kho tho",
    "khó thở",
    "dau nguc",
    "đau ngực",
    "ngat",
    "ngất",
    "chay mau nhieu",
    "chảy máu nhiều",
    "co giat",
    "co giật",
]


DOCTORS = [
    {
        "name": "BS. Nguyen Minh An",
        "specialty": "Tieu hoa",
        "facility": "Phong kham Tieu hoa Co so 1",
        "slots": ["2026-07-29 14:00", "2026-07-29 15:30", "2026-07-29 16:00"],
    },
    {
        "name": "BS. Tran Hai Yen",
        "specialty": "Tieu hoa",
        "facility": "Khoa Noi soi tieu hoa Co so 2",
        "slots": ["2026-07-29 13:30", "2026-07-29 17:00"],
    },
    {
        "name": "BS. Le Quoc Bao",
        "specialty": "Than kinh",
        "facility": "Khoa Than kinh Co so 1",
        "slots": ["2026-07-29 09:00", "2026-07-29 10:30"],
    },
    {
        "name": "BS. Do Thanh Tung",
        "specialty": "Ho hap",
        "facility": "Khoa Ho hap Co so 1",
        "slots": ["2026-07-29 08:30", "2026-07-29 11:00"],
    },
    {
        "name": "BS. Hoang Minh Duc",
        "specialty": "Tim mach",
        "facility": "Khoa Tim mach Co so 1",
        "slots": [],
    },
    {
        "name": "BS. Nguyen Bich Van",
        "specialty": "Tim mach",
        "facility": "Phong kham Tim mach Co so 2",
        "slots": ["2026-07-29 15:00", "2026-07-29 16:30"],
    },
    {
        "name": "BS. Vu Thanh Mai",
        "specialty": "Noi tong quat",
        "facility": "Phong kham tong quat Co so 1",
        "slots": ["2026-07-29 08:30", "2026-07-29 11:00"],
    },
]


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _find_doctors(
    specialty: str | None = None,
    facility: str | None = None,
    doctor_name: str | None = None,
) -> list[dict]:
    specialty_value = _normalize(specialty)
    facility_value = _normalize(facility)
    doctor_value = _normalize(doctor_name)

    results = []
    for doctor in DOCTORS:
        if specialty_value and specialty_value not in doctor["specialty"].lower():
            continue
        if facility_value and facility_value not in doctor["facility"].lower():
            continue
        if doctor_value and doctor_value not in doctor["name"].lower():
            continue
        results.append(doctor)
    return results


def search_specialties(symptoms: str) -> str:
    """
    Suggest suitable specialties from symptoms only.
    This is not a disease diagnosis.
    """
    text = _normalize(symptoms)
    if not text:
        return "LOI: Thieu mo ta trieu chung de goi y chuyen khoa."

    if any(keyword in text for keyword in EMERGENCY_KEYWORDS):
        return (
            "KHAN CAP: Trieu chung co dau hieu nguy hiem. "
            "Can huong dan nguoi dung den cap cuu ngay thay vi dat lich thong thuong."
        )

    if any(keyword in text for keyword in ["dau bung", "tieu chay", "o nong", "day hoi", "da day", "dạ dày"]):
        return (
            "Cac chuyen khoa goi y:\n"
            "1. Tieu hoa\n"
            "2. Noi tong quat\n"
            "Luu y: Day chi la goi y chuyen khoa dua tren trieu chung, khong phai chan doan benh."
        )
    if any(keyword in text for keyword in ["dau dau", "mat ngu", "chong mat", "đau đầu", "mất ngủ", "chóng mặt"]):
        return (
            "Cac chuyen khoa goi y:\n"
            "1. Than kinh\n"
            "2. Noi tong quat\n"
            "Luu y: Day chi la goi y chuyen khoa dua tren trieu chung, khong phai chan doan benh."
        )
    if any(keyword in text for keyword in ["sot", "viem hong", "kho tho", "sốt", "viêm họng", "khó thở"]):
        return (
            "Cac chuyen khoa goi y:\n"
            "1. Ho hap\n"
            "2. Noi tong quat\n"
            "Luu y: Day chi la goi y chuyen khoa dua tren trieu chung, khong phai chan doan benh."
        )
    if any(keyword in text for keyword in ["dau nguc", "tim dap nhanh", "cao huyet ap", "đau ngực", "tim đập nhanh", "cao huyết áp"]):
        return (
            "Cac chuyen khoa goi y:\n"
            "1. Tim mach\n"
            "2. Noi tong quat\n"
            "Luu y: Day chi la goi y chuyen khoa dua tren trieu chung, khong phai chan doan benh."
        )

    return (
        "Cac chuyen khoa goi y:\n"
        "1. Noi tong quat\n"
        "Luu y: Trieu chung con mo ho. Can hoi them truoc khi chot huong dat lich."
    )


def search_doctors(
    specialty: str | None = None,
    facility: str | None = None,
    doctor_name: str | None = None,
) -> str:
    """
    Search doctors by specialty, facility, or doctor name.
    """
    if not any([specialty, facility, doctor_name]):
        return "LOI: Can it nhat mot tieu chi tim kiem: specialty, facility hoac doctor_name."

    matches = _find_doctors(specialty=specialty, facility=facility, doctor_name=doctor_name)
    if not matches:
        return "LOI: Khong tim thay bac si phu hop voi bo loc da yeu cau."

    lines = ["Danh sach bac si phu hop:"]
    for index, doctor in enumerate(matches, start=1):
        lines.append(
            f"{index}. {doctor['name']} | Chuyen khoa: {doctor['specialty']} | Co so: {doctor['facility']}"
        )
    return "\n".join(lines)


def get_available_appointments(
    doctor_name: str | None = None,
    specialty: str | None = None,
    facility: str | None = None,
    date: str | None = None,
) -> str:
    """
    Look up available appointment slots using doctor/specialty/facility filters.
    """
    if not date:
        return "LOI: Thieu ngay kham de tra cuu lich trong."

    matches = _find_doctors(specialty=specialty, facility=facility, doctor_name=doctor_name)
    if not matches:
        return "LOI: Khong tim thay bac si nao de tra cuu lich kham."

    lines = [f"Lich trong ngay {date}:"]
    found_any = False
    for doctor in matches:
        slots = [slot.split(" ", 1)[1] for slot in doctor["slots"] if slot.startswith(date)]
        if slots:
            found_any = True
            lines.append(f"- {doctor['name']} | Co so: {doctor['facility']} | Gio trong: {', '.join(slots)}")
        else:
            lines.append(f"- {doctor['name']} | Co so: {doctor['facility']} | Da kin lich")

    if not found_any:
        return f"Lich trong ngay {date}: khong con slot phu hop voi bo loc hien tai."
    return "\n".join(lines)


def book_appointment(doctor_name: str, date: str, time_slot: str, patient_info: str) -> str:
    """
    Create a mocked booking confirmation.
    """
    doctor = doctor_name.strip()
    when = date.strip()
    slot = time_slot.strip()
    patient = patient_info.strip()
    if not all([doctor, when, slot, patient]):
        return "LOI: Thieu thong tin de dat lich. Can bac si, ngay, gio va thong tin benh nhan."

    appointment_id = f"APT-{doctor.replace(' ', '').replace('.', '')[:8].upper()}-{when.replace('-', '')}-{slot.replace(':', '')}"
    return (
        f"DAT LICH THANH CONG: appointment_id={appointment_id}; "
        f"benh nhan={patient}; bac_si={doctor}; ngay={when}; gio={slot}."
    )


AVAILABLE_TOOLS = {
    "search_specialties": search_specialties,
    "search_doctors": search_doctors,
    "get_available_appointments": get_available_appointments,
    "book_appointment": book_appointment,
}
