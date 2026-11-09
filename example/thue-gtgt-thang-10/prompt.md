# Prompt – Thuế GTGT tháng 10

## Chuẩn bị (trước giờ dạy)

1. Cài bộ skill kế toán (trọn bộ hoặc 2 skill `doc-hoa-don-xml`, `thue-gtgt-dn`) – xem README gốc của repo.
2. Bật **Code execution** (claude.ai: Settings → Capabilities; ChatGPT: Code Interpreter).
3. Mở cuộc trò chuyện mới, **đính kèm toàn bộ thư mục `dau-vao/`**: 8 file XML trong `hoa-don-mua-vao/`, `ban-ra-thang-10.xlsx`, `so-quy-sao-ke-thang-10.xlsx`, `thong-tin-cong-ty.md`.

## Prompt demo (chép nguyên văn)

```
Tôi là kế toán Công ty TNHH Thương mại An Phát (thông tin trong file thong-tin-cong-ty.md).
Đính kèm 8 file hóa đơn XML mua vào tháng 10/2026, bảng bán ra tháng 10 và sổ quỹ – sao kê ghi cách đã thanh toán từng hóa đơn.

Hãy:
1. Lập bảng kê hóa đơn mua vào tháng 10.
2. Chỉ ra hóa đơn có vấn đề và cho biết hóa đơn nào không được khấu trừ thuế GTGT, vì sao.
3. Tính thuế GTGT phải nộp tháng 10.
4. Cho biết hạn nộp.
5. Soạn thư đề nghị nhà cung cấp xuất lại / điều chỉnh hóa đơn sai.

Xuất bảng kê ra file Excel.
```

Kết quả đúng: xem `ket-qua-mau/ket-qua.md` – **thuế phải nộp 22.824.000 đồng**, 3 hóa đơn có vấn đề (trùng 3301, tiền mặt 568, sai MST 88) và lưu ý HĐ 9015 chưa thanh toán.

## Prompt hỏi tiếp (nếu còn thời gian)

```
Định khoản giúp tôi các hóa đơn mua vào tháng 10 theo Thông tư 133.
```

```
Nếu tôi cứ kê khai cả 8 hóa đơn như file nhận được thì sai bao nhiêu tiền thuế và bị phạt thế nào?
```

## Prompt đầy đủ khi đã kết nối Gmail, Drive, Calendar (chỉ giảng trên slide, không demo)

```
Tìm trong Gmail các thư có hóa đơn XML gửi cho công ty từ 01/10/2026 đến 31/10/2026,
lập bảng kê mua vào và lưu vào thư mục "Kế toán/2026/T10" trên Drive,
tính thuế GTGT tháng 10, tạo nhắc hạn nộp trên lịch của tôi,
và tạo nháp thư gửi nhà cung cấp có hóa đơn sai.
```

Lý do không demo bước Gmail: tìm thư phụ thuộc hộp thư thật, tên tệp đính kèm, quyền truy cập – dễ trục trặc trên lớp. Đặt sẵn file trong `dau-vao/` cho kết quả ổn định.
