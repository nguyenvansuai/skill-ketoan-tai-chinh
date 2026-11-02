# Chế độ kế toán cho doanh nghiệp nhỏ, vừa và siêu nhỏ

> Cập nhật 02/11/2026. Nguồn và độ tin cậy: `van-ban-hieu-luc.md`. Hệ thống tài khoản dạng máy đọc: `tai-khoan-tt133.csv`.

## 1. Xác định quy mô (NĐ 80/2021/NĐ-CP Điều 5) – [cần kiểm tra ngưỡng với văn bản hiện hành]

Lao động = số lao động **tham gia BHXH bình quân năm**. Thỏa tiêu chí lao động **và** một trong hai tiêu chí doanh thu năm hoặc tổng nguồn vốn.

| Lĩnh vực | Siêu nhỏ | Nhỏ | Vừa |
|---|---|---|---|
| Nông, lâm, thủy sản; công nghiệp, xây dựng | ≤10 lao động; doanh thu ≤3 tỷ **hoặc** nguồn vốn ≤3 tỷ | ≤100 lao động; doanh thu ≤50 tỷ hoặc nguồn vốn ≤20 tỷ | ≤200 lao động; doanh thu ≤200 tỷ hoặc nguồn vốn ≤100 tỷ |
| Thương mại, dịch vụ | ≤10 lao động; doanh thu ≤10 tỷ **hoặc** nguồn vốn ≤3 tỷ | ≤50 lao động; doanh thu ≤100 tỷ hoặc nguồn vốn ≤50 tỷ | ≤100 lao động; doanh thu ≤300 tỷ hoặc nguồn vốn ≤100 tỷ |

Quy mô kế toán (NĐ 80) và ngưỡng thuế (miễn TNDN ≤1 tỷ, thuế suất 15%/17%, giảm 30% ≤10 tỷ) là **hai phép kiểm khác nhau**. Script: `che-do-ke-toan/scripts/xac_dinh_quy_mo.py`.

## 2. Chọn chế độ kế toán

| Chế độ | Ai áp dụng | Ghi chú |
|---|---|---|
| **TT 133/2016** | DNNVV (kể cả siêu nhỏ nếu muốn chế độ đầy đủ); loại trừ DNNN, DN Nhà nước sở hữu >50%, công ty đại chúng, HTX (TT133 Đ.2) | Còn hiệu lực. Bộ Tài chính có kế hoạch sửa/thay trong 2026–2027 (TC) |
| **TT 58/2026** | DN siêu nhỏ (tự nguyện); hộ, cá nhân kinh doanh có nhu cầu | Áp dụng **năm tài chính bắt đầu từ/sau 01/07/2026** (Đ.12). DN năm dương lịch: theo câu chữ, năm 2027 mới đổi – đây là suy luận về kỳ, hỏi người hành nghề trước khi đổi sổ |
| **TT 99/2025** | Mọi DN; DNNVV **được lựa chọn** (Đ.31 k.3) | Phải nhất quán tối thiểu 1 kỳ kế toán năm |

Quy tắc chung:
- Chế độ áp dụng nhất quán cả năm tài chính; đổi chế độ chỉ từ **đầu năm tài chính tiếp theo**.
- DN siêu nhỏ vượt ngưỡng trong năm: dùng tiếp TT58 đến hết năm, năm sau chuyển chế độ phù hợp.
- **Không hạch toán đan xen** TT58 và TT133 trong cùng năm.
- TT58 **không tạo quyền chọn phương pháp thuế**: phương pháp thuế GTGT, TNDN phải đủ điều kiện theo luật thuế, không suy từ mẫu sổ.
- DN tự sửa mẫu chứng từ, sổ, tài khoản, chỉ tiêu BCTC: phải ban hành quy chế hạch toán (TT133 Đ.10 được thay bởi TT 46/2025).

## 3. TT 58/2026 – DN siêu nhỏ: sổ theo phương pháp nộp thuế (Đ.5–8, TC)

| Nhóm | Thuế GTGT | Thuế TNDN | Sổ kế toán | BCTC |
|---|---|---|---|---|
| 1 (Đ.5) | Tỷ lệ % trên doanh thu | Tỷ lệ % trên doanh thu | S1-DNSN Sổ doanh thu bán hàng hóa, dịch vụ | Không bắt buộc lập để nộp cơ quan nhà nước |
| 2 (Đ.6) | Tỷ lệ % trên doanh thu | Thu nhập tính thuế | S2a-DNSN doanh thu; S2b-DNSN chi tiết doanh thu, chi phí; S2c-DNSN vật liệu, dụng cụ, hàng hóa; S2d-DNSN chi tiết tiền | Bắt buộc |
| 3 (Đ.7) | Khấu trừ | Tỷ lệ % trên doanh thu | S3a-DNSN doanh thu; S3b-DNSN theo dõi nghĩa vụ thuế GTGT | Không bắt buộc lập để nộp |
| 4 (Đ.8) | Khấu trừ | Thu nhập tính thuế | S2b, S2c, S2d-DNSN + S3b-DNSN | Bắt buộc |

