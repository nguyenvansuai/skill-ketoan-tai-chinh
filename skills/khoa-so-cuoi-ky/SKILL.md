---
name: khoa-so-cuoi-ky
description: Lập kế hoạch và thực hiện khóa sổ kế toán cuối tháng, cuối quý, cuối năm cho doanh nghiệp nhỏ và vừa theo TT133 — checklist có thứ tự công việc, tính khấu hao TSCĐ theo ngày (đường thẳng) và phân bổ chi phí trả trước 242 ra bút toán, trích trước 335, khấu trừ thuế GTGT, kết chuyển 911, kiểm tra tài khoản số dư âm, việc phải làm trước quyết toán năm. Dùng khi người dùng nói "khóa sổ", "chốt sổ cuối tháng", "cuối năm cần làm gì", "tính khấu hao", "bảng khấu hao TSCĐ", "phân bổ chi phí trả trước", "phân bổ công cụ dụng cụ", "kết chuyển lãi lỗ", "month-end close".
---

# Khóa sổ cuối kỳ

Đọc `references/nguyen-tac-chung.md`, `references/checklist-khoa-so.md`, `references/che-do-ke-toan-dnnvv.md`; thuế ở `references/thue-dn-2026.md`.

## 1. Xác định

Kỳ khóa sổ (tháng/quý/năm), chế độ kế toán (TT133 mặc định), phần mềm đang dùng (MISA, Fast, Excel…), đã làm tới bước nào. Người dùng chỉ cần một phần (vd chỉ khấu hao) → làm phần đó.

## 2. Checklist

Trả về checklist theo `references/checklist-khoa-so.md` (mục A + B nếu cuối quý + C nếu cuối năm), giữ thứ tự **mức 1 → mức 4** vì có phụ thuộc. Đánh dấu việc nào skill khác làm được (`doc-hoa-don-xml`, `doi-soat`, `luong-bao-hiem`, `thue-gtgt-dn`, `thue-tndn`, `bao-cao-tai-chinh`).

## 3. Khấu hao, phân bổ

CSV `ma,ten,nguyen_gia,ngay_bat_dau,so_thang,bo_phan[,luy_ke_dau]` (bo_phan = 6421/6422/154):

```bash
python3 scripts/khau_hao.py tscd.csv --ky 2026-10 --xlsx khau_hao_10_2026.xlsx
python3 scripts/khau_hao.py tra_truoc.csv --ky 2026-10 --loai 242
python3 scripts/khau_hao.py tscd_vo_hinh.csv --ky 2026-10 --tk-co 2143
```

- Đường thẳng, tháng đầu/cuối theo số ngày sử dụng thực tế (TT 45/2013). TT 45/2013 chỉ tiếp tục hiệu lực **không quá 31/12/2026** → từ kỳ 2027 nhắc kiểm tra văn bản thay thế.
- Nguyên giá dưới 30 triệu → không phải TSCĐ, chuyển 153/242 [cần kiểm tra]. Thời gian khấu hao phải trong khung Phụ lục I TT 45/2013 để được trừ khi tính TNDN.

## 4. Kết chuyển

Lập bút toán kết chuyển theo mục 7 của `but-toan-mau` (skill `dinh-khoan`): 511/515/711 → 911; 911 → 632/635/6421/6422/811/821; lãi 911 → 4212, lỗ 4212 → 911. Cuối năm: ghi nhận 821/3334 theo số TNDN ước tính trước khi kết chuyển.

## 5. Đầu ra

1. Checklist có trạng thái (✅ xong / ⬜ chưa / ⚠️ cần xử lý) + bút toán khấu hao, phân bổ, kết chuyển; "Đã kiểm tra phép tính".
2. Bảng **Cần anh/chị kiểm tra**: tài khoản dư bất thường (mục D checklist), khoản trích trước thiếu cơ sở, tài sản khấu hao ngoài khung.
3. Bước tiếp: `bao-cao-tai-chinh` (cuối năm) hoặc `thue-gtgt-dn` (cuối tháng/quý).
