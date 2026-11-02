# Ghi công nguồn kế thừa

Bộ skill viết mới bằng tiếng Việt cho chế độ kế toán, thuế Việt Nam; có kế thừa phương pháp và đối chiếu số liệu từ các nguồn mở sau.

| Nguồn | Giấy phép | Kế thừa gì | Dùng ở |
|---|---|---|---|
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) – plugin `finance` (journal-entry, reconciliation, close-management, financial-statements) | Apache-2.0 | Quy trình định khoản, phân loại chênh lệch đối soát (thời điểm / cần điều chỉnh / cần điều tra), trình tự và phụ thuộc công việc khóa sổ. Viết lại theo TT133, bỏ SOX/hợp nhất | `dinh-khoan`, `doi-soat`, `khoa-so-cuoi-ky`, `bao-cao-tai-chinh` |
| [diginno-net/opc-vn-business-law](https://github.com/diginno-net/opc-vn-business-law) – "Diginno — opc-vn-business-law" | Nội dung CC BY 4.0; script MIT | Kết quả đối chiếu văn bản gốc (TT58/2026, TT133, TT46/2025, Luật TNDN 67/2025, NĐ 320/2025, NĐ 141/2026, NQ 43/2026, NQ 198/2025); nguyên tắc "cổng điều kiện trước phép tính" cho TNDN | `shared/van-ban-hieu-luc.md`, `shared/che-do-ke-toan-dnnvv.md`, `thue-tndn` |
| [tndvnn/tncn](https://github.com/tndvnn/tncn) | MIT | Số liệu TNCN, bảo hiểm, thời hạn khai (Luật 109/2025, NĐ 253/2026, NĐ 252/2026, NĐ 161/2026, NĐ 293/2025, NĐ 125/2020 Đ.13) đã đối chiếu Công báo | `shared/van-ban-hieu-luc.md`, `shared/thue-dn-2026.md` |
| [nguyenvansuai/skill-ho-kinh-doanh](https://github.com/nguyenvansuai/skill-ho-kinh-doanh) | MIT | Cấu trúc repo, `scripts/build.py`, nguyên tắc chung; 5 file toàn văn trong `van-ban/` (lấy từ vbpl.vn ngày 30/10/2026) | Toàn bộ repo, `van-ban/` |

Miễn trừ trách nhiệm của Diginno được giữ nguyên tinh thần: nội dung là thông tin tham khảo, không phải tư vấn pháp lý, thuế, kế toán; không bảo đảm đầy đủ hoặc cập nhật.
