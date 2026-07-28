# BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ

Dành cho Role 5: Observability & Reviewer.

---

## 1. Bảng chấm điểm Agentic Fit (Scoring Matrix)

Chủ đề nhóm chọn: **Đặt Lịch Khám Bệnh & Tư Vấn Chuyên Khoa**

| Tiêu chí | Điểm (1–5) | Lý do đánh giá |
| :--- | :---: | :--- |
| Multi-step Reasoning | `5/5` | Agent phải đi qua chuỗi bước: đọc triệu chứng, chỉ gợi ý chuyên khoa phù hợp, tìm bác sĩ, tra cứu lịch trống và có thể chốt lịch hẹn. |
| Tool Interaction | `5/5` | Bài toán cần các tool để tra cứu chuyên khoa, tìm bác sĩ, tìm lịch trống và tạo booking. Chatbot thường không tự truy cập được các dữ liệu này. |
| Dynamic Decision | `4/5` | Hướng xử lý thay đổi theo mức độ triệu chứng, tính đầy đủ của thông tin và tình trạng còn lịch hay hết lịch. |
| Long Horizon | `4/5` | Quy trình thường dài hơn một lần hỏi đáp, nhiều lúc cần 3–5 bước và có nhánh xử lý thay thế nếu tool thất bại. |
| **Tổng điểm fit** | **18/20** | **Kết luận: Bài toán rất phù hợp để dùng ReAct Agent thay vì chỉ dùng chatbot.** |

---

## 2. So sánh phản hồi cho Test Case #3

**Câu hỏi:** “Tôi bị đau bụng âm ỉ mấy ngày nay, muốn khám vào chiều ngày mai 2026-07-29. Tôi nên khám khoa nào và còn lịch bác sĩ nào?”

### Chatbot Baseline

- Phản hồi kỳ vọng: “Dựa trên mô tả, bạn có thể cần khám chuyên khoa Tiêu hóa. Tuy nhiên, tôi không thể xác nhận bác sĩ nào còn lịch nếu không có dữ liệu thời gian thực.”
- Nhận xét: Chatbot có thể đưa ra gợi ý thông tin chung nhưng không giải quyết trọn vẹn yêu cầu đặt lịch.

### ReAct Agent

- Thought 1: Cần đọc triệu chứng để gợi ý chuyên khoa phù hợp.
- Action 1: `search_specialties['Tôi bị đau bụng âm ỉ mấy ngày nay...']`
- Observation 1: `1. Tiêu hóa`
- Thought 2: Đã có chuyên khoa, cần tìm bác sĩ phù hợp.
- Action 2: `search_doctors[specialty='Tiêu hóa']`
- Observation 2: `BS. Nguyễn Minh An`, `BS. Trần Hải Yến`
- Thought 3: Cần tra cứu lịch khám còn trống của bác sĩ ưu tiên.
- Action 3: `get_available_appointments[doctor_name='BS. Nguyễn Minh An', date='2026-07-29']`
- Observation 3: `Còn các khung giờ 14:00, 15:30, 16:00`
- Final Answer: “Dựa trên triệu chứng, chuyên khoa phù hợp để khám ban đầu là Tiêu hóa. Đây không phải chẩn đoán bệnh. Hiện BS. Nguyễn Minh An còn lịch vào ngày 2026-07-29.”
- Nhận xét: Agent kết hợp suy luận và công cụ nên đáp ứng được cả phần gợi ý chuyên khoa và phần tra cứu lịch.

---

## 3. Tool inventory cho MOC 1

Đề xuất tool trong `src/tools.py`:

- `search_specialties(symptoms)`
- `search_doctors(specialty=None, facility=None, doctor_name=None)`
- `get_available_appointments(doctor_name=None, specialty=None, facility=None, date=None)`
- `book_appointment(doctor_name, date, time_slot, patient_info)`

Lý do:

- Tool 1 biến mô tả triệu chứng thành danh sách chuyên khoa gợi ý.
- Tool 2 tìm bác sĩ theo nhiều bộ lọc, phù hợp với bài toán thực tế hơn.
- Tool 3 tra cứu slot khám còn trống theo ngày và bộ lọc.
- Tool 4 mô phỏng bước tạo booking để khớp luồng đặt lịch.

---

