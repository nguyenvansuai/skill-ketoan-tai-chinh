#!/usr/bin/env python3
"""Tính khấu hao TSCĐ (đường thẳng) hoặc phân bổ chi phí trả trước 242 cho một kỳ tháng; lập bảng và bút toán TT133.

CSV: ma,ten,nguyen_gia,ngay_bat_dau,so_thang,bo_phan[,luy_ke_dau]
  bo_phan: 6421 (bán hàng) · 6422 (quản lý) · 154 (sản xuất) – tài khoản chi phí ghi Nợ
  luy_ke_dau: hao mòn/đã phân bổ lũy kế đến đầu kỳ (bỏ trống → script tự tính từ ngày bắt đầu)
Phương pháp đường thẳng; tháng đầu, tháng cuối tính theo số ngày sử dụng thực tế (TT 45/2013 Đ.9 – văn bản tiếp tục
hiệu lực đến khi thay thế, không quá 31/12/2026 [cần kiểm tra văn bản mới]). Tiêu chuẩn TSCĐ: nguyên giá từ 30 triệu,
thời gian sử dụng trên 1 năm [cần kiểm tra]; khung thời gian khấu hao theo Phụ lục I TT 45/2013.

  python3 khau_hao.py tscd.csv --ky 2026-10                 # TSCĐ → Có 2141
  python3 khau_hao.py tra_truoc.csv --ky 2026-10 --loai 242 # chi phí trả trước → Có 242
"""
import argparse
import calendar
import csv
import datetime as dt
import sys
from collections import defaultdict

NGUONG_TSCD = 30_000_000


def so(s):
    s = str(s or "").strip().replace(" ", "")
    if not s:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3):
        s = s.replace(".", "")
    else:
        s = s.replace(",", "")
    return float(s)


def ngay(s):
    s = str(s).strip()[:10]
    for f in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError(f"ngày không đọc được {s!r}")


