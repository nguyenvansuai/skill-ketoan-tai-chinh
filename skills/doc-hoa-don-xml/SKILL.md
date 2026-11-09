---
name: doc-hoa-don-xml
description: Đọc hàng loạt file XML hóa đơn điện tử Việt Nam (Viettel, VNPT, MISA meInvoice, BKAV, EasyInvoice… theo định dạng của Tổng cục Thuế) thành bảng kê hóa đơn mua vào, bán ra kèm tổng theo thuế suất; kiểm tra cộng dòng, tổng tiền, thuế suất 8% sau 31/12/2026, thiếu mã cơ quan thuế, thiếu chữ ký số, MST sai, hóa đơn trùng, hóa đơn cùng người bán cùng ngày từ 5 triệu phải chuyển khoản; gợi ý bút toán TT133 và xuất Excel. Dùng khi người dùng gửi file .xml hóa đơn, thư mục hóa đơn, hoặc nói "đọc hóa đơn xml", "lập bảng kê mua vào bán ra", "tổng hợp hóa đơn đầu vào", "kiểm tra hóa đơn trước khi kê khai", "nhập hóa đơn vào sổ".
---

# Đọc hóa đơn điện tử XML

Đọc `references/nguyen-tac-chung.md`, `references/cau-truc-xml.md`; điều kiện khấu trừ ở `references/thue-dn-2026.md`.

## 1. Đầu vào

- **File XML** (dữ liệu gốc). PDF/ảnh chỉ là bản thể hiện: nếu người dùng chỉ có PDF/ảnh, đọc thủ công từng trường, chữ mờ ghi `[?]`, và khuyên tải XML từ email người bán hoặc hoadondientu.gdt.gov.vn.
- **MST của doanh nghiệp** để phân loại mua vào / bán ra. Thiếu thì hỏi.
- File ZIP: giải nén vào thư mục riêng trước khi đọc.

## 2. Chạy script

```bash
python3 scripts/doc_hoa_don.py thu_muc_xml/ --mst-cua-toi 0312345678 --xlsx bang_ke_hoa_don.xlsx --csv bang_ke.csv
```

Kết quả: bảng kê theo chiều mua vào / bán ra, tổng theo thuế suất, cảnh báo từng hóa đơn, danh sách người bán cần chứng từ chuyển khoản (≥5 triệu cùng ngày), hóa đơn trùng, gợi ý bút toán tổng hợp. Excel có sheet Mua vào / Bán ra, dòng cộng là công thức.

## 3. Diễn giải kết quả

- Cảnh báo **không có MCCQT**: có thể là hóa đơn không mã (máy tính tiền, hóa đơn không mã của DN đủ điều kiện) – không phải lỗi; vẫn tra trạng thái trên hoadondientu.gdt.gov.vn.
- **Không tự xác định hóa đơn hợp lệ**: script chỉ kiểm tra số học và định dạng; trạng thái hóa đơn (thay thế, điều chỉnh, hủy), rủi ro người bán phải tra cứu trên cổng thuế.
- Phân loại tài khoản Nợ cho hóa đơn mua vào theo **bản chất**: hàng để bán 156, nguyên vật liệu 152, công cụ dưới chuẩn TSCĐ dùng nhiều kỳ 153/242, chi phí dùng ngay 6421/6422, TSCĐ 211 + 1332. Hỏi lại khi không rõ.
- Hóa đơn mua vào từ 5 triệu chưa có chứng từ chuyển khoản → nhắc: chưa đủ điều kiện khấu trừ GTGT, không được trừ chi phí TNDN.

## 4. Đầu ra

1. Bảng kê (hoặc file Excel) + tổng số thuế GTGT đầu vào, đầu ra theo kỳ.
2. Bảng **Cần anh/chị kiểm tra**: từng hóa đơn có cảnh báo, hóa đơn cần chứng từ chuyển khoản, hóa đơn trùng.
3. Bước tiếp: dùng skill `dinh-khoan` để hạch toán chi tiết, `thue-gtgt-dn` để lập số liệu tờ khai.
4. Câu chốt: "Tra cứu hóa đơn trên hoadondientu.gdt.gov.vn và đối chiếu quy định hiện hành trước khi kê khai."

<!-- KET-NOI:BAT-DAU (sinh tự động từ scripts/ket_noi.json – sửa ở đó rồi chạy build) -->
## Kết nối ứng dụng

Connector dùng cho skill này: **Gmail** · **Google Drive** · **Microsoft 365 (Outlook, OneDrive/SharePoint, Teams)**. Đọc quy tắc trong `references/ket-noi.md` trước khi dùng.

1. Tìm thư nhà cung cấp gửi hóa đơn trong kỳ: `has:attachment filename:xml after:2026/10/01 before:2026/11/01` (thêm `subject:hóa đơn` nếu cần); lấy file XML đính kèm để đọc hàng loạt.
2. Hoặc đọc cả thư mục hóa đơn XML theo tháng trên Drive.
3. Lưu bảng kê mua vào/bán ra (Excel/Sheets) vào thư mục kỳ kế toán; tạo nháp email đề nghị nhà cung cấp xuất lại hóa đơn sai thông tin.

**Khi chưa kết nối:** làm đủ phần soạn thảo, tính toán; đưa nội dung sẵn để người dùng tự dán vào email, lịch, thư mục; nhắc **một lần** cách bật connector, không dừng việc chỉ vì chưa kết nối.
<!-- KET-NOI:KET-THUC -->
