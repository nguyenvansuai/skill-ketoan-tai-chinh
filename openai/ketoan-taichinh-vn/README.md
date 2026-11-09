# Kế toán – Tài chính VN – gói cho ChatGPT / Codex

Thư mục này được sinh tự động bởi `scripts/build_openai.py` – không sửa tay.

Bộ 12 skill cho kế toán và chủ doanh nghiệp nhỏ, vừa, siêu nhỏ Việt Nam năm 2026: chọn chế độ kế toán (TT133, TT58), định khoản, đọc hóa đơn điện tử XML, đối soát ngân hàng và công nợ, khóa sổ, lập báo cáo tài chính, thuế GTGT, TNDN, thuế nhà thầu, bảng lương – bảo hiểm, lịch thuế, dự báo dòng tiền. Tính toán bằng script, không bịa số.

## Skill (12)

- `bao-cao-tai-chinh`
- `che-do-ke-toan`
- `dinh-khoan`
- `doc-hoa-don-xml`
- `doi-soat`
- `dong-tien-chu-dn`
- `khoa-so-cuoi-ky`
- `lich-thue-dn`
- `luong-bao-hiem`
- `thue-gtgt-dn`
- `thue-nha-thau`
- `thue-tndn`

## Cài đặt

Xem README ở gốc repo, mục **ChatGPT / Codex**.

## Connector khai báo sẵn (`.app.json`)

Khi cài plugin, ChatGPT đề nghị kết nối các ứng dụng: `gmail`, `google-drive`, `google-calendar`, `outlook-email`, `outlook-calendar`, `sharepoint`, `teams`. Mỗi người đăng nhập một lần bằng tài khoản của mình. Chưa kết nối thì skill vẫn chạy, chỉ không tự lấy dữ liệu hoặc tạo nháp được.
