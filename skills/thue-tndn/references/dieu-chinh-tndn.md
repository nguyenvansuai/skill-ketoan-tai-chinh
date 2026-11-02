# Điều chỉnh từ lợi nhuận kế toán sang thu nhập tính thuế TNDN

> Dùng để lập file `dieu_chinh.csv` (cột `noi_dung,so_tien,loai`) cho `scripts/tinh_tndn.py`. Căn cứ và độ tin cậy: `van-ban-hieu-luc.md`. Mục **[cần kiểm tra]** chưa đối chiếu nguyên văn. Đây là danh mục rà soát thường gặp, không thay hướng dẫn của cơ quan thuế.

Thu nhập tính thuế = (lợi nhuận kế toán + điều chỉnh tăng − điều chỉnh giảm) − thu nhập được miễn − lỗ được kết chuyển (Luật 67/2025 Đ.7).

## `tang` – chi phí đã hạch toán nhưng không được trừ

| Khoản | Căn cứ / ghi chú | Lấy số ở đâu |
|---|---|---|
| Khoản chi **từ 5 triệu đồng** không có chứng từ thanh toán không dùng tiền mặt | NĐ 320/2025 (trước đây 20 triệu) – TC | Sổ quỹ 111, cảnh báo của `dinh-khoan/scripts/kiem_tra_but_toan.py` |
| Thuế GTGT đầu vào của khoản mua **không có chứng từ thanh toán không dùng tiền mặt** đã ghi vào chi phí | Luật 48/2024 Đ.14 k.1 điểm e – NV | TK 1331 bị loại, 6421/6422 |
| Tiền lương, thù lao của chủ DNTN, chủ công ty TNHH MTV là cá nhân | Luật 67/2025 Đ.9 k.2 điểm h – NV | Bảng lương, TK 334 chi tiết chủ DN |
| Chi không có hóa đơn, chứng từ hợp pháp; hóa đơn bất hợp pháp, người bán bỏ địa chỉ | Nguyên tắc chi phí được trừ – TC | Bảng kê `doc-hoa-don-xml`, tra cứu MST |
| Chi không phục vụ hoạt động sản xuất kinh doanh (chi cá nhân, gia đình) | Nguyên tắc chi phí được trừ | Sổ chi tiết 6421, 6422, 811 |
| Tiền phạt vi phạm hành chính (thuế, giao thông, lao động…), tiền chậm nộp thuế | Không được trừ – TC | TK 811 |
| Khấu hao TSCĐ vượt khung thời gian, TSCĐ không phục vụ SXKD, không có hồ sơ | TT 45/2013 (hiệu lực không quá 31/12/2026) – TC | Bảng khấu hao `khoa-so-cuoi-ky/scripts/khau_hao.py` |
| Chi phí trích trước (335) không chi hết, dự phòng không đủ hồ sơ | TC | TK 335, 229, 352 |
| Thuế TNDN, thuế GTGT đầu vào đã khấu trừ hoặc hoàn mà vẫn ghi chi phí | Nguyên tắc | TK 821, 6422 |
| Chi phí của năm khác hạch toán vào năm nay | Nguyên tắc phù hợp | Rà chứng từ |
| Phần chi vượt mức theo quy định riêng (vd lãi vay vượt mức với giao dịch liên kết) | NĐ về giao dịch liên kết – **chuyển người hành nghề** | — |

## `giam` – giảm thu nhập chịu thuế

| Khoản | Ghi chú |
|---|---|
| Khoản thu nhập đã tính thuế ở kỳ trước nay hạch toán lại (hoàn nhập dự phòng đã bị loại khi tính thuế…) | Phải có hồ sơ năm trước |
| Chênh lệch tỷ giá đánh giá lại số dư cuối kỳ chưa thực hiện (nếu thuộc diện không tính thu nhập chịu thuế) | **[cần kiểm tra]** |

## `mien` – thu nhập được miễn thuế

Chỉ nhập khi đã xác định đúng điều kiện (ưu đãi, cổ tức nhận từ DN trong nước đã nộp TNDN…). **Miễn TNDN cho DN doanh thu năm ≤1 tỷ** (NĐ 141/2026) và **miễn cho DNNVV đăng ký lần đầu** (NQ 198/2025, NĐ 20/2026) là miễn **cả số thuế**, không nhập ở đây – rà riêng điều kiện.

## `lo` – lỗ các năm trước chuyển sang

Ghi từng năm lỗ còn được chuyển (theo tờ khai quyết toán các năm trước). Thời hạn chuyển lỗ tối đa 5 năm liên tục **[cần kiểm tra theo Luật 67/2025]**. Lỗ của hoạt động chuyển nhượng BĐS, dự án có quy định bù trừ riêng **[cần kiểm tra]**.

## Mẫu file

```csv
noi_dung,so_tien,loai
Chi tiền mặt từ 5 triệu (PC045 tháng 8),12000000,tang
Lương chủ công ty TNHH MTV,180000000,tang
Phạt chậm nộp tờ khai,3500000,tang
Hoàn nhập dự phòng đã loại năm 2025,2000000,giam
Lỗ năm 2024 còn chuyển,50000000,lo
```
