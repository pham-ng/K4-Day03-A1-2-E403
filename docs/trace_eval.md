# BAO CAO GIAM SAT & DANH GIA

Danh cho Role 5: Observability & Reviewer.

---

## 1. Bang cham diem Agentic Fit (Scoring Matrix)

Chu de nhom chon: **Dat Lich Kham Benh & Tu Van Chuyen Khoa**

| Tieu chi | Diem (1-5) | Ly do danh gia |
| :--- | :---: | :--- |
| Multi-step Reasoning | `5/5` | Agent phai di qua chuoi buoc: doc trieu chung, chi goi y chuyen khoa phu hop, tim bac si, tra cuu lich trong, va co the chot lich hen. |
| Tool Interaction | `5/5` | Bai toan can cac tool de tra cuu chuyen khoa, tim bac si, tim lich trong va tao booking. Chatbot thuong khong tu truy cap duoc cac du lieu nay. |
| Dynamic Decision | `4/5` | Huong xu ly thay doi theo muc do trieu chung, tinh day du cua thong tin, va tinh trang con lich hay het lich. |
| Long Horizon | `4/5` | Quy trinh thuong dai hon 1 lan hoi dap, nhieu luc can 3-5 buoc va co nhanh xu ly thay the neu tool that bai. |
| **Tong diem fit** | **18/20** | **Ket luan: Bai toan rat phu hop de dung ReAct Agent thay vi chi dung chatbot.** |

---

## 2. So sanh phan hoi cho Test Case #3

**Cau hoi:** "Toi bi dau bung am i may ngay nay, muon kham vao chieu ngay mai 2026-07-29. Toi nen kham khoa nao va con lich bac si nao?"

### Chatbot Baseline

- Phan hoi ky vong: "Dua tren mo ta, ban co the can kham chuyen khoa Tieu hoa. Tuy nhien toi khong the xac nhan bac si nao con lich neu khong co du lieu thoi gian thuc."
- Nhan xet: Chatbot co the dua ra goi y thong tin chung, nhung khong giai quyet tron ven yeu cau dat lich.

### ReAct Agent

- Thought 1: Can doc trieu chung de goi y chuyen khoa phu hop.
- Action 1: `search_specialties['Toi bi dau bung am i may ngay nay...']`
- Observation 1: `1. Tieu hoa`
- Thought 2: Da co chuyen khoa, can tim bac si phu hop.
- Action 2: `search_doctors[specialty='Tieu hoa']`
- Observation 2: `BS. Nguyen Minh An`, `BS. Tran Hai Yen`
- Thought 3: Can tra cuu lich kham con trong cua bac si uu tien.
- Action 3: `get_available_appointments[doctor_name='BS. Nguyen Minh An', date='2026-07-29']`
- Observation 3: `Con cac khung gio 14:00, 15:30, 16:00`
- Final Answer: "Dua tren trieu chung, chuyen khoa phu hop de kham ban dau la Tieu hoa. Day khong phai chan doan benh. Hien BS. Nguyen Minh An con lich vao ngay 2026-07-29."
- Nhan xet: Agent ket hop suy luan va cong cu nen dap ung duoc ca phan goi y chuyen khoa va phan tra cuu lich.

---

## 3. Tool inventory cho MOC 1

De xuat tool trong `src/tools.py`:

- `search_specialties(symptoms)`
- `search_doctors(specialty=None, facility=None, doctor_name=None)`
- `get_available_appointments(doctor_name=None, specialty=None, facility=None, date=None)`
- `book_appointment(doctor_name, date, time_slot, patient_info)`

Ly do:

- Tool 1 bien mo ta trieu chung thanh danh sach chuyen khoa goi y.
- Tool 2 tim bac si theo nhieu bo loc dung voi bai toan thuc te hon.
- Tool 3 tra cuu slot kham con trong theo ngay va bo loc.
- Tool 4 mo phong buoc tao booking de khop luong dat lich.

---

## 4. Failure modes can theo doi

- Nguoi dung mo ta trieu chung qua mo ho nen khong du de goi y chuyen khoa ro rang.
- Agent dua ra chan doan benh cu the thay vi chi goi y chuyen khoa.
- Co dau hieu khan cap nhu kho tho, dau nguc, ngat; agent phai dung luong dat lich thong thuong.
- Khong tim thay bac si theo bo loc chuyen khoa, co so hoac ten.
- Khong con lich trong phu hop trong ngay nguoi dung muon.
- Thieu thong tin dat lich nhu ho ten, ngay, gio, so dien thoai.
- Nguoi dung doi agent chan doan benh xac dinh hoac de xuat dieu tri thay vi chi tu van chuyen khoa.

---

## 5. Kiem tra moi truong MOC 1

Ngay kiem tra: **Tuesday, July 28, 2026**

- Lenh da chay: `python src/app.py`
- Ket qua: app chay duoc, tai thanh cong `config/test_cases.json`, baseline chatbot va ReAct demo deu in ra ket qua.
- Dieu chinh da ap dung: neu `.env` chua co API key hop le, he thong tu fallback sang `MockProvider` de ca nhom van demo duoc.
- Ket luan: moi truong da san sang de sang MOC 2.
