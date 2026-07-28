"""
Standardized tool registry for medical appointment booking and specialty guidance.

The tools only support:
- suggesting suitable specialties from symptoms
- looking up doctors and appointment slots
- booking appointments

They do not diagnose diseases or provide treatment advice.
"""

from __future__ import annotations

import unicodedata


EMERGENCY_KEYWORDS = [
    "kho tho",
    "dau nguc",
    "ngat",
    "chay mau nhieu",
    "co giat",
]


DOCTORS = [
    {
        "name": "BS. Nguyễn Minh An",
        "specialty": "Tiêu hóa",
        "facility": "Phòng khám Tiêu hóa Cơ sở 1",
        "slots": ["2026-07-29 14:00", "2026-07-29 15:30", "2026-07-29 16:00"],
    },
    {
        "name": "BS. Trần Hải Yến",
        "specialty": "Tiêu hóa",
        "facility": "Khoa Nội soi tiêu hóa Cơ sở 2",
        "slots": ["2026-07-29 13:30", "2026-07-29 17:00"],
    },
    {
        "name": "BS. Lê Quốc Bảo",
        "specialty": "Thần kinh",
        "facility": "Khoa Thần kinh Cơ sở 1",
        "slots": ["2026-07-29 09:00", "2026-07-29 10:30"],
    },
    {
        "name": "BS. Đỗ Thanh Tùng",
        "specialty": "Hô hấp",
        "facility": "Khoa Hô hấp Cơ sở 1",
        "slots": ["2026-07-29 08:30", "2026-07-29 11:00"],
    },
    {
        "name": "BS. Hoàng Minh Đức",
        "specialty": "Tim mạch",
        "facility": "Khoa Tim mạch Cơ sở 1",
        "slots": [],
    },
    {
        "name": "BS. Nguyễn Bích Vân",
        "specialty": "Tim mạch",
        "facility": "Phòng khám Tim mạch Cơ sở 2",
        "slots": ["2026-07-29 15:00", "2026-07-29 16:30"],
    },
    {
        "name": "BS. Vũ Thanh Mai",
        "specialty": "Nội tổng quát",
        "facility": "Phòng khám tổng quát Cơ sở 1",
        "slots": ["2026-07-29 08:30", "2026-07-29 11:00"],
    },
]


def _normalize(value: str | None) -> str:
    normalized = unicodedata.normalize("NFD", (value or "").strip().lower())
    without_marks = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return without_marks.replace("đ", "d")


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
        if specialty_value and specialty_value not in _normalize(doctor["specialty"]):
            continue
        if facility_value and facility_value not in _normalize(doctor["facility"]):
            continue
        if doctor_value and doctor_value not in _normalize(doctor["name"]):
            continue
        results.append(doctor)
    return results


def search_specialties(symptoms: str) -> str:
    """
    Suggest suitable specialties from symptoms only.

    Purpose:
        Use symptom text to propose one or more relevant specialties for
        initial consultation. This tool only maps symptoms to specialties and
        does not diagnose a disease.

    Args:
        symptoms: Free-text symptom description from the user.

    Returns:
        A human-readable string listing suggested specialties, or a warning
        string for emergency symptoms.

    Error semantics:
        Returns a string starting with "LỖI:" when the symptom description is
        missing. Returns a string starting with "KHẨN CẤP:" when the symptom
        description suggests an emergency case.
    """
    text = _normalize(symptoms)
    if not text:
        return "LỖI: Thiếu mô tả triệu chứng để gợi ý chuyên khoa."

    if any(keyword in text for keyword in EMERGENCY_KEYWORDS):
        return (
            "KHẨN CẤP: Triệu chứng có dấu hiệu nguy hiểm. "
            "Cần hướng dẫn người dùng đến cấp cứu ngay thay vì đặt lịch thông thường."
        )

    if any(keyword in text for keyword in ["dau bung", "tieu chay", "o nong", "day hoi", "da day"]):
        return (
            "Các chuyên khoa gợi ý:\n"
            "1. Tiêu hóa\n"
            "2. Nội tổng quát\n"
            "Lưu ý: Đây chỉ là gợi ý chuyên khoa dựa trên triệu chứng, không phải chẩn đoán bệnh."
        )
    if any(keyword in text for keyword in ["dau dau", "mat ngu", "chong mat"]):
        return (
            "Các chuyên khoa gợi ý:\n"
            "1. Thần kinh\n"
            "2. Nội tổng quát\n"
            "Lưu ý: Đây chỉ là gợi ý chuyên khoa dựa trên triệu chứng, không phải chẩn đoán bệnh."
        )
    if any(keyword in text for keyword in ["sot", "viem hong", "kho tho"]):
        return (
            "Các chuyên khoa gợi ý:\n"
            "1. Hô hấp\n"
            "2. Nội tổng quát\n"
            "Lưu ý: Đây chỉ là gợi ý chuyên khoa dựa trên triệu chứng, không phải chẩn đoán bệnh."
        )
    if any(keyword in text for keyword in ["dau nguc", "tim dap nhanh", "cao huyet ap"]):
        return (
            "Các chuyên khoa gợi ý:\n"
            "1. Tim mạch\n"
            "2. Nội tổng quát\n"
            "Lưu ý: Đây chỉ là gợi ý chuyên khoa dựa trên triệu chứng, không phải chẩn đoán bệnh."
        )

    return (
        "Các chuyên khoa gợi ý:\n"
        "1. Nội tổng quát\n"
        "Lưu ý: Triệu chứng còn mơ hồ. Cần hỏi thêm trước khi chốt hướng đặt lịch."
    )


