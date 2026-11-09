#!/usr/bin/env python3
"""Phân tích tuổi nợ phải thu (131) hoặc phải trả (331) và ước tính dự phòng phải thu khó đòi.

Đầu vào CSV: doi_tuong,so_hd,ngay_hd,han_tt,so_tien,da_tra   (han_tt trống → ngay_hd + --han-mac-dinh ngày)
Nhóm tuổi theo số ngày quá hạn tại --ngay-chot: chưa đến hạn · 1–30 · 31–90 · 91–180 · 181–365 · >1 năm.

Mức dự phòng tham khảo (TT 48/2019/TT-BTC, tiếp tục hiệu lực đến khi thay thế, không quá 31/12/2026 – [cần kiểm tra]):
quá hạn 6 tháng–dưới 1 năm 30% · 1–dưới 2 năm 50% · 2–dưới 3 năm 70% · từ 3 năm 100%. Điều kiện: có chứng từ gốc,
đối chiếu công nợ/đòi nợ; trích dự phòng: Nợ 6422 / Có 2293.

  python3 tuoi_no.py cong_no_131.csv --ngay-chot 2026-12-31 --xlsx tuoi_no.xlsx
"""
import argparse
import csv
import datetime as dt
import re
import sys
from collections import defaultdict

NHOM = [(0, "Chưa đến hạn"), (30, "Quá hạn 1–30 ngày"), (90, "31–90 ngày"), (180, "91–180 ngày"), (365, "181–365 ngày"), (10**9, "Trên 1 năm")]


def so(s):
    s = str(s or "").strip().replace(" ", "")
    if not s or s == "-":
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", s):
        s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    return float(s)


def ngay(s):
    s = str(s).strip()[:10]
    for f in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError(f"ngày không đọc được {s!r}")


