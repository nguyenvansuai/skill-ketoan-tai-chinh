#!/usr/bin/env python3
"""Tính thuế nhà thầu nước ngoài (GTGT + TNDN) theo phương pháp trực tiếp – bên Việt Nam khấu trừ, khai, nộp thay.

Tỷ lệ (nguồn thứ cấp – [cần kiểm tra] trước khi khai):
  GTGT trên doanh thu – TT 69/2025/TT-BTC Đ.9: hàng hóa 1%; dịch vụ, cho thuê máy móc thiết bị, xây lắp không bao thầu
    vật tư 5%; sản xuất, vận tải, dịch vụ gắn với hàng hóa, xây lắp có bao thầu vật tư 3%; khác 2%.
  TNDN trên doanh thu – NĐ 320/2025 Đ.12 + TT 20/2026: hàng hóa 1%; dịch vụ 5%; quản lý nhà hàng, khách sạn, casino 10%;
    dịch vụ gắn với hàng hóa 2%; lãi tiền vay 5%; bản quyền 10%; cho thuê máy móc thiết bị 5%; cho thuê máy bay, tàu biển 2%;
    xây lắp 2%; vận chuyển 2%; chuyển nhượng chứng khoán, tái bảo hiểm 0,1%; khác 2%.
Lãi tiền vay: thường thuộc diện không chịu GTGT. Bản quyền, chuyển giao công nghệ, phần mềm: phải xác định có chịu GTGT không
→ script bắt nhập --gtgt (kct hoặc tỷ lệ).

Hợp đồng giá NET (bên VN chịu thuế thay) – quy đổi phổ biến [cần kiểm tra TT 20/2026]:
  DT tính TNDN = giá net ÷ (1 − tỷ lệ TNDN);  DT tính GTGT = DT tính TNDN ÷ (1 − tỷ lệ GTGT)
Hợp đồng giá GROSS (đã gồm thuế, bên VN khấu trừ khi trả):
  GTGT = giá gross × tỷ lệ GTGT;  TNDN = (giá gross − GTGT) × tỷ lệ TNDN;  trả nhà thầu = gross − GTGT − TNDN

  python3 tinh_thue_nha_thau.py --hoat-dong dich-vu --gia 100000000 --loai net
  python3 tinh_thue_nha_thau.py --hoat-dong ban-quyen --gia 50000000 --loai gross --gtgt kct
  python3 tinh_thue_nha_thau.py --hoat-dong dich-vu --gia 2000 --ngoai-te USD --ty-gia 25400 --loai net
"""
import argparse
import json
import sys

# hoạt động: (tỷ lệ GTGT | "kct" | None = bắt nhập, tỷ lệ TNDN, mô tả)
BANG = {
    "hang-hoa": (0.01, 0.01, "Cung cấp hàng hóa tại Việt Nam (kèm dịch vụ trong giá trị hàng hóa)"),
    "dich-vu": (0.05, 0.05, "Dịch vụ (tư vấn, phần mềm dịch vụ, quảng cáo, đào tạo, cloud…)"),
    "dich-vu-gan-hang-hoa": (0.03, 0.02, "Dịch vụ gắn với hàng hóa (lắp đặt, bảo hành kèm hàng)"),
    "nha-hang-khach-san": (0.05, 0.10, "Quản lý nhà hàng, khách sạn, casino"),
    "lai-vay": ("kct", 0.05, "Lãi tiền vay từ bên nước ngoài"),
    "ban-quyen": (None, 0.10, "Tiền bản quyền, chuyển giao công nghệ, quyền sử dụng phần mềm"),
    "cho-thue-may-moc": (0.05, 0.05, "Cho thuê máy móc, thiết bị, phương tiện vận tải (trừ máy bay, tàu biển)"),
    "cho-thue-may-bay-tau-bien": (0.05, 0.02, "Cho thuê máy bay, động cơ, tàu biển"),
    "xay-lap-khong-vat-tu": (0.05, 0.02, "Xây dựng, lắp đặt không bao thầu nguyên vật liệu"),
    "xay-lap-co-vat-tu": (0.03, 0.02, "Xây dựng, lắp đặt có bao thầu nguyên vật liệu"),
    "van-chuyen": (0.03, 0.02, "Vận chuyển"),
    "khac": (0.02, 0.02, "Hoạt động kinh doanh khác"),
}


