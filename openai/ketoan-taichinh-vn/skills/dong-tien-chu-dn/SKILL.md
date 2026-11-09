---
name: dong-tien-chu-dn
description: Công cụ tài chính quản trị cho chủ doanh nghiệp nhỏ và vừa — dự báo dòng tiền 13 tuần (số dư đầu, các khoản thu theo xác suất, chi lặp lại hằng tuần/tháng, hạn nộp thuế, lương), cảnh báo tuần âm quỹ hoặc dưới mức tối thiểu, kịch bản khách trả trễ; điểm hòa vốn (sản lượng, doanh thu, biên an toàn); so sánh kế hoạch với thực tế, lọc chênh lệch trọng yếu cần giải thích, tách giá – lượng. Dùng khi người dùng hỏi "dự báo dòng tiền", "có đủ tiền trả lương không", "tháng sau có bị thiếu tiền không", "cash flow 13 tuần", "bán bao nhiêu thì hòa vốn", "điểm hòa vốn", "so sánh kế hoạch thực tế", "vì sao lợi nhuận tháng này giảm".
---

# Dòng tiền, hòa vốn, kế hoạch – thực tế

Đọc `references/nguyen-tac-chung.md`. Hạn nộp thuế để đưa vào phần chi: `references/thue-dn-2026.md` (mục 6, 6a) hoặc skill `lich-thue-dn`. Phương pháp phân tích chênh lệch kế thừa `anthropics/knowledge-work-plugins` – finance/variance-analysis (Apache-2.0), rút gọn cho DN nhỏ.

Đây là **quản trị nội bộ**, không phải BCTC nộp cơ quan nhà nước (B03-DNN lập bằng skill `bao-cao-tai-chinh`).

## 1. Dòng tiền 13 tuần

Thu thập: số dư tiền đầu kỳ (tiền mặt + tiền gửi không kỳ hạn); các khoản **thu** (khách hàng, ngày dự kiến, mức chắc chắn %); các khoản **chi** (lương, bảo hiểm, thuê, nhà cung cấp, trả nợ vay, thuế theo lịch); mức tồn quỹ tối thiểu muốn giữ.

CSV `ngay,loai,noi_dung,so_tien,xac_suat,lap_lai` (`loai`: thu/chi; `lap_lai`: trống/tuan/thang):

```bash
python3 scripts/dong_tien.py 13-tuan dong_tien.csv --so-du-dau 350000000 --tu-ngay 2026-11-02 --muc-toi-thieu 100000000 --xlsx dong_tien_13_tuan.xlsx
python3 scripts/dong_tien.py 13-tuan dong_tien.csv --so-du-dau 350000000 --tre-thu 14     # kịch bản khách trả trễ 2 tuần
```

- Luôn chạy thêm kịch bản xấu (`--tre-thu`) khi có tuần sát mức tối thiểu.
- Công nợ phải thu lấy từ skill `doi-soat` (tuổi nợ): khoản quá hạn lâu nên để xác suất thấp.
- Tuần thiếu tiền: gợi ý theo thứ tự – đôn đốc thu nợ quá hạn, giãn chi không bắt buộc, đàm phán nhà cung cấp, hạn mức vay, gia hạn thuế **nếu đủ điều kiện** (NĐ 245/2026 cho năm 2026). Không gợi ý chậm đóng bảo hiểm, chậm nộp thuế ngoài diện gia hạn.

## 2. Điểm hòa vốn

```bash
python3 scripts/dong_tien.py hoa-von --dinh-phi 120000000 --gia-ban 450000 --bien-phi 270000 --san-luong 900
```

Định phí = chi phí không đổi theo sản lượng trong kỳ (thuê, lương cố định, khấu hao, phần mềm). Biến phí đơn vị = giá vốn + phí sàn, thanh toán, vận chuyển, hoa hồng mỗi đơn vị. Giá bán ≤ biến phí → script báo lỗi: mỗi đơn đang lỗ.

## 3. Kế hoạch – thực tế

CSV `khoan,ke_hoach,thuc_te,loai` (`loai`: thu/chi):

```bash
python3 scripts/dong_tien.py so-sanh ke_hoach_thuc_te.csv --nguong-pt 10 --nguong-tien 20000000
```

- Chỉ giải thích khoản **trọng yếu** (vượt cả ngưỡng % và ngưỡng tiền).
- Doanh thu, giá vốn: tách **giá** (giá bán thay đổi × sản lượng thực tế) và **lượng** (sản lượng thay đổi × giá kế hoạch); chi phí: theo nhóm chi phí.
- Mỗi khoản ghi: nguyên nhân, một lần hay lặp lại, việc cần làm. Không đoán nguyên nhân khi thiếu dữ liệu – liệt kê câu hỏi cần hỏi.

## 4. Đầu ra

1. Bảng 13 tuần (Excel, số dư nối tiếp bằng công thức), tuần thấp nhất, tuần cảnh báo; hoặc kết quả hòa vốn; hoặc bảng chênh lệch; "Đã kiểm tra phép tính".
2. 3–5 việc cần làm cụ thể theo thứ tự ưu tiên.
3. Bảng **Cần anh/chị kiểm tra**: giả định xác suất thu, khoản chi thiếu (thuế, bảo hiểm, trả nợ), cách chia định phí – biến phí.
