---
name: lich-thue-dn
description: Lập lịch hạn khai, nộp thuế và báo cáo tài chính cả năm cho doanh nghiệp nhỏ và vừa — GTGT và TNCN khấu trừ theo tháng (ngày 20) hoặc quý (ngày cuối tháng đầu quý sau), tạm nộp TNDN quý, quyết toán TNDN, TNCN và nộp BCTC (ngày cuối tháng thứ 3 sau năm), gia hạn nộp tiền 2026 theo NĐ 245/2026, tự lùi hạn trùng thứ Bảy, Chủ nhật, ngày lễ, báo hạn đã quá và sắp tới trong 60 ngày, xuất file .ics nhập Google Calendar, iPhone, Outlook có nhắc trước. Dùng khi người dùng hỏi "lịch nộp thuế", "hạn nộp tờ khai quý này", "hạn quyết toán thuế", "khi nào phải nộp BCTC", "nhắc lịch thuế vào Google Calendar", "tháng này có hạn thuế gì", "đã trễ hạn chưa".
---

# Lịch thuế doanh nghiệp

Đọc `references/nguyen-tac-chung.md`, `references/thue-dn-2026.md` (mục 6, 6a, 7); căn cứ ở `references/van-ban-hieu-luc.md`. Hộ kinh doanh: dùng `lich-thue-hkd` trong bộ `skill-ho-kinh-doanh`.

## 1. Xác định

- **Hôm nay** (lấy từ ngữ cảnh hội thoại hoặc hệ thống; không có thì hỏi).
- Năm tài chính (mặc định năm dương lịch; năm tài chính khác → tính lại hạn theo ngày kết thúc năm, script chưa hỗ trợ).
- Kỳ khai GTGT, TNCN: **quý** (doanh thu năm trước ≤50 tỷ, DN mới) hay **tháng** – [cần kiểm tra NĐ 252/2026].
- Có trả lương phải khấu trừ TNCN không; năm 2026 có thuộc diện gia hạn NĐ 245/2026 (DN nhỏ, siêu nhỏ hoặc 43 ngành) và **đã gửi đề nghị gia hạn** chưa.

## 2. Chạy script

```bash
python3 scripts/tao_lich_thue.py --nam 2026 --ky-khai quy --nd245 --hom-nay 2026-11-02 --ics lich_thue_2026.ics
python3 scripts/tao_lich_thue.py --nam 2027 --ky-khai thang --ngay-nghi 2027-02-05,2027-02-08,2027-02-09 --ics lich_thue_2027.ics
```

- Ngày nghỉ tự tính: thứ Bảy, Chủ nhật, 01/01, 30/04, 01/05, 02/09. **Tết Âm lịch, Giỗ Tổ Hùng Vương, nghỉ bù** chưa có trong script → tra lịch nghỉ chính thức của năm và nhập `--ngay-nghi`; chưa có lịch chính thức thì nói rõ.
- File `.ics` nhắc trước 7 và 2 ngày (đổi bằng `--nhac-truoc`). Nhập Google Calendar: Cài đặt → Nhập và xuất → Nhập.

## 3. Quy tắc phải nói đúng

- Hạn nộp tiền thuế = hạn nộp hồ sơ khai. Hạn trùng ngày nghỉ được lùi sang ngày làm việc tiếp theo (NĐ 252/2026 Đ.3 k.7), nhưng **khuyên nộp trước hạn gốc**.
- NĐ 245/2026 **chỉ lùi hạn nộp tiền**, không lùi hạn tờ khai; phải gửi đề nghị chậm nhất 02/11/2026; **không** gia hạn TNCN khấu trừ của NLĐ.
- Lệ phí môn bài: bỏ từ 01/01/2026 (NQ 198/2025) – không đưa vào lịch, chỉ rà nợ tồn đọng trước 2026.
- Thuế nhà thầu: khai theo từng lần thanh toán → dùng skill `thue-nha-thau`.
- Trễ hạn: tiền chậm nộp 0,03%/ngày (Luật 108/2025 Đ.16); phạt chậm nộp hồ sơ theo số ngày (NĐ 125/2020 Đ.13, mức cho tổ chức: 2–5 triệu nếu 1–30 ngày … 15–25 triệu nếu trên 90 ngày có thuế phải nộp). Tự khai bổ sung, nộp đủ trước khi có quyết định kiểm tra thì không bị phạt khai sai (Luật 108/2025 Đ.44).

## 4. Đầu ra

1. Bảng lịch: hạn thực tế, hạn gốc nếu bị lùi, việc, trạng thái (**ĐÃ QUÁ / HÔM NAY / còn N ngày**) – hạn đã quá đặt lên đầu phần "Việc cần làm ngay".
2. File `.ics` (và `.csv` nếu cần).
3. Bảng **Cần anh/chị kiểm tra**: kỳ khai tháng/quý, ngày nghỉ Tết, nghỉ bù chưa nhập, điều kiện gia hạn.
4. Câu chốt: "Đối chiếu văn bản hiện hành và thông báo của cơ quan thuế trước khi dựa vào lịch."

<!-- KET-NOI:BAT-DAU (sinh tự động từ scripts/ket_noi.json – sửa ở đó rồi chạy build) -->
## Kết nối ứng dụng

Connector dùng cho skill này: **Google Calendar** · **Google Drive** · **Microsoft 365 (Outlook, OneDrive/SharePoint, Teams)**. Đọc quy tắc trong `references/ket-noi.md` trước khi dùng.

1. Đưa lịch hạn thuế cả năm vào Google Calendar/Outlook thành sự kiện cả ngày có nhắc trước 5 ngày và 1 ngày (sau khi xác nhận danh sách).
2. Lưu bảng lịch thuế vào Drive.

**Khi chưa kết nối:** làm đủ phần soạn thảo, tính toán; đưa nội dung sẵn để người dùng tự dán vào email, lịch, thư mục; nhắc **một lần** cách bật connector, không dừng việc chỉ vì chưa kết nối.
<!-- KET-NOI:KET-THUC -->