def ty_le_du_phong(qua_han_ngay, chot, han):
    if qua_han_ngay <= 0:
        return 0.0
    def cong_nam(d, n):
        try:
            return d.replace(year=d.year + n)
        except ValueError:
            return d.replace(year=d.year + n, day=28)
    if chot >= cong_nam(han, 3):
        return 1.0
    if chot >= cong_nam(han, 2):
        return 0.7
    if chot >= cong_nam(han, 1):
        return 0.5
    m = han.month + 6
    sau_6t = dt.date(han.year + (m - 1) // 12, (m - 1) % 12 + 1, min(han.day, 28))
    return 0.3 if chot >= sau_6t else 0.0


def phan_tich(rows, chot, han_md):
    ket = []
    for r in rows:
        con = so(r["so_tien"]) - so(r.get("da_tra"))
        if con <= 0.5:
            continue
        n_hd = ngay(r["ngay_hd"])
        han = ngay(r["han_tt"]) if (r.get("han_tt") or "").strip() else n_hd + dt.timedelta(days=han_md)
        qh = (chot - han).days
        nhom = next(t for gh, t in NHOM if qh <= gh)
        tl = ty_le_du_phong(qh, chot, han)
        ket.append({"doi_tuong": r["doi_tuong"], "so_hd": r.get("so_hd", ""), "han": han, "qua_han": qh, "con_no": con,
                    "nhom": nhom, "ty_le_dp": tl, "du_phong": con * tl})
    return ket


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ngay-chot", type=ngay, default=dt.date.today())
    ap.add_argument("--han-mac-dinh", type=int, default=30, help="số ngày hạn thanh toán khi cột han_tt trống")
    ap.add_argument("--xlsx")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.file:
        ap.error("cần file CSV công nợ")
    with open(a.file, encoding="utf-8-sig") as f:
        ket = phan_tich(list(csv.DictReader(f)), a.ngay_chot, a.han_mac_dinh)
    in_bc(ket, a.ngay_chot)
    if a.xlsx:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Tuoi no"
        ws.append(["Đối tượng", "Số HĐ", "Hạn TT", "Số ngày quá hạn", "Còn nợ", "Nhóm tuổi", "Tỷ lệ DP", "Dự phòng tham khảo"])
        for k in ket:
            ws.append([k["doi_tuong"], k["so_hd"], k["han"], k["qua_han"], k["con_no"], k["nhom"], k["ty_le_dp"], k["du_phong"]])
        n = ws.max_row
        ws.append(["CỘNG", "", "", "", f"=SUM(E2:E{n})", "", "", f"=SUM(H2:H{n})"])
        for row in ws.iter_rows(min_row=2):
            row[2].number_format = "DD/MM/YYYY"
            row[4].number_format = row[7].number_format = "#,##0"
            row[6].number_format = "0%"
        wb.save(a.xlsx)
        print(f"Đã ghi {a.xlsx}")
    return 0


def d(x):
    return f"{x:,.0f}".replace(",", ".")


def in_bc(ket, chot):
    print(f"Tuổi nợ tại {chot:%d/%m/%Y}: {len(ket)} khoản còn nợ, tổng {d(sum(k['con_no'] for k in ket))} đồng\n")
    theo_nhom = defaultdict(float)
    for k in ket:
        theo_nhom[k["nhom"]] += k["con_no"]
    for _, t in NHOM:
        if theo_nhom.get(t):
            print(f"  {t:22} {d(theo_nhom[t]):>16}")
    theo_dt = defaultdict(lambda: [0.0, 0])
    for k in ket:
        theo_dt[k["doi_tuong"]][0] += k["con_no"]
        theo_dt[k["doi_tuong"]][1] = max(theo_dt[k["doi_tuong"]][1], k["qua_han"])
    print("\nTheo đối tượng (quá hạn lâu nhất):")
    for ten_dt, (v, qh) in sorted(theo_dt.items(), key=lambda x: -x[1][0]):
        print(f"  {ten_dt[:35]:35} {d(v):>16}  quá hạn tối đa {max(qh, 0)} ngày")
    dp = sum(k["du_phong"] for k in ket)
    if dp:
        print(f"\nDự phòng phải thu khó đòi tham khảo (TT 48/2019 – [cần kiểm tra]): {d(dp)} đồng → Nợ 6422 / Có 2293 "
              "(chỉ trích khi đủ hồ sơ: chứng từ gốc, biên bản đối chiếu, văn bản đòi nợ).")
    print("Đã kiểm tra phép tính.")


def self_test():
    rows = [
        {"doi_tuong": "KH A", "so_hd": "1", "ngay_hd": "2026-11-20", "han_tt": "2026-12-20", "so_tien": "10000000", "da_tra": "0"},
        {"doi_tuong": "KH B", "so_hd": "2", "ngay_hd": "2026-01-10", "han_tt": "2026-02-10", "so_tien": "20.000.000", "da_tra": "5.000.000"},
        {"doi_tuong": "KH C", "so_hd": "3", "ngay_hd": "2024-10-01", "han_tt": "2024-11-01", "so_tien": "8000000", "da_tra": ""},
        {"doi_tuong": "KH D", "so_hd": "4", "ngay_hd": "2026-01-01", "han_tt": "", "so_tien": "1000000", "da_tra": "1000000"},
    ]
    ket = phan_tich(rows, dt.date(2026, 12, 31), 30)
    assert len(ket) == 3
    b = next(k for k in ket if k["doi_tuong"] == "KH B")
    assert b["con_no"] == 15_000_000 and b["ty_le_dp"] == 0.3 and b["nhom"] == "181–365 ngày"
    c = next(k for k in ket if k["doi_tuong"] == "KH C")
    assert c["ty_le_dp"] == 0.7 and c["nhom"] == "Trên 1 năm"
    a = next(k for k in ket if k["doi_tuong"] == "KH A")
    assert a["qua_han"] == 11 and a["ty_le_dp"] == 0
    in_bc(ket, dt.date(2026, 12, 31))
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
