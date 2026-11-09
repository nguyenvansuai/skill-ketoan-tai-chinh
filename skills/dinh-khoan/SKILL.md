---
name: dinh-khoan
description: Định khoản, hạch toán nghiệp vụ kế toán cho doanh nghiệp nhỏ và vừa theo hệ thống tài khoản Thông tư 133/2016 — từ mô tả nghiệp vụ, hóa đơn, phiếu thu chi, sao kê ra bút toán Nợ/Có (mua hàng, bán hàng, giảm trừ doanh thu ghi Nợ 511, lương và bảo hiểm, khấu hao, phân bổ 242, vay, góp vốn, thuế GTGT, TNDN, thuế nhà thầu, kết chuyển 911); kiểm tra file bút toán có dùng sai tài khoản TT200 (521, 641), chưa chi tiết 6421/6422, chi tiền mặt từ 5 triệu mất khấu trừ; xuất Sổ Nhật ký chung Excel. Dùng khi người dùng nói "định khoản", "hạch toán", "bút toán", "nghiệp vụ này ghi nợ có gì", "hạch toán theo 133", "kiểm tra bút toán", "lên sổ nhật ký chung".
---

# Định khoản theo TT133

Đọc `references/nguyen-tac-chung.md`, `references/but-toan-mau-tt133.md`, `references/che-do-ke-toan-dnnvv.md`. Danh mục tài khoản: `references/tai-khoan-tt133.csv`. Điều kiện thuế (5 triệu, khấu trừ, chi phí được trừ): `references/thue-dn-2026.md`.

## 1. Trước khi định khoản

- Chế độ kế toán: TT133 (mặc định), TT58 (siêu nhỏ – chỉ ghi sổ theo nhóm, không định khoản kiểu tài khoản nếu nhóm 1, 3), TT99. Khác TT133 → nói rõ skill này viết theo TT133.
- Phương pháp GTGT: khấu trừ (dùng 133) hay trực tiếp (không dùng 133). Phương pháp hàng tồn kho: kê khai thường xuyên (mặc định) hay kiểm kê định kỳ (611, 631).
- Thiếu chứng từ, số tiền, đối tượng công nợ → `[CẦN BỔ SUNG]`, không đoán.

## 2. Định khoản 1 hoặc vài nghiệp vụ

Với mỗi nghiệp vụ trả về bảng:

| Ngày | Số CT | Diễn giải | TK Nợ | TK Có | Số tiền | Ghi chú thuế |

- Dùng **tài khoản chi tiết đúng TT133**: 6421/6422 (không 641/642 trần), 1331/1332, 33311, 3334, 3335, 3383/3384/3385/3382.
- Giảm trừ doanh thu ghi **Nợ 511** (TT133 không có 521).
- Cột "Ghi chú thuế": hóa đơn từ 5 triệu chưa chuyển khoản → mất khấu trừ GTGT + không được trừ chi phí TNDN; lương chủ DNTN/TNHH MTV cá nhân không được trừ; tiền phạt không được trừ; thuế nhà thầu phải khấu trừ.
- Nghiệp vụ không có trong `references/but-toan-mau-tt133.md` hoặc đặc thù (hợp nhất, cổ phần hóa, xây dựng dài hạn, ngoại tệ phức tạp) → đưa phương án, gắn **[cần kế toán viên xác nhận]**.

## 3. Kiểm tra file bút toán / lên sổ

Người dùng gửi file nhiều bút toán (Excel/CSV): chuyển về CSV cột `ngay,so_ct,dien_giai,tk_no,tk_co,so_tien` (mỗi dòng một cặp Nợ/Có) rồi chạy:

```bash
python3 scripts/kiem_tra_but_toan.py but_toan.csv --xlsx so_nhat_ky_chung.xlsx --phat-sinh phat_sinh.csv
```

- Script báo **LỖI** (tài khoản không có trong TT133, tài khoản chỉ có ở TT200, Nợ ≠ Có, số tiền sai) và **CẢNH BÁO** (chưa chi tiết, tiền mặt ≥5 triệu, Nợ 133 đối ứng lạ, đối ứng trực tiếp giữa hai tài khoản kết quả).
- Excel xuất ra có sheet Sổ Nhật ký chung và Tổng hợp phát sinh (dòng cộng là công thức).
- `phat_sinh.csv` dùng tiếp cho skill `bao-cao-tai-chinh`.

## 4. Đầu ra

1. Bảng bút toán (hoặc kết quả kiểm tra + file Excel), ghi "Đã kiểm tra phép tính" khi đã chạy script.
2. Bảng **Cần anh/chị kiểm tra**: chứng từ thiếu, mục cảnh báo thuế, giả định phương pháp.
3. Câu chốt: "Bút toán là bản nháp tham khảo – kế toán viên xác nhận trước khi ghi sổ chính thức."

<!-- KET-NOI:BAT-DAU (sinh tự động từ scripts/ket_noi.json – sửa ở đó rồi chạy build) -->
## Kết nối ứng dụng

Connector dùng cho skill này: **Google Drive** · **Gmail** · **Microsoft 365 (Outlook, OneDrive/SharePoint, Teams)**. Đọc quy tắc trong `references/ket-noi.md` trước khi dùng.

1. Đọc chứng từ (hóa đơn, phiếu thu chi, hợp đồng, sao kê) trên Drive hoặc tệp đính kèm email người dùng chỉ để định khoản đúng nội dung thật.
2. Lưu bảng định khoản (Excel) vào thư mục kỳ kế toán để nhập phần mềm.

**Khi chưa kết nối:** làm đủ phần soạn thảo, tính toán; đưa nội dung sẵn để người dùng tự dán vào email, lịch, thư mục; nhắc **một lần** cách bật connector, không dừng việc chỉ vì chưa kết nối.
<!-- KET-NOI:KET-THUC -->
