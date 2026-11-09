---
name: che-do-ke-toan
description: Xác định doanh nghiệp siêu nhỏ, nhỏ hay vừa (NĐ 80/2021) và chọn chế độ kế toán phù hợp năm 2026 — TT133/2016 cho DNNVV, TT58/2026 cho DN siêu nhỏ (4 nhóm sổ theo phương pháp nộp thuế, chỉ áp dụng năm tài chính bắt đầu từ/sau 01/07/2026), hay TT99/2025; tra hệ thống tài khoản TT133, mẫu sổ, mẫu BCTC, có cần kế toán trưởng không, ai được làm kế toán, chuyển đổi chế độ khi nào. Dùng khi người dùng hỏi "công ty tôi áp dụng thông tư nào", "TT133 hay TT58", "DN siêu nhỏ là gì", "hệ thống tài khoản 133", "tài khoản 642 là gì", "có cần kế toán trưởng không", "vợ giám đốc làm kế toán được không", "chuyển từ 133 sang 99".
---

# Chế độ kế toán cho DN nhỏ và vừa

Đọc `references/nguyen-tac-chung.md`, `references/che-do-ke-toan-dnnvv.md`; căn cứ và độ tin cậy ở `references/van-ban-hieu-luc.md`. Danh mục tài khoản máy đọc: `references/tai-khoan-tt133.csv`.

## 1. Thu thập (hỏi tối đa 3 câu, gộp một lượt)

- Lĩnh vực chính: nông–lâm–thủy sản / công nghiệp–xây dựng / thương mại–dịch vụ.
- Số lao động **tham gia BHXH bình quân năm**; tổng doanh thu năm; tổng nguồn vốn (nếu biết).
- Ngày bắt đầu năm tài chính; chế độ đang áp dụng; phương pháp thuế GTGT (khấu trừ hay % doanh thu) và TNDN (thu nhập tính thuế hay % doanh thu) đang được cơ quan thuế chấp nhận.
- Loại hình: DNTN, TNHH MTV cá nhân, TNHH 2 TV, cổ phần (ảnh hưởng ai được làm kế toán).

## 2. Chạy script

```bash
python3 scripts/xac_dinh_quy_mo.py --linh-vuc thuong-mai-dich-vu --lao-dong 6 --doanh-thu 4.2e9 --nguon-von 1.5e9 \
    --doanh-thu-nam-truoc 3.8e9 --nam-tai-chinh-bat-dau 2027-01-01
```

Kết quả: quy mô, các chế độ được áp dụng, cờ thuế cần rà (miễn ≤1 tỷ, 15%/17%, giảm 30% NQ 43, kỳ khai GTGT).

## 3. Quy tắc phải nói đúng

- **TT133 vẫn còn hiệu lực**; TT58 chỉ thay TT132. TT99 không bắt buộc DNNVV. Bộ Tài chính có kế hoạch sửa/thay TT133 trong 2026–2027 → nhắc kiểm tra văn bản mới.
- TT58 áp dụng **năm tài chính bắt đầu từ/sau 01/07/2026**. DN năm dương lịch đang dùng TT133: theo câu chữ năm 2027 mới chuyển được – nói rõ đây là suy luận về kỳ, khuyên hỏi người hành nghề trước khi đổi sổ giữa năm.
- TT58 **không cho quyền chọn phương pháp thuế**; nhóm sổ (1–4) đi theo phương pháp thuế hợp lệ. Nhóm TNDN theo % doanh thu không bắt buộc lập BCTC để nộp, nhóm TNDN theo thu nhập phải lập B01-DNSN, B02-DNSN.
- Siêu nhỏ: không bắt buộc kế toán trưởng (NĐ 174/2016 Đ.20). DNTN, TNHH MTV do cá nhân làm chủ: người thân, người quản lý, thủ kho, thủ quỹ được làm kế toán (Luật Kế toán Đ.52 k.3–4). Không có kế toán trưởng **không** có nghĩa là không cần sổ sách, BCTC.
- Đổi chế độ chỉ từ **đầu năm tài chính tiếp theo**; vượt ngưỡng siêu nhỏ trong năm thì dùng tiếp đến hết năm.
- Tra tài khoản: đọc `references/tai-khoan-tt133.csv` (cột `tinh_chat`: No/Co/LuongTinh/KhongSoDu). Chỉ ra khác biệt TT133 với TT200/TT99 (không có 521, gộp 641 vào 6421…) khi người dùng quen chế độ cũ.

## 4. Đầu ra

1. Kết luận: DN thuộc quy mô gì, nên/được áp dụng chế độ nào, từ năm tài chính nào.
2. Bảng việc phải làm: chế độ, hình thức sổ (Nhật ký chung…), bộ sổ tối thiểu, mẫu BCTC, người làm kế toán, lưu trữ 10 năm; nếu chuyển chế độ: chốt số dư cuối năm, chuyển số dư theo hướng dẫn (TT58 Đ.11), quy chế hạch toán nếu tự sửa mẫu (TT 46/2025).
3. Bảng **Cần anh/chị kiểm tra**: ngưỡng NĐ 80 hiện hành, phương pháp thuế đã đăng ký, mục [cần kiểm tra].
4. Câu chốt: "Đối chiếu văn bản hiện hành và hỏi kế toán hành nghề hoặc cơ quan thuế trước khi đổi chế độ."

<!-- KET-NOI:BAT-DAU (sinh tự động từ scripts/ket_noi.json – sửa ở đó rồi chạy build) -->
## Kết nối ứng dụng

Connector dùng cho skill này: **Google Drive** · **Microsoft 365 (Outlook, OneDrive/SharePoint, Teams)**. Đọc quy tắc trong `references/ket-noi.md` trước khi dùng.

1. Đọc BCTC, tờ khai năm trước trên Drive để xác định quy mô doanh nghiệp (doanh thu, lao động, nguồn vốn) thay vì hỏi lại.

**Khi chưa kết nối:** làm đủ phần soạn thảo, tính toán; đưa nội dung sẵn để người dùng tự dán vào email, lịch, thư mục; nhắc **một lần** cách bật connector, không dừng việc chỉ vì chưa kết nối.
<!-- KET-NOI:KET-THUC -->
