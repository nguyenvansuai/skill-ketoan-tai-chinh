# Checklist khóa sổ cuối kỳ – DN nhỏ và vừa (TT133)

> Kế thừa trình tự và phụ thuộc công việc từ `anthropics/knowledge-work-plugins` – finance/close-management (Apache-2.0), rút gọn cho DNNVV Việt Nam: bỏ hợp nhất, SOX; thêm nghĩa vụ thuế Việt Nam.

## A. Hằng tháng (T+1 → T+5 ngày làm việc)

**Mức 1 – không phụ thuộc, làm ngay T+1**
- [ ] Nhập đủ chứng từ thu, chi, ngân hàng đến ngày cuối tháng.
- [ ] Tải và nhập hóa đơn đầu vào, đầu ra của tháng (XML) → skill `doc-hoa-don-xml`.
- [ ] Tính lương, bảo hiểm, thuế TNCN khấu trừ → skill `luong-bao-hiem`.
- [ ] Khấu hao TSCĐ, phân bổ 242 → `scripts/khau_hao.py`.
- [ ] Trích trước chi phí đã phát sinh chưa có hóa đơn (điện, nước, dịch vụ cuối tháng): Nợ 6421/6422 / Có 335 – có cơ sở ước tính, hoàn nhập khi có hóa đơn.

**Mức 2 – sau mức 1**
- [ ] Đối chiếu ngân hàng TK 112 về chênh lệch 0 → skill `doi-soat`.
- [ ] Kiểm kê quỹ tiền mặt TK 111.
- [ ] Đối chiếu công nợ 131, 331 với sổ chi tiết; khách hàng dư Có, người bán dư Nợ ghi nhận đúng.
- [ ] Nhập – xuất – tồn kho: giá vốn 632 khớp số lượng xuất bán; tồn kho âm = lỗi.
- [ ] Đánh giá lại số dư ngoại tệ (nếu có): chênh lệch qua 413 → 515/635.

**Mức 3 – sau mức 2**
- [ ] Khấu trừ thuế GTGT: Nợ 33311 / Có 133 (số nhỏ hơn). Chuẩn bị số liệu tờ khai → skill `thue-gtgt-dn`.
- [ ] Thuế nhà thầu phát sinh trong tháng đã khấu trừ, khai → skill `thue-nha-thau`.
- [ ] Lập bảng cân đối số phát sinh (trước kết chuyển): tổng Nợ = tổng Có; tài khoản tài sản không dư Có bất thường (111, 112, 156 âm).

**Mức 4 – kết quả**
- [ ] Kết chuyển doanh thu, chi phí về 911; lãi/lỗ về 4212. Tài khoản loại 5–9 hết số dư.
- [ ] So sánh với tháng trước, kế hoạch: biến động lớn (>10% và > mức trọng yếu tự đặt) phải giải thích được (phân tích giá–lượng, theo khoản mục).
- [ ] Khóa sổ trên phần mềm; lưu chứng từ điện tử.

## B. Thêm vào cuối quý
- [ ] Tờ khai GTGT, TNCN khấu trừ theo quý (hạn ngày cuối tháng đầu quý sau).
- [ ] Ước tính TNDN tạm nộp quý (lũy kế 4 quý phải ≥80% số quyết toán) → skill `thue-tndn`.
- [ ] Rà hóa đơn từ 5 triệu chưa có chứng từ chuyển khoản – thanh toán bổ sung nếu còn kịp, nếu không loại khỏi khấu trừ/chi phí.

## C. Thêm vào cuối năm
- [ ] Kiểm kê hàng tồn kho, TSCĐ, quỹ; xử lý thừa thiếu (3381/1381).
- [ ] Biên bản đối chiếu công nợ với khách hàng, nhà cung cấp lớn; đối chiếu số dư vay với ngân hàng.
- [ ] Trích lập dự phòng (giảm giá hàng tồn kho 2294, phải thu khó đòi 2293) khi đủ hồ sơ [cần kiểm tra văn bản sau 31/12/2026].
- [ ] Phân loại lại công nợ ngắn hạn/dài hạn nếu thuyết minh cần.
- [ ] Xác định chi phí không được trừ khi tính TNDN (tiền mặt từ 5 triệu, lương chủ DNTN/TNHH MTV cá nhân, phạt, không hóa đơn) → skill `thue-tndn`.
- [ ] Ghi nhận chi phí thuế TNDN năm: Nợ 821 / Có 3334 (điều chỉnh theo số quyết toán).
- [ ] Kết chuyển 911 → 4212; lập BCTC (B01a-DNN, B02-DNN, B09-DNN, F01-DNN; B03-DNN nếu lập) → skill `bao-cao-tai-chinh`.
- [ ] Quyết toán TNDN, TNCN, nộp BCTC: hạn ngày cuối tháng thứ 3 sau năm (31/03).
- [ ] Đầu năm sau: kết chuyển 4212 → 4211; mở sổ mới; xem có cần đổi chế độ kế toán (TT58/TT99) từ đầu năm tài chính mới.

## D. Dấu hiệu sổ có vấn đề
- Tiền mặt, tiền gửi, hàng tồn kho số dư âm.
- 131 tổng hợp dư Có lớn bất thường, 331 dư Nợ lớn (có thể ghi nhầm bên).
- 133 dư Nợ tăng liên tục nhiều kỳ (khấu trừ không hết – xem lại có hoàn thuế hay ghi sai).
- 242 không giảm qua các tháng (quên phân bổ); 141 tạm ứng tồn lâu không quyết toán.
- Lợi nhuận kế toán và thu nhập tính thuế chênh lớn mà không giải thích được.
