---
name: thue-gtgt-dn
description: Tính và chuẩn bị số liệu khai thuế GTGT cho doanh nghiệp nhỏ và vừa năm 2026 — phương pháp khấu trừ (đầu ra trừ đầu vào đủ điều kiện, thuế còn được khấu trừ chuyển kỳ sau) hoặc trực tiếp theo tỷ lệ % doanh thu (1%, 3%, 5%, 2%); loại hóa đơn từ 5 triệu trả tiền mặt (kể cả cộng dồn cùng người bán cùng ngày), giảm thuế suất 8% đến 31/12/2026, kỳ khai tháng hay quý (doanh thu năm trước 50 tỷ), hạn nộp, bút toán khấu trừ 33311/1331, khai bổ sung, hoàn thuế. Dùng khi người dùng hỏi "tính thuế GTGT quý này", "tờ khai 01/GTGT", "thuế VAT phải nộp bao nhiêu", "hóa đơn trả tiền mặt có được khấu trừ không", "còn được khấu trừ chuyển kỳ sau", "thuế suất 8% hay 10%", "khai thuế tháng hay quý".
---

# Thuế GTGT doanh nghiệp

Đọc `references/nguyen-tac-chung.md`, `references/thue-dn-2026.md` (mục 1, 6, 7); căn cứ ở `references/van-ban-hieu-luc.md`.

## 1. Xác định

- Phương pháp: **khấu trừ** (mặc định DN) hay **trực tiếp** (chỉ khi không đủ điều kiện khấu trừ – không phải quyền chọn). TNDN theo % doanh thu không làm mất quyền khấu trừ GTGT.
- Kỳ khai: quý (doanh thu năm trước ≤50 tỷ, DN mới) / tháng (>50 tỷ) – [cần kiểm tra NĐ 252/2026]. Hạn: tháng → ngày 20 tháng sau; quý → ngày cuối tháng đầu quý sau; trùng ngày nghỉ lùi sang ngày làm việc tiếp theo.
- Số thuế còn được khấu trừ kỳ trước (chỉ tiêu chuyển sang trên tờ khai kỳ trước).

## 2. Tính

Khấu trừ – lấy bảng kê từ skill `doc-hoa-don-xml` (`--csv`), thêm cột `thanh_toan` (CK/TM) và `loai_tru` nếu cần:

```bash
python3 scripts/tinh_gtgt.py bang_ke_q3.csv --con-khau-tru-ky-truoc 12000000
```

Trực tiếp:

```bash
python3 scripts/tinh_gtgt.py --truc-tiep hang-hoa=2400000000 dich-vu=300000000 --giam-20
```

## 3. Quy tắc phải nói đúng

- Hóa đơn mua vào **từ 5 triệu** (giá đã có thuế; nhiều hóa đơn cùng người bán cùng ngày cộng lại) phải có **chứng từ thanh toán không dùng tiền mặt** mới được khấu trừ (NĐ 181/2025 Đ.26 – [cần kiểm tra nguyên văn]); trước 01/07/2025 là 20 triệu.
- Thuế suất **8%** chỉ cho nhóm được giảm, đến **31/12/2026** (NĐ 174/2025); loại trừ viễn thông, tài chính, ngân hàng, chứng khoán, bảo hiểm, BĐS, kim loại, khai khoáng, hàng chịu TTĐB. Sau 31/12/2026 kiểm tra có gia hạn không.
- Đầu vào dùng chung cho hoạt động chịu thuế và không chịu thuế: phân bổ theo tỷ lệ doanh thu [cần kiểm tra].
- Khai sai: tự khai bổ sung, nộp đủ tiền thuế + tiền chậm nộp 0,03%/ngày **trước khi** có quyết định kiểm tra → không bị phạt khai sai (Luật 108/2025 Đ.44 k.2 điểm a).
- Hoàn thuế GTGT (xuất khẩu, dự án đầu tư…): điều kiện riêng – nêu nguyên tắc, chuyển người hành nghề.
- Mẫu tờ khai, số chỉ tiêu: theo TT 89/2026 → [cần kiểm tra mẫu mới] trước khi chỉ chỉ tiêu cụ thể; không tự điền thay người dùng trên eTax.

## 4. Đầu ra

1. Bảng tính: đầu ra, đầu vào được khấu trừ, còn được khấu trừ kỳ trước → **phải nộp** hoặc **chuyển kỳ sau**; "Đã kiểm tra phép tính".
2. Danh sách hóa đơn bị loại khỏi khấu trừ và hóa đơn cần bổ sung chứng từ chuyển khoản.
3. Bút toán: khấu trừ Nợ 33311 / Có 1331; nộp thuế Nợ 33311 / Có 112.
4. Hạn khai, nộp của kỳ (gợi ý dùng skill `lich-thue-dn`).
5. Câu chốt: "Đối chiếu tờ khai trên eTax/HTKK và hỏi cơ quan thuế quản lý trước khi nộp."
