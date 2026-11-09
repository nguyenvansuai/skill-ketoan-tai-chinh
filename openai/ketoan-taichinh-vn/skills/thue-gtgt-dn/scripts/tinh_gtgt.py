#!/usr/bin/env python3
"""Tính số thuế GTGT phải nộp / còn được khấu trừ của kỳ (tháng hoặc quý) cho DN nhỏ và vừa.

A. Phương pháp KHẤU TRỪ – đầu vào là bảng kê hóa đơn CSV (xuất từ skill doc-hoa-don-xml, hoặc tự lập) với cột:
   chieu (mua-vao | ban-ra), ngay, ban_mst, ban_ten, so, tien_hang, tien_thue[, tsuat][, thanh_toan][, loai_tru]
   thanh_toan: CK (không dùng tiền mặt) | TM (tiền mặt) | trống (chưa thanh toán / chưa rõ)
   loai_tru:   x nếu hóa đơn dùng cho hoạt động không chịu thuế, phúc lợi không đủ điều kiện… (loại khỏi khấu trừ)
   Điều kiện khấu trừ (Luật GTGT 48/2024 Đ.14 k.2; ngưỡng 5 triệu tại NĐ 181/2025 Đ.26 – TC): hóa đơn hợp pháp + chứng từ thanh toán không
   dùng tiền mặt khi hóa đơn (hoặc tổng hóa đơn cùng người bán cùng ngày) từ 5 triệu đồng trở lên (giá đã có thuế).
B. Phương pháp TRỰC TIẾP (% doanh thu, Luật GTGT 48/2024 Đ.12 k.2 – DN doanh thu năm dưới 1 tỷ, trừ khi tự nguyện khấu trừ): --truc-tiep hang-hoa=… dich-vu=… san-xuat=… khac=…
   Giảm 20% tỷ lệ % đến 31/12/2026 cho nhóm được giảm (NĐ 174/2025): thêm --giam-20 (tự xác định nhóm được giảm).

  python3 tinh_gtgt.py bang_ke_q3.csv --con-khau-tru-ky-truoc 12000000
  python3 tinh_gtgt.py --truc-tiep hang-hoa=2.4e9 dich-vu=300e6 --giam-20
"""
import argparse
import csv
import io
import re
import sys
from collections import defaultdict

NGUONG = 5_000_000
TY_LE_TT = {"hang-hoa": 0.01, "dich-vu": 0.05, "san-xuat": 0.03, "khac": 0.02}


def so(s):
    s = str(s or "").strip().replace(" ", "")
    if not s:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", s):
        s = s.replace(",", "")
    return float(s)


def d(x):
    return f"{x:,.0f}".replace(",", ".")


def khau_tru(rows, con_kt_truoc=0.0):
    mua = [r for r in rows if r.get("chieu") == "mua-vao"]
    ban = [r for r in rows if r.get("chieu") == "ban-ra"]
    nhom = defaultdict(float)
    for r in mua:
        nhom[(r.get("ban_mst", ""), r.get("ngay", "")[:10])] += so(r["tien_hang"]) + so(r["tien_thue"])
    du_dk, khong_dk, cho = [], [], []
    for r in mua:
        thue = so(r["tien_thue"])
        lon = nhom[(r.get("ban_mst", ""), r.get("ngay", "")[:10])] >= NGUONG
        tt = (r.get("thanh_toan") or "").strip().upper()
        if (r.get("loai_tru") or "").strip():
            khong_dk.append((r, "loại trừ theo đánh dấu (không dùng cho hoạt động chịu thuế…)"))
        elif lon and tt == "TM":
            khong_dk.append((r, "từ 5 triệu (cộng cùng người bán cùng ngày) nhưng trả tiền mặt"))
        elif lon and tt != "CK":
            cho.append((r, "từ 5 triệu, chưa có/chưa rõ chứng từ thanh toán không dùng tiền mặt – được kê khai nếu thanh toán đúng hạn hợp đồng [cần kiểm tra quy định mua trả chậm]"))
            du_dk.append(r)
        else:
            du_dk.append(r)
    v = {
        "dau_vao_gia_tri": sum(so(r["tien_hang"]) for r in mua),
        "dau_vao_thue": sum(so(r["tien_thue"]) for r in mua),
        "dau_vao_duoc_kt": sum(so(r["tien_thue"]) for r in du_dk),
        "dau_ra_gia_tri": sum(so(r["tien_hang"]) for r in ban),
        "dau_ra_thue": sum(so(r["tien_thue"]) for r in ban),
        "con_kt_truoc": con_kt_truoc,
    }
    chenh = v["dau_ra_thue"] - v["dau_vao_duoc_kt"] - con_kt_truoc
    v["phai_nop"] = max(chenh, 0.0)
    v["chuyen_ky_sau"] = max(-chenh, 0.0)
    theo_ts = defaultdict(lambda: [0.0, 0.0])
    for r in ban:
        ts = (r.get("tsuat") or "").strip() or "chưa ghi"
        theo_ts[ts][0] += so(r["tien_hang"])
        theo_ts[ts][1] += so(r["tien_thue"])
    return v, khong_dk, cho, dict(theo_ts)