- BCTC DN siêu nhỏ (Đ.10, TC): **B01-DNSN** Báo cáo tình hình tài chính; **B02-DNSN** Báo cáo kết quả hoạt động kinh doanh. Nộp trong **90 ngày** kể từ kết thúc năm tài chính (năm dương lịch: 31/03 năm sau). Nhóm TNDN theo % doanh thu vẫn lập BCTC nếu tự chọn sổ của Đ.6, Đ.8 để quản trị – lưu tại DN, cung cấp khi được yêu cầu.
- Không bắt buộc kế toán trưởng; được bố trí người thân của người đại diện, người quản lý, thủ kho, thủ quỹ làm kế toán, hoặc thuê dịch vụ (NĐ 174/2016 Đ.20; TT58 Đ.3).
- Chuyển số dư từ TT132 sang TT58: TT58 Đ.11 (NV).

## 4. TT 133/2016 – hệ thống tài khoản

Tính chất: **Nợ** = thường dư Nợ; **Có** = thường dư Có (214, 229 là tài khoản điều chỉnh giảm tài sản); **Lưỡng tính** = theo dõi chi tiết từng đối tượng, có thể dư cả hai bên (131, 331, 138, 338, 413, 421); **Không số dư** = loại 5–9, kết chuyển hết về 911 cuối kỳ.

| Số hiệu | Tên | Tài khoản cấp 2 |
|---|---|---|
| **Loại 1–2: Tài sản** | | |
| 111 | Tiền mặt | 1111 Tiền Việt Nam; 1112 Ngoại tệ |
| 112 | Tiền gửi ngân hàng | 1121 Tiền Việt Nam; 1122 Ngoại tệ |
| 121 | Chứng khoán kinh doanh | |
| 128 | Đầu tư nắm giữ đến ngày đáo hạn | 1281 Tiền gửi có kỳ hạn; 1288 Đầu tư khác |
| 131 | Phải thu của khách hàng | |
| 133 | Thuế GTGT được khấu trừ | 1331 Hàng hóa, dịch vụ; 1332 TSCĐ |
| 136 | Phải thu nội bộ | 1361 Vốn kinh doanh ở đơn vị trực thuộc; 1368 Khác |
| 138 | Phải thu khác | 1381 Tài sản thiếu chờ xử lý; 1386 Cầm cố, thế chấp, ký quỹ, ký cược; 1388 Phải thu khác |
| 141 | Tạm ứng | |
| 151–157 | Hàng mua đang đi đường (151); Nguyên liệu, vật liệu (152); Công cụ, dụng cụ (153); Chi phí SXKD dở dang (154); Thành phẩm (155); Hàng hóa (156); Hàng gửi đi bán (157) | |
| 211 | Tài sản cố định | 2111 Hữu hình; 2112 Thuê tài chính; 2113 Vô hình |
| 214 | Hao mòn TSCĐ | 2141, 2142, 2143; 2147 Hao mòn BĐS đầu tư |
| 217 | Bất động sản đầu tư | |
| 228 | Đầu tư góp vốn vào đơn vị khác | 2281 Liên doanh, liên kết; 2288 Khác |
| 229 | Dự phòng tổn thất tài sản | 2291 Chứng khoán KD; 2292 Đầu tư vào đơn vị khác; 2293 Phải thu khó đòi; 2294 Giảm giá hàng tồn kho |
| 241 | Xây dựng cơ bản dở dang | 2411 Mua sắm TSCĐ; 2412 XDCB; 2413 Sửa chữa lớn TSCĐ |
| 242 | Chi phí trả trước | |
| **Loại 3: Nợ phải trả** | | |
| 331 | Phải trả cho người bán | |
| 333 | Thuế và các khoản phải nộp Nhà nước | 3331 GTGT phải nộp (33311 đầu ra; 33312 hàng nhập khẩu); 3332 TTĐB; 3333 XNK; 3334 TNDN; 3335 TNCN; 3336 Tài nguyên; 3337 Nhà đất, tiền thuê đất; 3338 BVMT và thuế khác (33381, 33382); 3339 Phí, lệ phí, khoản phải nộp khác |
| 334 | Phải trả người lao động | |
| 335 | Chi phí phải trả | |
| 336 | Phải trả nội bộ | 3361 Về vốn kinh doanh; 3368 Khác |
| 338 | Phải trả, phải nộp khác | 3381 Tài sản thừa; 3382 KPCĐ; 3383 BHXH; 3384 BHYT; 3385 BHTN; 3386 Nhận ký quỹ, ký cược; 3387 Doanh thu chưa thực hiện; 3388 Khác |
| 341 | Vay và nợ thuê tài chính | 3411 Các khoản đi vay; 3412 Nợ thuê tài chính |
| 352 | Dự phòng phải trả | 3521 Bảo hành sản phẩm; 3522 Bảo hành công trình; 3524 Khác |
| 353 | Quỹ khen thưởng, phúc lợi | 3531, 3532, 3533, 3534 |
| 356 | Quỹ phát triển KH&CN | 3561, 3562 |
| **Loại 4: Vốn chủ sở hữu** | | |
| 411 | Vốn đầu tư của chủ sở hữu | 4111 Vốn góp; 4112 Thặng dư vốn cổ phần; 4118 Vốn khác |
| 413 | Chênh lệch tỷ giá hối đoái | |
| 418 | Các quỹ thuộc vốn chủ sở hữu | |
| 419 | Cổ phiếu quỹ | |
| 421 | Lợi nhuận sau thuế chưa phân phối | 4211 Năm trước; 4212 Năm nay |
| **Loại 5: Doanh thu** | | |
| 511 | Doanh thu bán hàng và cung cấp dịch vụ | 5111 Hàng hóa; 5112 Thành phẩm; 5113 Dịch vụ; 5118 Khác |
| 515 | Doanh thu hoạt động tài chính | |
| **Loại 6: Chi phí SXKD** | | |
| 611 | Mua hàng (kiểm kê định kỳ) | |
| 631 | Giá thành sản xuất (kiểm kê định kỳ) | |
| 632 | Giá vốn hàng bán | |
| 635 | Chi phí tài chính | |
| 642 | Chi phí quản lý kinh doanh | **6421 Chi phí bán hàng; 6422 Chi phí quản lý doanh nghiệp** |
| **Loại 7–9** | | |
| 711 | Thu nhập khác | |
| 811 | Chi phí khác | |
| 821 | Chi phí thuế TNDN | |
| 911 | Xác định kết quả kinh doanh | |