def cong_thang(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def khau_hao_thang(nguyen_gia, bat_dau, so_thang, nam, thang):
    """Số khấu hao trong tháng (nam, thang), theo ngày sử dụng thực tế ở tháng đầu và tháng cuối."""
    ket_thuc = cong_thang(bat_dau, so_thang)  # ngày hết khấu hao (không tính)
    dau = dt.date(nam, thang, 1)
    so_ngay = calendar.monthrange(nam, thang)[1]
    cuoi = dt.date(nam, thang, so_ngay) + dt.timedelta(days=1)
    tu, den = max(dau, bat_dau), min(cuoi, ket_thuc)
    if den <= tu:
        return 0.0
    muc_thang = nguyen_gia / so_thang
    return muc_thang * (den - tu).days / so_ngay


def luy_ke_den(nguyen_gia, bat_dau, so_thang, nam, thang):
    tong, d = 0.0, dt.date(bat_dau.year, bat_dau.month, 1)
    while (d.year, d.month) < (nam, thang):
        tong += khau_hao_thang(nguyen_gia, bat_dau, so_thang, d.year, d.month)
        d = cong_thang(d, 1)
    return tong


def tinh(rows, nam, thang, loai):
    ket, canh_bao = [], []
    for r in rows:
        ng, bd, st = so(r["nguyen_gia"]), ngay(r["ngay_bat_dau"]), int(so(r["so_thang"]))
        if st <= 0 or ng <= 0:
            canh_bao.append(f"{r['ma']}: nguyên giá/số tháng không hợp lệ")
            continue
        lk = so(r["luy_ke_dau"]) if (r.get("luy_ke_dau") or "").strip() else luy_ke_den(ng, bd, st, nam, thang)
        kh = khau_hao_thang(ng, bd, st, nam, thang)
        kh = max(0.0, min(kh, ng - lk))
        if loai == "tscd" and ng < NGUONG_TSCD:
            canh_bao.append(f"{r['ma']} {r['ten']}: nguyên giá {ng:,.0f} < 30 triệu – không đủ tiêu chuẩn TSCĐ, chuyển 153/242 [cần kiểm tra]".replace(",", "."))
        if loai == "242" and st > 36:
            canh_bao.append(f"{r['ma']}: phân bổ {st} tháng > 3 năm – kiểm tra quy định thời gian phân bổ chi phí trả trước [cần kiểm tra]")
        bp = (r.get("bo_phan") or "6422").strip()
        ket.append({"ma": r["ma"], "ten": r["ten"], "nguyen_gia": ng, "luy_ke_dau": lk, "trong_ky": round(kh),
                    "luy_ke_cuoi": lk + round(kh), "con_lai": ng - lk - round(kh), "bo_phan": bp})
    return ket, canh_bao


def d(x):
    return f"{x:,.0f}".replace(",", ".")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ky", help="tháng tính, YYYY-MM")
    ap.add_argument("--loai", choices=["tscd", "242"], default="tscd")
    ap.add_argument("--tk-co", help="tài khoản ghi Có (mặc định 2141 với TSCĐ, 242 với chi phí trả trước); TSCĐ vô hình dùng 2143")
    ap.add_argument("--xlsx")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.file or not a.ky:
        ap.error("cần file CSV và --ky YYYY-MM")
    nam, thang = map(int, a.ky.split("-"))
    with open(a.file, encoding="utf-8-sig") as f:
        ket, cb = tinh(list(csv.DictReader(f)), nam, thang, a.loai)
    tk_co = a.tk_co or ("2141" if a.loai == "tscd" else "242")
    nhan = "KHẤU HAO TSCĐ" if a.loai == "tscd" else "PHÂN BỔ CHI PHÍ TRẢ TRƯỚC"
    print(f"{nhan} THÁNG {thang:02d}/{nam}\n")
    print(f"{'Mã':8} {'Tên':30} {'Nguyên giá':>15} {'Lũy kế đầu':>15} {'Trong kỳ':>13} {'Còn lại':>15} TK chi phí")
    for k in ket:
        print(f"{k['ma']:8} {k['ten'][:30]:30} {d(k['nguyen_gia']):>15} {d(k['luy_ke_dau']):>15} {d(k['trong_ky']):>13} {d(k['con_lai']):>15} {k['bo_phan']}")
    theo_bp = defaultdict(float)
    for k in ket:
        theo_bp[k["bo_phan"]] += k["trong_ky"]
    print("\nBút toán:")
    for bp, v in sorted(theo_bp.items()):
        if v:
            print(f"  Nợ {bp:6} / Có {tk_co:6}  {d(v):>15}")
    print(f"  Cộng                   {d(sum(theo_bp.values())):>15}")
    for x in cb:
        print("! " + x)
    print("Đã kiểm tra phép tính.")
    if a.xlsx:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["Mã", "Tên", "Nguyên giá", "Lũy kế đầu kỳ", "Trong kỳ", "Lũy kế cuối kỳ", "Còn lại", "TK chi phí"])
        for i, k in enumerate(ket, start=2):
            ws.append([k["ma"], k["ten"], k["nguyen_gia"], k["luy_ke_dau"], k["trong_ky"], f"=D{i}+E{i}", f"=C{i}-F{i}", k["bo_phan"]])
        n = ws.max_row
        ws.append(["", "CỘNG"] + [f"=SUM({c}2:{c}{n})" for c in "CDEFG"] + [""])
        for row in ws.iter_rows(min_row=2):
            for c in row[2:7]:
                c.number_format = "#,##0"
        wb.save(a.xlsx)
        print(f"Đã ghi {a.xlsx}")
    return 0


def self_test():
    # 120 triệu, 60 tháng, bắt đầu 01/01/2026 → 2.000.000/tháng
    assert round(khau_hao_thang(120e6, dt.date(2026, 1, 1), 60, 2026, 10)) == 2_000_000
    # bắt đầu 16/10/2026: tháng 10 có 31 ngày, dùng 16 ngày
    assert round(khau_hao_thang(120e6, dt.date(2026, 10, 16), 60, 2026, 10)) == round(2_000_000 * 16 / 31)
    # tổng khấu hao toàn bộ đời tài sản = nguyên giá
    tong, dd = 0.0, dt.date(2026, 10, 1)
    for _ in range(62):
        tong += khau_hao_thang(120e6, dt.date(2026, 10, 16), 60, dd.year, dd.month)
        dd = cong_thang(dd, 1)
    assert abs(tong - 120e6) < 1, tong
    rows = [{"ma": "TS01", "ten": "Máy tính", "nguyen_gia": "25.000.000", "ngay_bat_dau": "2026-01-01", "so_thang": "36", "bo_phan": "6422"},
            {"ma": "TS02", "ten": "Xe tải", "nguyen_gia": "600000000", "ngay_bat_dau": "2025-07-01", "so_thang": "96", "bo_phan": "6421"}]
    ket, cb = tinh(rows, 2026, 10, "tscd")
    assert ket[1]["trong_ky"] == 6_250_000 and ket[1]["luy_ke_dau"] == 15 * 6_250_000
    assert any("TS01" in x and "30 triệu" in x for x in cb)
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
