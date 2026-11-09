# Ví dụ bài giảng

Ví dụ thực tế cho người làm **kế toán tổng hợp**: so sánh làm thủ công với dùng plugin, kèm dữ liệu để demo trên lớp.

| Bài | Thư mục | Skill dùng |
|---|---|---|
| Lên số thuế GTGT tháng 10 từ 8 hóa đơn XML | [`thue-gtgt-thang-10/`](thue-gtgt-thang-10/) | `doc-hoa-don-xml`, `thue-gtgt-dn` |

## Mỗi bài gồm

| Thành phần | Nội dung |
|---|---|
| `slide/*.pptx` (+ `.pdf`) | 2 slide: (1) không dùng skill và dùng skill; (2) demo: đầu vào – prompt – kết quả, quy trình đầy đủ khi có connector |
| `dau-vao/` | Tài liệu đầu vào đặt sẵn cho demo (dữ liệu giả lập, cài sẵn lỗi để plugin phát hiện) |
| `prompt.md` | Chuẩn bị trước giờ dạy, prompt demo chép nguyên văn, prompt hỏi tiếp, prompt đầy đủ có connector |
| `ket-qua-mau/` | Kết quả chạy thật bằng công cụ của plugin để giảng viên đối chiếu – câu chữ AI có thể khác, **con số phải giống** |

## Cách dạy gợi ý (15–20 phút)

1. Chiếu slide 1: hỏi học viên đang làm việc này thế nào, mất bao lâu, từng sai chỗ nào.
2. Chiếu slide 2, mở cuộc trò chuyện mới, đính kèm file trong `dau-vao/`, dán prompt demo trong `prompt.md`.
3. Trong lúc AI chạy, giải thích quy trình đầy đủ khi có connector (Gmail, Drive, Calendar...).
4. Đối chiếu kết quả với `ket-qua-mau/`, nhấn mạnh phần **người vẫn phải tự làm**.

Demo không dùng connector (không đọc email, Drive thật) để buổi dạy chạy ổn định; phần connector chỉ giảng trên slide.

## Sửa slide

Nội dung slide nằm trong `slide/noi-dung-slide.json`. Sửa xong dựng lại (cần `pip install python-pptx`):

```bash
python3 example/tao_slide.py example/thue-gtgt-thang-10/slide/noi-dung-slide.json example/thue-gtgt-thang-10/slide/thue-gtgt-thang-10.pptx
```

Toàn bộ tên công ty, người, mã số thuế, mã số BHXH trong ví dụ là **giả lập để học**. Mức phí, quy định dùng trong ví dụ cập nhật đến 11/2026 – đối chiếu lại trước khi áp dụng thật.
