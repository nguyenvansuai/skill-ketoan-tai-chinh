# Kết quả mẫu – Thuế GTGT tháng 10/2026, Công ty TNHH Thương mại An Phát

Kết quả chạy thật bằng công cụ của skill `doc-hoa-don-xml` và `thue-gtgt-dn` trên dữ liệu trong `dau-vao/`. Dùng để giảng viên đối chiếu; câu chữ AI trả lời mỗi lần có thể khác, **con số phải giống**.

## 1. Bảng kê hóa đơn mua vào (8 file → 7 hóa đơn)

| Ngày | Số HĐ | Người bán | Tiền hàng | Thuế | Tổng | Thanh toán | Khấu trừ? |
|---|---|---|---:|---:|---:|---|---|
| 03/10 | 1201 | Giấy Sài Gòn | 45.000.000 | 3.600.000 | 48.600.000 | CK | Được |
| 06/10 | 568 | Vận tải Minh Long | 12.000.000 | 960.000 | 12.960.000 | **Tiền mặt** | **Không** |
| 09/10 | 3301 | Bao bì Thành Công | 28.500.000 | 2.280.000 | 30.780.000 | CK | Được |
| 09/10 | 3301 | Bao bì Thành Công (file gửi lại) | – | – | – | – | **Trùng – loại** |
| 14/10 | 88 | Thiết bị VP Hoàng Gia | 9.800.000 | 784.000 | 10.584.000 | CK | **Không – sai MST người mua** |
| 15/10 | 4521 | Viễn thông Sao Việt | 1.500.000 | 150.000 | 1.650.000 | Tiền mặt (dưới 5 triệu) | Được |
| 20/10 | 702 | Điện máy Nam Phong | 3.200.000 | 256.000 | 3.456.000 | Tiền mặt (dưới 5 triệu) | Được |
| 28/10 | 9015 | Logistics Cát Lái | 18.000.000 | 1.440.000 | 19.440.000 | Chưa trả (trả chậm 30 ngày) | Được, **phải bổ sung chứng từ CK khi trả** |

File Excel: `bang-ke-mua-vao-thang-10.xlsx` (sheet "Mua vao" và "Chua phan loai" do công cụ xuất).

## 2. Hóa đơn có vấn đề

1. **HĐ 3301 trùng** – nhà cung cấp gửi 2 lần cùng ký hiệu C26TTC, số 3301. Chỉ kê khai 1 lần. Nếu cộng cả hai: khai thừa 2.280.000 thuế đầu vào.
2. **HĐ 568 trả tiền mặt 12.960.000** – từ 5 triệu đồng trở lên phải có chứng từ thanh toán không dùng tiền mặt mới được khấu trừ (Luật GTGT 48/2024 Điều 14 khoản 2; NĐ 181/2025 Điều 26). Loại 960.000 thuế; chi phí này cũng có rủi ro không được trừ khi tính thuế TNDN.
3. **HĐ 88 ghi sai mã số thuế người mua** – trên hóa đơn là 0319876534, đúng phải là 0319876543 (đảo hai số cuối). Chưa khấu trừ 784.000; đề nghị người bán lập hóa đơn điều chỉnh (thư nháp ở mục 5).
4. **HĐ 9015 chưa thanh toán** – hóa đơn từ 5 triệu, hợp đồng cho trả chậm 30 ngày: được kê khai, nhưng khi trả phải chuyển khoản và lưu chứng từ [cần kiểm tra quy định mua trả chậm].

## 3. Số thuế GTGT tháng 10/2026

| Chỉ tiêu | Số tiền (đồng) |
|---|---:|
| Thuế còn được khấu trừ kỳ trước chuyển sang | 1.850.000 |
| Thuế GTGT đầu vào đủ điều kiện khấu trừ | 7.726.000 |
| Doanh số bán ra chưa thuế (8%: 380.000.000; 10%: 20.000.000) | 400.000.000 |
| Thuế GTGT đầu ra (8%: 30.400.000; 10%: 2.000.000) | 32.400.000 |
| **Thuế GTGT phải nộp** | **22.824.000** |

So với cách cộng tay tất cả 8 file: thuế đầu vào 11.750.000 → phải nộp 18.800.000, **khai thiếu 4.024.000 đồng** → bị truy thu, phạt 20% số thuế khai thiếu và tiền chậm nộp 0,03%/ngày.

## 4. Hạn nộp

Kê khai theo tháng → nộp tờ khai và tiền thuế tháng 10/2026 **chậm nhất ngày 20/11/2026 (thứ Sáu)**.

## 5. Thư nháp gửi nhà cung cấp

> **Tiêu đề:** Đề nghị điều chỉnh mã số thuế người mua trên hóa đơn số 88, ký hiệu C26THG ngày 14/10/2026
>
> Kính gửi Công ty TNHH Thiết bị Văn phòng Hoàng Gia,
>
> Công ty TNHH Thương mại An Phát đã nhận hóa đơn GTGT số 88, ký hiệu C26THG, lập ngày 14/10/2026, tổng thanh toán 10.584.000 đồng. Hóa đơn ghi mã số thuế người mua là **0319876534**, mã số thuế đúng của chúng tôi là **0319876543**.
>
> Đề nghị Quý công ty lập hóa đơn điều chỉnh thông tin mã số thuế người mua theo quy định và gửi lại cho chúng tôi trước ngày 18/11/2026 để kịp kê khai thuế tháng 10.
>
> Trân trọng,
> [Họ tên kế toán] – Công ty TNHH Thương mại An Phát

## 6. Kế toán vẫn phải tự làm

- Tra cứu 7 hóa đơn trên hoadondientu.gdt.gov.vn (trạng thái, có bị thay thế không).
- Đối chiếu số liệu với tờ khai trên eTax/HTKK, kế toán trưởng duyệt rồi mới nộp.
- Tự bấm gửi thư cho nhà cung cấp.