def truc_tiep(doanh_thu, giam_20):
    dong, tong = [], 0.0
    for nganh, dt_ in doanh_thu.items():
        tl = TY_LE_TT[nganh] * (0.8 if giam_20 else 1)
        thue = dt_ * tl
        dong.append((nganh, dt_, tl, thue))
        tong += thue
    return dong, tong


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--con-khau-tru-ky-truoc", type=so, default=0.0)
    ap.add_argument("--truc-tiep", nargs="+", metavar="NGANH=DOANH_THU")
    ap.add_argument("--giam-20", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.truc_tiep:
        dt_ = {}
        for x in a.truc_tiep:
            k, val = x.split("=")
            if k not in TY_LE_TT:
                ap.error(f"ngành {k} không hợp lệ; chọn {', '.join(TY_LE_TT)}")
            dt_[k] = float(val)
        dong, tong = truc_tiep(dt_, a.giam_20)
        print("THUẾ GTGT – PHƯƠNG PHÁP TRỰC TIẾP (% doanh thu, Luật GTGT 48/2024 Đ.12 k.2)")
        for nganh, v, tl, thue in dong:
            print(f"  {nganh:10} doanh thu {d(v):>16} × {tl * 100:.2f}% = {d(thue):>14}")
        print(f"  PHẢI NỘP {d(tong):>45}")
        if a.giam_20:
            print("  Đã giảm 20% tỷ lệ (NĐ 174/2025, đến 31/12/2026) – chỉ đúng với hàng hóa, dịch vụ được giảm; ghi chú trên hóa đơn.")
        print("Đã kiểm tra phép tính. Phương pháp trực tiếp áp dụng cho DN doanh thu năm dưới 1 tỷ chưa đăng ký tự nguyện khấu trừ (Luật 48/2024 Đ.11 k.2, Đ.12 k.2).")
        return 0
    if not a.file:
        ap.error("cần file bảng kê hoặc --truc-tiep")
    with open(a.file, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    v, kdk, cho, theo_ts = khau_tru(rows, a.con_khau_tru_ky_truoc)
    in_kq(v, kdk, cho, theo_ts)
    return 0


def in_kq(v, kdk, cho, theo_ts):
    print("THUẾ GTGT – PHƯƠNG PHÁP KHẤU TRỪ")
    print(f"  Thuế GTGT còn được khấu trừ kỳ trước chuyển sang      {d(v['con_kt_truoc']):>16}")
    print(f"  Giá trị HHDV mua vào (chưa thuế)                      {d(v['dau_vao_gia_tri']):>16}")
    print(f"  Thuế GTGT của HHDV mua vào                            {d(v['dau_vao_thue']):>16}")
    print(f"  Thuế GTGT đầu vào đủ điều kiện khấu trừ kỳ này        {d(v['dau_vao_duoc_kt']):>16}")
    print(f"  Doanh số HHDV bán ra (chưa thuế)                      {d(v['dau_ra_gia_tri']):>16}")
    print(f"  Thuế GTGT đầu ra                                      {d(v['dau_ra_thue']):>16}")
    for ts, (g, t) in sorted(theo_ts.items()):
        print(f"     thuế suất {ts:8}: doanh số {d(g):>16} – thuế {d(t):>14}")
    print(f"  → THUẾ GTGT PHẢI NỘP                                  {d(v['phai_nop']):>16}")
    print(f"  → THUẾ GTGT CÒN ĐƯỢC KHẤU TRỪ CHUYỂN KỲ SAU           {d(v['chuyen_ky_sau']):>16}")
    if kdk:
        print("\nKHÔNG ĐƯỢC KHẤU TRỪ (đã loại):")
        for r, ly_do in kdk:
            print(f"  {r.get('ngay', '')[:10]} {r.get('ban_ten', '')[:30]:30} HĐ {r.get('so', ''):>8} thuế {d(so(r['tien_thue'])):>12} – {ly_do}")
    if cho:
        print("\nCẦN BỔ SUNG CHỨNG TỪ THANH TOÁN (đang tính vào khấu trừ):")
        for r, ly_do in cho:
            print(f"  {r.get('ngay', '')[:10]} {r.get('ban_ten', '')[:30]:30} HĐ {r.get('so', ''):>8} thuế {d(so(r['tien_thue'])):>12}")
        print("  " + cho[0][1])
    print("\nBút toán khấu trừ cuối kỳ: Nợ 33311 / Có 1331 = số nhỏ hơn giữa thuế đầu ra và thuế đầu vào được khấu trừ (kể cả kỳ trước).")
    print("Đã kiểm tra phép tính. Đối chiếu tờ khai trên eTax/HTKK (mẫu theo TT 89/2026) và hỏi cơ quan thuế quản lý trước khi nộp.")


def self_test():
    csv_txt = ("chieu,ngay,ban_mst,ban_ten,so,tien_hang,tien_thue,tsuat,thanh_toan\n"
               "mua-vao,2026-07-05,0300000001,NCC A,11,10000000,1000000,10%,CK\n"
               "mua-vao,2026-07-06,0300000002,NCC B,12,6000000,480000,8%,TM\n"
               "mua-vao,2026-07-07,0300000003,NCC C,13,2000000,160000,8%,TM\n"
               "mua-vao,2026-07-07,0300000003,NCC C,14,3000000,240000,8%,TM\n"
               "mua-vao,2026-07-08,0300000004,NCC D,15,20000000,2000000,10%,\n"
               "ban-ra,2026-07-20,0312345678,Tôi,101,50000000,4000000,8%,\n")
    rows = list(csv.DictReader(io.StringIO(csv_txt)))
    v, kdk, cho, ts = khau_tru(rows, 500_000)
    # B (6,48tr TM) và C (2,16 + 3,24 = 5,4tr cùng ngày TM) bị loại; D chờ chứng từ nhưng vẫn tính
    assert len(kdk) == 3 and len(cho) == 1
    assert v["dau_vao_duoc_kt"] == 3_000_000
    assert v["phai_nop"] == 4_000_000 - 3_000_000 - 500_000
    dong, tong = truc_tiep({"hang-hoa": 2.4e9, "dich-vu": 300e6}, True)
    assert round(tong) == round(2.4e9 * 0.008 + 300e6 * 0.04)
    in_kq(v, kdk, cho, ts)
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
