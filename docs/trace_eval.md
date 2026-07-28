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

--- DEMO 1: BASELINE CHATBOT (5 TEST CASES) ---

[Test 1/5] Category: Đơn giản

[CHATBOT BASELINE] Câu hỏi: Khi nào thì nên đi khám sức khỏe tổng quát định kỳ?
Chatbot trả lời:
Mock response: toi chi dang mo phong baseline chatbot offline.

[Test 2/5] Category: Làm rõ thông tin

[CHATBOT BASELINE] Câu hỏi: Tôi hay mệt mỏi và đau đầu, không biết nên khám khoa nào.
Chatbot trả lời:
Mock response: toi chi dang mo phong baseline chatbot offline.

[Test 3/5] Category: Multi-step cần tool

[CHATBOT BASELINE] Câu hỏi: Tôi bị đau bụng âm ỉ mấy ngày nay, muốn khám vào chiều ngày mai 2026-07-29. Tôi nên khám khoa nào và còn lịch bác sĩ nào?
Chatbot trả lời:
Ban co the can kham chuyen khoa Tieu hoa dua tren mo ta hien tai. Toi chua the tu kiem tra lich bac si neu khong dung cong cu.

[Test 4/5] Category: Lịch đầy kín

[CHATBOT BASELINE] Câu hỏi: Tôi muốn đặt lịch khám tim mạch với BS. Hoàng Minh Đức vào ngày 2026-07-29.
Chatbot trả lời:
Mock response: toi chi dang mo phong baseline chatbot offline.

[Test 5/5] Category: Khẩn cấp

[CHATBOT BASELINE] Câu hỏi: Tôi đang khó thở và đau ngực dữ dội, hãy đặt lịch sớm nhất cho tôi.
Chatbot trả lời:
Trieu chung co dau hieu nguy hiem. Ban nen den cap cuu ngay thay vi cho lich kham thong thuong.

--- DEMO 2: REACT AGENT ---

[REACT AGENT] Câu hỏi: Tôi bị đau bụng âm ỉ mấy ngày nay, muốn khám vào chiều ngày mai 2026-07-29. Tôi nên khám khoa nào và còn lịch bác sĩ nào?

--- Vòng lặp ReAct (Step 1/4) ---
Thought: Cần đọc triệu chứng để gợi ý chuyên khoa phù hợp trước.
Action: search_specialties['Tôi bị đau bụng âm ỉ mấy ngày nay, muốn khám vào chiều ngày mai 2026-07-29. Tôi nên khám khoa nào và còn lịch bác sĩ nào?']
Observation: Các chuyên khoa gợi ý:
1. Tiêu hóa
2. Nội tổng quát
Lưu ý: Đây chỉ là gợi ý chuyên khoa dựa trên triệu chứng, không phải chẩn đoán bệnh.

--- Vòng lặp ReAct (Step 2/4) ---
Thought: Đã có chuyên khoa gợi ý, giờ cần tìm bác sĩ phù hợp.
Action: search_doctors[specialty='Tiêu hóa']
Observation: Danh sách bác sĩ phù hợp:
1. BS. Nguyễn Minh An | Chuyên khoa: Tiêu hóa | Cơ sở: Phòng khám Tiêu hóa Cơ sở 1
2. BS. Trần Hải Yến | Chuyên khoa: Tiêu hóa | Cơ sở: Khoa Nội soi tiêu hóa Cơ sở 2

--- Vòng lặp ReAct (Step 3/4) ---
Thought: Cần tra cứu lịch khám còn trống của bác sĩ ưu tiên.
Action: get_available_appointments[doctor_name='BS. Nguyễn Minh An', date='2026-07-29']
Observation: Lịch trống ngày 2026-07-29:
- BS. Nguyễn Minh An | Cơ sở: Phòng khám Tiêu hóa Cơ sở 1 | Giờ trống: 14:00, 15:30, 16:00

--- Vòng lặp ReAct (Step 4/4) ---
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: Dựa trên triệu chứng bạn mô tả, chuyên khoa phù hợp để khám ban đầu là Tiêu hóa. Đây không phải chẩn đoán bệnh. Tôi tìm thấy BS. Nguyễn Minh An còn lịch vào ngày 2026-07-29. Bạn có thể chọn một khung giờ còn trống trong phần quan sát để sang bước đặt lịch.