def search_doctors(
    specialty: str | None = None,
    facility: str | None = None,
    doctor_name: str | None = None,
) -> str:
    """
    Search doctors by specialty, facility, or doctor name.

    Purpose:
        Filter the mocked doctor directory using one or more lookup fields so
        the agent can present candidates for booking.

    Args:
        specialty: Optional specialty filter such as "Tiêu hóa".
        facility: Optional facility filter such as a clinic or hospital branch.
        doctor_name: Optional partial or full doctor name.

    Returns:
        A formatted multi-line string containing matching doctors and their
        associated specialty and facility.

    Error semantics:
        Returns a string starting with "LỖI:" when no filter is provided or
        when no doctors match the requested criteria.
    """
    if not any([specialty, facility, doctor_name]):
        return "LỖI: Cần ít nhất một tiêu chí tìm kiếm: specialty, facility hoặc doctor_name."

    matches = _find_doctors(specialty=specialty, facility=facility, doctor_name=doctor_name)
    if not matches:
        return "LỖI: Không tìm thấy bác sĩ phù hợp với bộ lọc đã yêu cầu."

    lines = ["Danh sách bác sĩ phù hợp:"]
    for index, doctor in enumerate(matches, start=1):
        lines.append(
            f"{index}. {doctor['name']} | Chuyên khoa: {doctor['specialty']} | Cơ sở: {doctor['facility']}"
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

    Purpose:
        Retrieve mocked appointment availability for one or more doctors on a
        specific date so the agent can recommend valid booking options.

    Args:
        doctor_name: Optional doctor name filter.
        specialty: Optional specialty filter.
        facility: Optional facility filter.
        date: Required appointment date in YYYY-MM-DD format.

    Returns:
        A formatted multi-line string describing available time slots or
        indicating that matching doctors are fully booked on that date.

    Error semantics:
        Returns a string starting with "LỖI:" when the date is missing or when
        no doctors match the provided filters.
    """
    if not date:
        return "LỖI: Thiếu ngày khám để tra cứu lịch trống."

    matches = _find_doctors(specialty=specialty, facility=facility, doctor_name=doctor_name)
    if not matches:
        return "LỖI: Không tìm thấy bác sĩ nào để tra cứu lịch khám."

    lines = [f"Lịch trống ngày {date}:"]
    found_any = False
    for doctor in matches:
        slots = [slot.split(" ", 1)[1] for slot in doctor["slots"] if slot.startswith(date)]
        if slots:
            found_any = True
            lines.append(
                f"- {doctor['name']} | Cơ sở: {doctor['facility']} | Giờ trống: {', '.join(slots)}"
            )
        else:
            lines.append(f"- {doctor['name']} | Cơ sở: {doctor['facility']} | Đã kín lịch")

    if not found_any:
        return f"Lịch trống ngày {date}: không còn slot phù hợp với bộ lọc hiện tại."
    return "\n".join(lines)


def book_appointment(doctor_name: str, date: str, time_slot: str, patient_info: str) -> str:
    """
    Create a mocked booking confirmation.

    Purpose:
        Simulate the final booking step after the user has already selected a
        doctor and a valid appointment slot.

    Args:
        doctor_name: Selected doctor name.
        date: Appointment date in YYYY-MM-DD format.
        time_slot: Selected appointment time such as "14:00".
        patient_info: Patient identification text, for example name or contact.

    Returns:
        A confirmation string containing a mocked appointment identifier and
        the submitted booking details.

    Error semantics:
        Returns a string starting with "LỖI:" when any required booking field
        is missing.
    """
    doctor = doctor_name.strip()
    when = date.strip()
    slot = time_slot.strip()
    patient = patient_info.strip()
    if not all([doctor, when, slot, patient]):
        return "LỖI: Thiếu thông tin để đặt lịch. Cần bác sĩ, ngày, giờ và thông tin bệnh nhân."

    appointment_id = (
        f"APT-{doctor.replace(' ', '').replace('.', '')[:8].upper()}"
        f"-{when.replace('-', '')}-{slot.replace(':', '')}"
    )
    return (
        f"ĐẶT LỊCH THÀNH CÔNG: appointment_id={appointment_id}; "
        f"bệnh nhân={patient}; bác sĩ={doctor}; ngày={when}; giờ={slot}."
    )


AVAILABLE_TOOLS = {
    "search_specialties": search_specialties,
    "search_doctors": search_doctors,
    "get_available_appointments": get_available_appointments,
    "book_appointment": book_appointment,
}
