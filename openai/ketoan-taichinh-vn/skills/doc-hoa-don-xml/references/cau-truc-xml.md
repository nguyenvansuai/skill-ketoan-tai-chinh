# Cấu trúc file XML hóa đơn điện tử

> Theo thành phần dữ liệu tại **QĐ 1450/QĐ-TCT (2021)** – nguồn thứ cấp, **[cần kiểm tra]** phiên bản định dạng cập nhật sau NĐ 254/2026 (hiệu lực 01/07/2026). Script đọc theo **tên thẻ**, bỏ qua namespace, nên chịu được khác biệt nhỏ giữa nhà cung cấp.

```
HDon
├── DLHDon                      dữ liệu hóa đơn
│   ├── TTChung                 thông tin chung
│   │   ├── PBan                phiên bản định dạng
│   │   ├── THDon               tên hóa đơn (HÓA ĐƠN GIÁ TRỊ GIA TĂNG / HÓA ĐƠN BÁN HÀNG…)
│   │   ├── KHMSHDon            ký hiệu mẫu số (1 = GTGT, 2 = bán hàng…)
│   │   ├── KHHDon              ký hiệu hóa đơn (vd C26TAA: C = có mã, 26 = năm, T = DN đăng ký, AA = DN tự đặt)
│   │   ├── SHDon               số hóa đơn
│   │   ├── NLap                ngày lập (YYYY-MM-DD)
│   │   ├── DVTTe, TGia         đơn vị tiền tệ, tỷ giá
│   │   └── HTTToan             hình thức thanh toán (TM, CK, TM/CK…)
│   └── NDHDon                  nội dung
│       ├── NBan                người bán: Ten, MST, DChi, STKNHang…
│       ├── NMua                người mua: Ten, MST, DChi, HVTNMHang (họ tên người mua hàng)
│       ├── DSHHDVu / HHDVu     từng dòng hàng: TChat (1 hàng hóa dịch vụ, 2 khuyến mại, 3 chiết khấu thương mại, 4 ghi chú),
│       │                       STT, MHHDVu, THHDVu, DVTinh, SLuong, DGia, TLCKhau, STCKhau, ThTien, TSuat
│       └── TToan               tổng: THTTLTSuat/LTSuat (TSuat, ThTien, TThue), TgTCThue (cộng tiền hàng chưa thuế),
│                               TgTThue (tổng thuế), TTCKTMai (chiết khấu thương mại), TgTTTBSo (tổng thanh toán bằng số), TgTTTBChu
├── DSCKS                       chữ ký số người bán, (người mua), cơ quan thuế – thẻ Signature
└── MCCQT                       mã của cơ quan thuế (chỉ có ở hóa đơn có mã)
```

## Giá trị TSuat thường gặp
`0%`, `5%`, `8%` (giảm GTGT đến 31/12/2026), `10%`, `KCT` (không chịu thuế), `KKKNT` (không kê khai, tính nộp thuế), `KHAC:x%`.

## Kiểm tra trước khi hạch toán, kê khai
1. Hóa đơn có mã: có `MCCQT`; tra trạng thái (hợp lệ / bị thay thế / bị điều chỉnh / hủy) trên **hoadondientu.gdt.gov.vn**.
2. MST người mua đúng MST DN mình; tên, địa chỉ khớp đăng ký thuế.
3. Số học: cộng dòng = TgTCThue; TgTCThue + TgTThue − TTCKTMai = TgTTTBSo.
4. Thuế suất đúng hàng hóa, dịch vụ (8% chỉ cho nhóm được giảm, đến 31/12/2026).
5. Hóa đơn mua vào (hoặc tổng hóa đơn cùng người bán cùng ngày) **từ 5 triệu đồng** → phải có chứng từ thanh toán không dùng tiền mặt để được khấu trừ GTGT (NĐ 181/2025 Đ.26) và tính chi phí được trừ TNDN (NĐ 320/2025).
6. Người bán có rủi ro (bỏ địa chỉ kinh doanh, ngừng hoạt động): tra cứu MST trên tracuunnt.gdt.gov.vn trước khi kê khai khấu trừ.
7. Hóa đơn sai: xử lý điều chỉnh, thay thế theo NĐ 254/2026 và TT 91/2026 – không tự hủy.
