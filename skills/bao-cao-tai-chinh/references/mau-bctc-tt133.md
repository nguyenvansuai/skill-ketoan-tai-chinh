# Mẫu BCTC TT133/2016 – chỉ tiêu và cách lấy số (bản dùng cho script `lap_bctc.py`)

> Mã số chỉ tiêu B01a-DNN, B02-DNN đã đối chiếu với bài hướng dẫn lập BCTC (nguồn thứ cấp). **Ánh xạ tài khoản → chỉ tiêu** dưới đây là cách lập phổ biến theo hướng dẫn TT133 – **[cần kiểm tra]** với Phụ lục hướng dẫn lập BCTC của TT133 khi DN có nghiệp vụ đặc thù (ngoại tệ, đầu tư, vay dài hạn, quỹ). Ký hiệu: **N(x)** = tổng dư Nợ chi tiết TK x; **C(x)** = tổng dư Có chi tiết TK x; số có (*) ghi âm.

## B01a-DNN – Báo cáo tình hình tài chính

| Mã | Chỉ tiêu | Cách lấy số |
|---|---|---|
| 110 | Tiền và các khoản tương đương tiền | N(111) + N(112) (+ tiền gửi kỳ hạn ≤3 tháng trong 1281 nếu DN xếp là tương đương tiền) |
| 121 | Chứng khoán kinh doanh | N(121) |
| 122 | Đầu tư nắm giữ đến ngày đáo hạn | N(128) |
| 123 | Đầu tư góp vốn vào đơn vị khác | N(228) |
| 124 | Dự phòng tổn thất đầu tư tài chính (*) | −C(2291, 2292) |
| 131 | Phải thu của khách hàng | N(131) chi tiết theo khách |
| 132 | Trả trước cho người bán | N(331) chi tiết theo người bán |
| 133 | Vốn kinh doanh ở đơn vị trực thuộc | N(1361) |
| 134 | Phải thu khác | N(1368, 1386, 1388, 141, 334, 338) |
| 135 | Tài sản thiếu chờ xử lý | N(1381) |
| 136 | Dự phòng phải thu khó đòi (*) | −C(2293) |
| 141 | Hàng tồn kho | N(151–157) |
| 142 | Dự phòng giảm giá hàng tồn kho (*) | −C(2294) |
| 151 / 152 | TSCĐ: nguyên giá / hao mòn lũy kế (*) | N(211) / −C(2141, 2142, 2143) |
| 161 / 162 | BĐS đầu tư: nguyên giá / hao mòn (*) | N(217) / −C(2147) |
| 170 | XDCB dở dang | N(241) |
| 181 | Thuế GTGT được khấu trừ | N(133) |
| 182 | Tài sản khác | N(242) + N(333) (thuế nộp thừa) |
| **200** | **Tổng cộng tài sản** | 110 + 120 + 130 + 140 + 150 + 160 + 170 + 180 |
| 311 | Phải trả người bán | C(331) chi tiết |
| 312 | Người mua trả tiền trước | C(131) chi tiết |
| 313 | Thuế và các khoản phải nộp Nhà nước | C(333) |
| 314 | Phải trả người lao động | C(334) |
| 315 | Phải trả khác | C(335, 3368, 338, 1386, 1388) |
| 316 | Vay và nợ thuê tài chính | C(341) |
| 317 | Phải trả nội bộ về vốn kinh doanh | C(3361) |
| 318 | Dự phòng phải trả | C(352) |
| 319 | Quỹ khen thưởng, phúc lợi | C(353) |
| 320 | Quỹ phát triển KH&CN | C(356) |
| **300** | **Nợ phải trả** | 311 → 320 |
| 411 | Vốn góp của chủ sở hữu | C(4111) |
| 412 | Thặng dư vốn cổ phần | C(4112) − N(4112) |
| 413 | Vốn khác của chủ sở hữu | C(4118) |
| 414 | Cổ phiếu quỹ (*) | −N(419) |
| 415 | Chênh lệch tỷ giá hối đoái | C(413) − N(413) |
| 416 | Các quỹ thuộc vốn chủ sở hữu | C(418) |
| 417 | Lợi nhuận sau thuế chưa phân phối | C(421) − N(421) (+ LNST năm nay nếu số liệu trước kết chuyển) |
| **400** | **Vốn chủ sở hữu** | 411 → 417 |
| **500** | **Tổng cộng nguồn vốn** | 300 + 400 = **200** |

Nguyên tắc: **không bù trừ** dư Nợ và dư Có của tài khoản công nợ – lấy theo từng đối tượng chi tiết.

## B02-DNN – Báo cáo kết quả hoạt động kinh doanh (lấy từ phát sinh trước kết chuyển)

| Mã | Chỉ tiêu | Cách lấy số |
|---|---|---|
| 01 | Doanh thu bán hàng và cung cấp dịch vụ | PS Có 511 (doanh thu gộp) |
| 02 | Các khoản giảm trừ doanh thu | PS Nợ 511 đối ứng 111, 112, 131 (chiết khấu thương mại, giảm giá, hàng bán bị trả lại) |
| 10 | Doanh thu thuần | 01 − 02 |
| 11 | Giá vốn hàng bán | PS Nợ 632 − PS Có 632 (không tính kết chuyển) |
| 20 | Lợi nhuận gộp | 10 − 11 |
| 21 | Doanh thu hoạt động tài chính | PS Có 515 ròng |
| 22 / 23 | Chi phí tài chính / trong đó lãi vay | PS Nợ 635 ròng / phần lãi vay |
| 24 | Chi phí quản lý kinh doanh | PS Nợ 642 ròng (6421 + 6422) |
| 30 | Lợi nhuận thuần từ HĐKD | 20 + 21 − 22 − 24 |
| 31 / 32 | Thu nhập khác / Chi phí khác | PS Có 711 ròng / PS Nợ 811 ròng |
| 40 | Lợi nhuận khác | 31 − 32 |
| 50 | Tổng lợi nhuận kế toán trước thuế | 30 + 40 |
| 51 | Chi phí thuế TNDN | PS Nợ 821 ròng |
| 60 | Lợi nhuận sau thuế | 50 − 51 |

## Bộ BCTC năm của DNNVV theo TT133

B01a-DNN (hoặc B01b-DNN nếu không đáp ứng giả định hoạt động liên tục), B02-DNN, B09-DNN (thuyết minh), F01-DNN (bảng cân đối tài khoản gửi cơ quan thuế); B03-DNN (lưu chuyển tiền tệ) – [cần kiểm tra mức bắt buộc]. DN siêu nhỏ áp dụng TT58: B01-DNSN, B02-DNSN (chỉ tiêu riêng – không dùng script này).

Hạn nộp: 90 ngày kể từ kết thúc năm tài chính, cùng hồ sơ quyết toán TNDN trên eTax.

## Thuyết minh B09-DNN – nội dung tối thiểu nên có
1. Đặc điểm hoạt động: hình thức sở hữu, lĩnh vực, ngành nghề, kỳ kế toán, đơn vị tiền tệ.
2. Chế độ kế toán áp dụng (TT133/2016), chính sách kế toán: ghi nhận doanh thu, phương pháp hàng tồn kho, khấu hao TSCĐ, dự phòng.
3. Thông tin bổ sung cho các khoản mục B01a, B02 (chi tiết tiền, phải thu, hàng tồn kho, TSCĐ tăng giảm, vay, thuế phải nộp, vốn chủ sở hữu).
4. Thông tin khác: sự kiện sau ngày kết thúc kỳ, bên liên quan, khả năng hoạt động liên tục.