def d(x):
    return f"{x:,.0f}".replace(",", ".")


def pt(x):
    return f"{x * 100:g}%".replace(".", ",")


def doc_gtgt(hd, gtgt):
    mac_dinh = BANG[hd][0]
    if gtgt is None:
        if mac_dinh is None:
            raise ValueError(f"Hoạt động {hd}: phải xác định có chịu GTGT không → nhập --gtgt kct hoặc --gtgt 0.05")
        return 0.0 if mac_dinh == "kct" else mac_dinh
    if str(gtgt).lower() == "kct":
        return 0.0
    v = float(gtgt)
    if not 0 <= v < 1:
        raise ValueError("--gtgt là số thập phân trong [0; 1), vd 0.05, hoặc kct")
    return v


def tinh(hd, gia, loai, gtgt=None, tndn=None):
    if hd not in BANG:
        raise ValueError(f"hoạt động không hợp lệ; chọn: {', '.join(BANG)}")
    if gia <= 0:
        raise ValueError("giá hợp đồng phải > 0")
    t_g = doc_gtgt(hd, gtgt)
    t_t = BANG[hd][1] if tndn is None else tndn
    if not 0 < t_t < 1:
        raise ValueError("--tndn là số thập phân trong (0; 1)")
    if loai == "net":
        dt_tndn = gia / (1 - t_t)
        dt_gtgt = dt_tndn / (1 - t_g) if t_g else dt_tndn
        thue_gtgt, thue_tndn = round(dt_gtgt * t_g), round(dt_tndn * t_t)
        tra_nha_thau = gia
    elif loai == "gross":
        dt_gtgt = gia
        thue_gtgt = round(gia * t_g)
        dt_tndn = gia - thue_gtgt
        thue_tndn = round(dt_tndn * t_t)
        tra_nha_thau = gia - thue_gtgt - thue_tndn
    else:
        raise ValueError("--loai phải là net hoặc gross")
    return {"hoat_dong": hd, "mo_ta": BANG[hd][2], "loai": loai, "gia_hop_dong": gia, "ty_le_gtgt": t_g, "ty_le_tndn": t_t,
            "dt_tinh_gtgt": round(dt_gtgt), "dt_tinh_tndn": round(dt_tndn), "thue_gtgt": thue_gtgt, "thue_tndn": thue_tndn,
            "tong_thue": thue_gtgt + thue_tndn, "tra_nha_thau": round(tra_nha_thau),
            "tong_chi_phi_dn": round(tra_nha_thau + thue_gtgt + thue_tndn)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hoat-dong", choices=list(BANG))
    ap.add_argument("--gia", type=float, help="giá trị thanh toán lần này theo hợp đồng")
    ap.add_argument("--loai", choices=["net", "gross"], help="net: giá chưa gồm thuế (bên VN chịu thuế); gross: đã gồm thuế")
    ap.add_argument("--ngoai-te", help="mã ngoại tệ nếu --gia là ngoại tệ")
    ap.add_argument("--ty-gia", type=float, help="tỷ giá quy đổi sang đồng [cần kiểm tra loại tỷ giá áp dụng]")
    ap.add_argument("--gtgt", help="ghi đè tỷ lệ GTGT (thập phân) hoặc kct")
    ap.add_argument("--tndn", type=float, help="ghi đè tỷ lệ TNDN (thập phân), vd theo hiệp định thuế")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not (a.hoat_dong and a.gia and a.loai):
        ap.error("cần --hoat-dong, --gia, --loai")
    gia = a.gia
    if a.ngoai_te:
        if not a.ty_gia:
            ap.error("hợp đồng ngoại tệ cần --ty-gia")
        gia = a.gia * a.ty_gia
    try:
        kq = tinh(a.hoat_dong, gia, a.loai, a.gtgt, a.tndn)
    except ValueError as e:
        print("✗ " + str(e))
        return 2
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
        return 0
    print(f"THUẾ NHÀ THẦU NƯỚC NGOÀI – {kq['mo_ta']} – hợp đồng giá {kq['loai'].upper()}")
    if a.ngoai_te:
        print(f"  Quy đổi: {a.gia:g} {a.ngoai_te} × {d(a.ty_gia)} = {d(gia)} đồng")
    print(f"  Giá trị thanh toán theo hợp đồng           {d(kq['gia_hop_dong']):>16}")
    print(f"  Doanh thu tính thuế GTGT                   {d(kq['dt_tinh_gtgt']):>16}  × {pt(kq['ty_le_gtgt'])}")
    print(f"  → Thuế GTGT nhà thầu                       {d(kq['thue_gtgt']):>16}")
    print(f"  Doanh thu tính thuế TNDN                   {d(kq['dt_tinh_tndn']):>16}  × {pt(kq['ty_le_tndn'])}")
    print(f"  → Thuế TNDN nhà thầu                       {d(kq['thue_tndn']):>16}")
    print(f"  Chuyển cho nhà thầu                        {d(kq['tra_nha_thau']):>16}")
    print(f"  Tổng tiền DN chi ra (gồm thuế nộp thay)    {d(kq['tong_chi_phi_dn']):>16}")
    print("\nBút toán gợi ý [cần kiểm tra tài khoản chi tiết DN dùng]:")
    gia_von = kq["tra_nha_thau"] + kq["thue_tndn"]
    print(f"  Nợ 6421/6422/242/211 {d(gia_von):>14} / Có 331 (nhà thầu)  – chi phí gồm TNDN nộp thay")
    if kq["thue_gtgt"]:
        print(f"  Nợ 1331             {d(kq['thue_gtgt']):>14} / Có 331 – GTGT nhà thầu, khấu trừ khi có chứng từ nộp thuế thay "
              "(Luật 48/2024 Đ.14 k.2 điểm a); không đủ điều kiện thì tính vào chi phí")
    print(f"  Nợ 331              {d(kq['thue_gtgt'] + kq['thue_tndn']):>14} / Có 3338 (TNDN, GTGT nhà thầu phải nộp)")
    print(f"  Nợ 3338 / Có 112    {d(kq['tong_thue']):>14}  – nộp thuế;  Nợ 331 / Có 112 {d(kq['tra_nha_thau'])} – trả nhà thầu")
    print("\nĐã kiểm tra phép tính. Kiểm tra: nhà thầu có thuộc diện hiệp định tránh đánh thuế hai lần (TT 95/2026) không; "
          "nhà cung cấp dịch vụ số đã tự đăng ký, khai nộp tại Việt Nam chưa; khai theo từng lần thanh toán (TT 89/2026). "
          "Đối chiếu văn bản hiện hành và hỏi cơ quan thuế quản lý trước khi kê khai.")
    return 0


def self_test():
    # net 100 triệu dịch vụ: DT TNDN = 105.263.158; DT GTGT = 110.803.324; GTGT 5.540.166; TNDN 5.263.158
    k = tinh("dich-vu", 100_000_000, "net")
    assert k["thue_tndn"] == 5_263_158 and k["thue_gtgt"] == 5_540_166, k
    assert k["tong_chi_phi_dn"] == 100_000_000 + 5_540_166 + 5_263_158
    g = tinh("dich-vu", 100_000_000, "gross")
    assert g["thue_gtgt"] == 5_000_000 and g["thue_tndn"] == 4_750_000 and g["tra_nha_thau"] == 90_250_000
    lv = tinh("lai-vay", 200_000_000, "gross")
    assert lv["thue_gtgt"] == 0 and lv["thue_tndn"] == 10_000_000
    try:
        tinh("ban-quyen", 50e6, "gross")
        raise AssertionError("bản quyền phải bắt nhập --gtgt")
    except ValueError:
        pass
    bq = tinh("ban-quyen", 50e6, "gross", gtgt="kct")
    assert bq["thue_tndn"] == 5_000_000 and bq["thue_gtgt"] == 0
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