### Khác biệt hay nhầm khi quen TT200/TT99

- TT133 **không có TK 521**: chiết khấu thương mại, giảm giá, hàng bán bị trả lại ghi **Nợ 511** trực tiếp (theo dõi chi tiết để lên chỉ tiêu 02 – Các khoản giảm trừ doanh thu).
- TT133 **không tách 641/642**: dùng 642 với 6421 (bán hàng) và 6422 (quản lý DN).
- TT133 không có tài khoản thuế TNDN hoãn lại (243, 347), không có 161, 466, 344 (ký quỹ nhận dùng 3386; ký quỹ đi dùng 1386), không có 113 tiền đang chuyển.
- Không có tài khoản ngoài bảng (loại 0) trong danh mục TT133 [cần kiểm tra khi DN cần theo dõi hàng giữ hộ].

## 5. Báo cáo tài chính theo TT133

| Mẫu | Tên | Ghi chú |
|---|---|---|
| B01a-DNN | Báo cáo tình hình tài chính | DN đáp ứng giả định hoạt động liên tục |
| B01b-DNN | Báo cáo tình hình tài chính | DN không đáp ứng giả định hoạt động liên tục |
| B02-DNN | Báo cáo kết quả hoạt động kinh doanh | |
| B03-DNN | Báo cáo lưu chuyển tiền tệ | Khuyến khích lập với DNNVV [cần kiểm tra mức bắt buộc] |
| B09-DNN | Bản thuyết minh BCTC | |
| F01-DNN | Bảng cân đối tài khoản | Phụ biểu gửi cơ quan thuế |

Hạn nộp BCTC năm: **90 ngày** kể từ kết thúc năm tài chính (năm dương lịch: 31/03 năm sau), nộp kèm quyết toán TNDN trên eTax. Lưu trữ BCTC tối thiểu 10 năm.

Chỉ tiêu chính – xem chi tiết và cách lấy số trong `bao-cao-tai-chinh/references/mau-bctc-tt133.md`.

## 6. Sổ kế toán TT133

Hình thức: Nhật ký chung (phổ biến nhất), Nhật ký – Sổ Cái, Chứng từ ghi sổ, hoặc trên máy vi tính. Bộ tối thiểu với hình thức Nhật ký chung: Sổ Nhật ký chung (S03a-DNN), Sổ Cái (S03b-DNN), sổ/thẻ chi tiết (quỹ tiền mặt, tiền gửi, vật tư hàng hóa, TSCĐ, công nợ, doanh thu, chi phí) [cần kiểm tra mã mẫu sổ chi tiết].
