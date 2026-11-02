#!/usr/bin/env python3
"""Công cụ tài chính cho chủ doanh nghiệp nhỏ: dự báo dòng tiền 13 tuần, điểm hòa vốn, so sánh kế hoạch – thực tế.

1) 13 tuần – CSV: ngay,loai,noi_dung,so_tien[,xac_suat][,lap_lai]
     loai: thu | chi · xac_suat: % chắc chắn của khoản thu (mặc định 100) · lap_lai: '' | tuan | thang
   python3 dong_tien.py 13-tuan dong_tien.csv --so-du-dau 350000000 --tu-ngay 2026-11-02 --muc-toi-thieu 100000000 \\
       --tre-thu 14 --xlsx dong_tien_13_tuan.xlsx
2) Hòa vốn
   python3 dong_tien.py hoa-von --dinh-phi 120000000 --gia-ban 450000 --bien-phi 270000 --san-luong 900
3) Kế hoạch – thực tế (ngưỡng trọng yếu theo cách của anthropics/knowledge-work-plugins finance/variance-analysis)
   CSV: khoan,ke_hoach,thuc_te[,loai]   loai: thu | chi (chi phí vượt kế hoạch là bất lợi)
   python3 dong_tien.py so-sanh ke_hoach_thuc_te.csv --nguong-pt 10 --nguong-tien 20000000
"""
import argparse
import calendar
import csv
import datetime as dt
import re
import sys


def so(s):
    s = str(s or "").strip().replace(" ", "").replace("đ", "")
    if not s:
        return 0.0
    if re.fullmatch(r"-?\d+(\.\d+)?[eE]\d+", s):
        return float(s)
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", s):
        s = s.replace(",", "")
    return float(s)


def d(x):
    s = f"{abs(x):,.0f}".replace(",", ".")
    return f"-{s}" if x < 0 else s


def ngay(s):
    s = str(s).strip()[:10]
    for f in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError(f"ngày không đọc được {s!r}")


def cong_thang(d0, n):
    m = d0.month - 1 + n
    y, m = d0.year + m // 12, m % 12 + 1
    return dt.date(y, m, min(d0.day, calendar.monthrange(y, m)[1]))


def trai_khoan(rows, tu, den, tre_thu=0):
    """Trải các dòng (kể cả lặp lại) thành danh sách (ngày, loại, nội dung, số tiền kỳ vọng) trong [tu, den)."""
    out = []
    for i, r in enumerate(rows, start=2):
        loai = (r.get("loai") or "").strip().lower()
        if loai not in ("thu", "chi"):
            raise ValueError(f"dòng {i}: loai phải là thu hoặc chi")
        tien = so(r.get("so_tien"))
        xs = so(r.get("xac_suat")) if (r.get("xac_suat") or "").strip() else 100.0
        ky_vong = tien * xs / 100 if loai == "thu" else tien
        lap = (r.get("lap_lai") or "").strip().lower()
        d0 = ngay(r["ngay"])
        k = 0
        while True:
            dd = d0 + dt.timedelta(weeks=k) if lap == "tuan" else (cong_thang(d0, k) if lap == "thang" else d0)
            if loai == "thu":
                dd += dt.timedelta(days=tre_thu)
            if dd >= den:
                break
            if dd >= tu:
                out.append((dd, loai, r.get("noi_dung", ""), ky_vong))
            if not lap:
                break
            k += 1
    return out


def du_bao_13_tuan(rows, so_du_dau, tu, muc_toi_thieu=0.0, tre_thu=0, so_tuan=13):
    den = tu + dt.timedelta(weeks=so_tuan)
    ds = trai_khoan(rows, tu, den, tre_thu)
    tuan = []
    sd = so_du_dau
    for w in range(so_tuan):
        a, b = tu + dt.timedelta(weeks=w), tu + dt.timedelta(weeks=w + 1)
        thu = sum(x[3] for x in ds if a <= x[0] < b and x[1] == "thu")
        chi = sum(x[3] for x in ds if a <= x[0] < b and x[1] == "chi")
        dau = sd
        sd = sd + thu - chi
        tuan.append({"tuan": w + 1, "tu": a, "den": b - dt.timedelta(days=1), "dau": dau, "thu": thu, "chi": chi, "cuoi": sd,
                     "canh_bao": "ÂM QUỸ" if sd < 0 else ("dưới mức tối thiểu" if sd < muc_toi_thieu else "")})
    return tuan, ds


