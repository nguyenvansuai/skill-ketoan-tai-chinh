# Skill AI Kế toán – Tài chính cho doanh nghiệp nhỏ và vừa (Việt Nam 2026)

Bộ **8 skill** giúp Claude (và ChatGPT) hỗ trợ **kế toán, chủ doanh nghiệp nhỏ, vừa và siêu nhỏ** làm sổ sách và thuế theo quy định năm 2026: chọn chế độ kế toán (**TT133/2016**, **TT58/2026**), định khoản, đọc hóa đơn điện tử XML, đối soát ngân hàng và công nợ, khóa sổ, lập BCTC, tính thuế GTGT và TNDN.

Mọi skill theo cùng nguyên tắc: **không bịa, không đoán số** (chữ mờ đánh dấu `[?]`), **tính bằng code**, viện dẫn pháp luật kèm số hiệu văn bản và độ tin cậy, **không tự khai, nộp, ký, xuất hóa đơn thay**.

> Hộ kinh doanh, cá nhân kinh doanh: dùng bộ [skill-ho-kinh-doanh](https://github.com/nguyenvansuai/skill-ho-kinh-doanh). Thuế TNCN cá nhân (quyết toán, người phụ thuộc, người nước ngoài): dùng thêm [tndvnn/tncn](https://github.com/tndvnn/tncn).

## Tải nhanh – không cần cài

| File | Dùng để |
|---|---|
| [`qua-tang/10_cau_lenh_AI_cho_Ke_toan_DNNVV.pdf`](qua-tang/10_cau_lenh_AI_cho_Ke_toan_DNNVV.pdf) | 10 câu lệnh sao chép dán vào ChatGPT, Claude: định khoản, bảng kê hóa đơn, đối soát, khóa sổ, BCTC, GTGT, TNDN |
| [`qua-tang/Mau_so_ke_toan_DNNVV_TT133.xlsx`](qua-tang/Mau_so_ke_toan_DNNVV_TT133.xlsx) | Nhập số dư đầu kỳ + Sổ Nhật ký chung → file tự lập Bảng cân đối phát sinh, B02-DNN, B01a-DNN bằng công thức, có dòng kiểm tra tài sản = nguồn vốn |
| [`van-ban/`](van-ban) | Toàn văn Luật GTGT 48/2024, Luật Quản lý thuế 108/2025, Luật 09/2026, NĐ 141/2026, NĐ 254/2026 (bản chữ) + đường dẫn chính thức các văn bản còn lại |

Trên điện thoại: bấm vào tên file → nút **Download** (biểu tượng tải xuống) góc phải.

## Danh sách skill

| # | Skill | Lệnh | Làm gì |
|---|---|---|---|
| 01 | Chế độ kế toán | `/che-do-ke-toan` | Xác định DN siêu nhỏ/nhỏ/vừa (NĐ 80/2021); chọn TT133, TT58 (4 nhóm sổ theo phương pháp thuế) hay TT99; hệ thống tài khoản TT133; kế toán trưởng, người làm kế toán; khi nào được đổi chế độ |
| 02 | Định khoản | `/dinh-khoan` | Nghiệp vụ → bút toán Nợ/Có theo TT133 (không có 521, 641 → 6421); kiểm tra file bút toán, cảnh báo chi tiền mặt từ 5 triệu; xuất Sổ Nhật ký chung Excel |
| 03 | Đọc hóa đơn XML | `/doc-hoa-don-xml` | Đọc hàng loạt XML hóa đơn điện tử (Viettel, VNPT, MISA, BKAV…) → bảng kê mua vào/bán ra, kiểm tra cộng sai, thiếu mã CQT, trùng hóa đơn, cùng người bán cùng ngày từ 5 triệu |
| 04 | Đối soát | `/doi-soat` | Đối chiếu sổ 112 với sao kê, bảng điều chỉnh số dư; tuổi nợ 131/331, dự phòng nợ khó đòi tham khảo; biên bản đối chiếu công nợ; kiểm kê quỹ |
| 05 | Khóa sổ cuối kỳ | `/khoa-so-cuoi-ky` | Checklist tháng/quý/năm có thứ tự phụ thuộc; khấu hao TSCĐ theo ngày, phân bổ 242; kết chuyển 911 |
| 06 | Báo cáo tài chính | `/bao-cao-tai-chinh` | Từ bảng cân đối phát sinh → B01a-DNN, B02-DNN, F01-DNN (Excel có công thức, dòng kiểm tra 200 = 500); dàn ý thuyết minh B09-DNN; chỉ số nhanh |
| 07 | Thuế GTGT | `/thue-gtgt-dn` | Khấu trừ hoặc trực tiếp; loại hóa đơn từ 5 triệu trả tiền mặt; 8% đến 31/12/2026; kỳ khai tháng/quý; gia hạn NĐ 245/2026 |
| 08 | Thuế TNDN | `/thue-tndn` | Thuế suất 15%/17%/20% theo doanh thu năm trước; rà miễn ≤1 tỷ, giảm 30% NQ 43/2026; điều chỉnh chi phí không được trừ; chuyển lỗ; tạm nộp quý, mức 80%; quyết toán |

**Sắp có:** lương – bảo hiểm, thuế nhà thầu nước ngoài, lịch thuế DN (.ics), dòng tiền 13 tuần cho chủ DN.

## Cài đặt

### Claude.ai (web / app) – dễ nhất

1. Bật **Settings → Capabilities → Code execution and file creation**.
2. Vào **Settings → Capabilities → Skills → Upload skill**.
3. Tải lên từng file trong [`dist/`](dist) (ví dụ `dist/thue-tndn.zip`).

Sau đó nói tự nhiên: "định khoản giúp tôi nghiệp vụ này", "đọc thư mục hóa đơn xml quý 3", "thuế TNDN năm nay bao nhiêu", Claude tự chọn skill.

### Claude Code – cài qua plugin marketplace

Cài cả bộ 8 skill (một lệnh, Claude Code 2.1.275 trở lên):

```
/plugin install tron-bo-skill-ke-toan --marketplace nguyenvansuai/skill-ketoan-tai-chinh
```

Hoặc cài từng skill:

```
/plugin install che-do-ke-toan --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install dinh-khoan --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install doc-hoa-don-xml --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install doi-soat --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install khoa-so-cuoi-ky --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install bao-cao-tai-chinh --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install thue-gtgt-dn --marketplace nguyenvansuai/skill-ketoan-tai-chinh
/plugin install thue-tndn --marketplace nguyenvansuai/skill-ketoan-tai-chinh
```

Claude Code bản cũ hơn: chạy `/plugin marketplace add nguyenvansuai/skill-ketoan-tai-chinh` một lần, rồi `/plugin install <tên-skill>@skill-ketoan-tai-chinh`. Cập nhật bản mới: `/plugin marketplace update skill-ketoan-tai-chinh`.

### Claude Code – chép thủ công

```bash
git clone https://github.com/nguyenvansuai/skill-ketoan-tai-chinh.git
mkdir -p ~/.claude/skills && cp -r skill-ketoan-tai-chinh/skills/* ~/.claude/skills/
```

### ChatGPT

Mỗi skill có file hướng dẫn trong [`chatgpt/`](chatgpt): tạo **Project** (hoặc Custom GPT), dán phần **Instructions**, tải các file `references/` lên; bật Code Interpreter để chạy script.

## Văn bản pháp luật dùng trong bộ skill

Bảng đầy đủ, hiệu lực và độ tin cậy (**NV** = đã đối chiếu nguyên văn, **TC** = nguồn thứ cấp): [`shared/van-ban-hieu-luc.md`](shared/van-ban-hieu-luc.md), cập nhật **02/11/2026**.

| Văn bản | Nội dung |
|---|---|
| TT 133/2016/TT-BTC (sửa bởi TT 46/2025) | Chế độ kế toán DNNVV – **vẫn còn hiệu lực** |
| TT 58/2026/TT-BTC | Chế độ kế toán DN siêu nhỏ (thay TT 132/2018), năm tài chính bắt đầu từ/sau 01/07/2026 |
| TT 99/2025/TT-BTC | Chế độ kế toán DN chung (thay TT 200/2014); DNNVV được chọn |
| Luật TNDN 67/2025/QH15; NĐ 320/2025 | Thuế suất 15%/17%/20%, chi phí được trừ, ngưỡng 5 triệu |
| Luật 09/2026/QH16; NĐ 141/2026; NQ 43/2026 | Miễn TNDN ≤1 tỷ; giảm 30% TNDN 2026–2027 (≤10 tỷ) |
| Luật GTGT 48/2024; NĐ 181/2025; NĐ 174/2025 | Khấu trừ, thanh toán không dùng tiền mặt từ 5 triệu, thuế suất 8% đến 31/12/2026 |
| Luật QLT 108/2025; NĐ 252/2026; NĐ 245/2026 | Thời hạn khai, tạm nộp TNDN, gia hạn nộp thuế 2026 |
| NĐ 254/2026; TT 91/2026 | Hóa đơn điện tử, xử lý hóa đơn sai |
| TT 45/2013, TT 48/2019 (QĐ 1760/QĐ-BTC) | Khấu hao, dự phòng – tiếp tục hiệu lực không quá 31/12/2026 |

## Script đi kèm (Python 3)

| Script | Chức năng |
|---|---|
| `skills/che-do-ke-toan/scripts/xac_dinh_quy_mo.py` | Quy mô DN, chế độ kế toán được áp dụng, cờ thuế cần rà |
| `skills/dinh-khoan/scripts/kiem_tra_but_toan.py` | Kiểm tra bút toán theo TT133, Sổ Nhật ký chung + tổng hợp phát sinh |
| `skills/doc-hoa-don-xml/scripts/doc_hoa_don.py` | XML hóa đơn → bảng kê, cảnh báo, gợi ý bút toán |
| `skills/doi-soat/scripts/doi_soat_ngan_hang.py` | Ghép cặp sổ 112 – sao kê, bảng điều chỉnh số dư |
| `skills/doi-soat/scripts/tuoi_no.py` | Tuổi nợ, dự phòng phải thu khó đòi tham khảo |
| `skills/khoa-so-cuoi-ky/scripts/khau_hao.py` | Khấu hao TSCĐ, phân bổ 242 theo ngày |
| `skills/bao-cao-tai-chinh/scripts/lap_bctc.py` | B01a-DNN, B02-DNN, F01-DNN từ bảng cân đối phát sinh |
| `skills/thue-gtgt-dn/scripts/tinh_gtgt.py` | GTGT khấu trừ / trực tiếp |
| `skills/thue-tndn/scripts/tinh_tndn.py` | Quyết toán TNDN, tạm nộp quý |

Mọi script có `--self-test`. Xuất Excel cần `pip install openpyxl`; còn lại chỉ cần Python 3.

## Cấu trúc repo

```
skills/<tên-skill>/SKILL.md        # hướng dẫn chính
skills/<tên-skill>/references/     # tài liệu (bản chép từ shared/ + tài liệu riêng)
skills/<tên-skill>/scripts/        # script hỗ trợ
shared/                            # nguồn gốc tài liệu dùng chung
chatgpt/  dist/  .claude-plugin/   # sinh tự động bởi scripts/build.py
qua-tang/                          # PDF 10 câu lệnh + Excel mẫu sổ (sinh bởi scripts/in_qua_tang_pdf.py, tao_qua_tang_excel.py)
van-ban/                           # văn bản pháp luật gốc (bản chữ)
```

Sửa tài liệu dùng chung ở `shared/` rồi chạy `python3 scripts/build.py --test`.

## Lưu ý pháp lý

Tổng hợp đến 02/11/2026 và **có thể đã thay đổi** (TT133 dự kiến sửa/thay trong 2026–2027; TT45/2013 chỉ hiệu lực đến 31/12/2026; giảm GTGT 8% hết 31/12/2026). Mục **[cần kiểm tra]** chưa đối chiếu văn bản gốc. Skill không thay thế kế toán trưởng, dịch vụ kế toán, kiểm toán hay cơ quan thuế.

## Giấy phép

MIT – xem [LICENSE](LICENSE). Ghi công nguồn kế thừa: [NOTICE.md](NOTICE.md).