def hoa_von(dinh_phi, gia_ban, bien_phi, san_luong=None):
    if gia_ban <= bien_phi:
        raise ValueError("giá bán phải lớn hơn biến phí đơn vị – mỗi sản phẩm đang lỗ, không có điểm hòa vốn")
    sdp = gia_ban - bien_phi
    sl = dinh_phi / sdp
    kq = {"so_du_dam_phi_don_vi": sdp, "ty_le_so_du": sdp / gia_ban, "san_luong_hoa_von": sl, "doanh_thu_hoa_von": sl * gia_ban}
    if san_luong is not None:
        kq["loi_nhuan_tai_san_luong"] = san_luong * sdp - dinh_phi
        kq["bien_an_toan"] = (san_luong - sl) / san_luong if san_luong else None
    return kq


def so_sanh(rows, nguong_pt, nguong_tien):
    out = []
    for r in rows:
        kh, tt = so(r.get("ke_hoach")), so(r.get("thuc_te"))
        loai = (r.get("loai") or "chi").strip().lower()
        chenh = tt - kh
        pt = chenh / kh * 100 if kh else None
        bat_loi = chenh < 0 if loai == "thu" else chenh > 0
        trong_yeu = abs(chenh) >= nguong_tien and (pt is None or abs(pt) >= nguong_pt)
        out.append({"khoan": r.get("khoan", ""), "loai": loai, "ke_hoach": kh, "thuc_te": tt, "chenh": chenh, "pt": pt,
                    "bat_loi": bat_loi, "can_giai_thich": trong_yeu})
    return sorted(out, key=lambda x: -abs(x["chenh"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="lenh")
    t = sub.add_parser("13-tuan")
    t.add_argument("file")
    t.add_argument("--so-du-dau", type=so, required=True, help="tiền mặt + tiền gửi không kỳ hạn đầu kỳ")
    t.add_argument("--tu-ngay", type=ngay, default=dt.date.today())
    t.add_argument("--muc-toi-thieu", type=so, default=0.0, help="số dư tối thiểu muốn giữ")
    t.add_argument("--tre-thu", type=int, default=0, help="kịch bản xấu: mọi khoản thu trễ N ngày")
    t.add_argument("--xlsx")
    h = sub.add_parser("hoa-von")
    h.add_argument("--dinh-phi", type=so, required=True, help="chi phí cố định của kỳ (thuê, lương cố định, khấu hao…)")
    h.add_argument("--gia-ban", type=so, required=True)
    h.add_argument("--bien-phi", type=so, required=True, help="chi phí biến đổi trên mỗi đơn vị (giá vốn, phí sàn, vận chuyển…)")
    h.add_argument("--san-luong", type=so, help="sản lượng dự kiến/thực tế để tính lợi nhuận, biên an toàn")
    s = sub.add_parser("so-sanh")
    s.add_argument("file")
    s.add_argument("--nguong-pt", type=float, default=10.0)
    s.add_argument("--nguong-tien", type=so, default=0.0)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.lenh:
        ap.error("chọn lệnh 13-tuan, hoa-von hoặc so-sanh")
    try:
        if a.lenh == "13-tuan":
            with open(a.file, encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            tuan, ds = du_bao_13_tuan(rows, a.so_du_dau, a.tu_ngay, a.muc_toi_thieu, a.tre_thu)
            in_13_tuan(tuan, a)
            if a.xlsx:
                xuat_13_tuan(a.xlsx, tuan, ds, a.so_du_dau)
                print(f"Đã ghi {a.xlsx}")
        elif a.lenh == "hoa-von":
            k = hoa_von(a.dinh_phi, a.gia_ban, a.bien_phi, a.san_luong)
            print("ĐIỂM HÒA VỐN")
            ty_le = f"{k['ty_le_so_du']:.1%}".replace(".", ",")
            print(f"  Số dư đảm phí mỗi đơn vị   {d(k['so_du_dam_phi_don_vi']):>16} ({ty_le} giá bán)")
            print(f"  Sản lượng hòa vốn          {k['san_luong_hoa_von']:>16,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))
            print(f"  Doanh thu hòa vốn          {d(k['doanh_thu_hoa_von']):>16}")
            if "loi_nhuan_tai_san_luong" in k:
                print(f"  Lợi nhuận tại sản lượng    {d(k['loi_nhuan_tai_san_luong']):>16}")
                if k["bien_an_toan"] is not None:
                    print(f"  Biên an toàn               {k['bien_an_toan']:>16.1%}".replace(".", ","))
            print("Đã kiểm tra phép tính. Lợi nhuận ở đây là trước thuế TNDN, chưa tính lãi vay nếu không đưa vào định phí.")
        else:
            with open(a.file, encoding="utf-8-sig") as f:
                kq = so_sanh(list(csv.DictReader(f)), a.nguong_pt, a.nguong_tien)
            print(f"KẾ HOẠCH – THỰC TẾ (trọng yếu: ≥{a.nguong_pt:g}% và ≥{d(a.nguong_tien)} đồng)\n")
            for x in kq:
                pt = "n/a" if x["pt"] is None else f"{x['pt']:+.1f}%".replace(".", ",")
                co = ("BẤT LỢI" if x["bat_loi"] else "thuận lợi") + (" · CẦN GIẢI THÍCH" if x["can_giai_thich"] else "")
                print(f"  {x['khoan'][:32]:32} KH {d(x['ke_hoach']):>14} TT {d(x['thuc_te']):>14} chênh {d(x['chenh']):>14} {pt:>8}  {co}")
            print("\nĐã kiểm tra phép tính. Với khoản cần giải thích: tách giá – lượng (doanh thu, giá vốn) hoặc theo nhóm chi phí; "
                  "ghi nguyên nhân, có lặp lại không, việc cần làm.")
    except (ValueError, KeyError) as e:
        print("✗ " + str(e))
        return 2
    return 0


def in_13_tuan(tuan, a):
    print(f"DỰ BÁO DÒNG TIỀN 13 TUẦN từ {a.tu_ngay:%d/%m/%Y} – số dư đầu {d(a.so_du_dau)}"
          + (f" – kịch bản thu trễ {a.tre_thu} ngày" if a.tre_thu else "") + "\n")
    print(f"{'Tuần':4} {'Từ':>10} {'Đến':>10} {'Đầu tuần':>15} {'Thu':>14} {'Chi':>14} {'Cuối tuần':>15}")
    for w in tuan:
        print(f"{w['tuan']:>4} {w['tu']:%d/%m/%Y} {w['den']:%d/%m/%Y} {d(w['dau']):>15} {d(w['thu']):>14} {d(w['chi']):>14} "
              f"{d(w['cuoi']):>15}  {w['canh_bao']}")
    thap = min(tuan, key=lambda w: w["cuoi"])
    print(f"\nĐiểm thấp nhất: tuần {thap['tuan']} ({thap['den']:%d/%m/%Y}) – {d(thap['cuoi'])} đồng.")
    if any(w["canh_bao"] for w in tuan):
        print("! Có tuần âm quỹ hoặc dưới mức tối thiểu: xem lại lịch thu nợ, giãn chi, hạn mức vay, gia hạn thuế (nếu đủ điều kiện).")
    print("Đã kiểm tra phép tính. Khoản thu đã nhân xác suất; nhớ đưa các hạn nộp thuế, bảo hiểm, lương vào phần chi.")


def xuat_13_tuan(path, tuan, ds, so_du_dau):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "13 tuan"
    ws.append(["Tuần", "Từ", "Đến", "Đầu tuần", "Thu", "Chi", "Cuối tuần", "Cảnh báo"])
    for c in ws[1]:
        c.font = Font(bold=True)
    for i, w in enumerate(tuan, start=2):
        dau = so_du_dau if i == 2 else f"=G{i - 1}"
        ws.append([w["tuan"], w["tu"], w["den"], dau, w["thu"], w["chi"], f"=D{i}+E{i}-F{i}", w["canh_bao"]])
    for row in ws.iter_rows(min_row=2):
        row[1].number_format = row[2].number_format = "DD/MM/YYYY"
        for c in row[3:7]:
            c.number_format = "#,##0;[Red]-#,##0"
    ws2 = wb.create_sheet("Chi tiet")
    ws2.append(["Ngày", "Loại", "Nội dung", "Số tiền kỳ vọng"])
    for x in sorted(ds):
        ws2.append(list(x))
    for row in ws2.iter_rows(min_row=2):
        row[0].number_format = "DD/MM/YYYY"
        row[3].number_format = "#,##0"
    wb.save(path)


def self_test():
    import io
    import os
    import tempfile
    rows = list(csv.DictReader(io.StringIO(
        "ngay,loai,noi_dung,so_tien,xac_suat,lap_lai\n"
        "2026-11-05,thu,Khách A trả,200000000,100,\n"
        "2026-11-20,thu,Khách B trả,100000000,50,\n"
        "2026-11-10,chi,Lương,80000000,,thang\n"
        "2026-11-02,chi,Thuê văn phòng,20000000,,thang\n"
        "2026-12-30,chi,Thuế GTGT quý III gia hạn,60000000,,\n")))
    tuan, ds = du_bao_13_tuan(rows, 50e6, dt.date(2026, 11, 2), 30e6)
    assert len(tuan) == 13 and tuan[0]["chi"] == 20e6 and tuan[0]["thu"] == 200e6
    assert tuan[2]["thu"] == 50e6  # khách B 50%
    # 13 tuần đến 31/01/2027: lương 3 lần (10/11, 10/12, 10/01), thuê 3 lần (02/11, 02/12, 02/01)
    assert sum(w["chi"] for w in tuan) == 3 * 80e6 + 3 * 20e6 + 60e6
    assert tuan[-1]["cuoi"] == 50e6 + 250e6 - 360e6 and tuan[-1]["canh_bao"] == "ÂM QUỸ"
    tre, _ = du_bao_13_tuan(rows, 50e6, dt.date(2026, 11, 2), 0, tre_thu=14)
    assert tre[0]["thu"] == 0 and tre[2]["thu"] == 200e6
    k = hoa_von(120e6, 450_000, 270_000, 900)
    assert round(k["san_luong_hoa_von"], 4) == round(120e6 / 180_000, 4) and k["loi_nhuan_tai_san_luong"] == 900 * 180_000 - 120e6
    try:
        hoa_von(1e6, 100, 120)
        raise AssertionError("phải báo lỗi khi giá ≤ biến phí")
    except ValueError:
        pass
    ss = so_sanh([{"khoan": "Doanh thu", "ke_hoach": "500000000", "thuc_te": "430000000", "loai": "thu"},
                  {"khoan": "Quảng cáo", "ke_hoach": "50000000", "thuc_te": "52000000", "loai": "chi"}], 10, 20e6)
    dt_ = next(x for x in ss if x["khoan"] == "Doanh thu")
    qc = next(x for x in ss if x["khoan"] == "Quảng cáo")
    assert dt_["bat_loi"] and dt_["can_giai_thich"] and qc["bat_loi"] and not qc["can_giai_thich"]
    with tempfile.TemporaryDirectory() as t:
        xuat_13_tuan(os.path.join(t, "x.xlsx"), tuan, ds, 50e6)
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
