#!/usr/bin/env python3
"""Lập bảng lương tháng cho DN nhỏ và vừa: bảo hiểm bắt buộc (phần NLĐ, phần DN), KPCĐ, thuế TNCN khấu trừ, lương thực nhận,
chi phí DN và bút toán TT133.

Căn cứ (xem references/van-ban-hieu-luc.md): Luật TNCN 109/2025 Đ.9 (biểu 5 bậc), Đ.10 (giảm trừ 15,5 triệu / 6,2 triệu);
NĐ 253/2026 Đ.50 (HĐ dưới 3 tháng, không HĐ: 10% mỗi lần trả từ 5 triệu), Đ.8 (ăn ca ≤1,2 triệu không tính);
NĐ 161/2026 (lương cơ sở 2.530.000 từ 01/07/2026 → trần BHXH, BHYT 50.600.000; trước đó 2.340.000 → 46.800.000);
NĐ 293/2025 (lương tối thiểu vùng 2026 → trần BHTN 20 lần). Tỷ lệ đóng: [cần kiểm tra với cơ quan BHXH].

CSV (UTF-8, có tiêu đề):
  ma,ho_ten,loai_hd,luong_dong_bh,tong_thu_nhap,an_ca,lam_them_mien,so_npt,bo_phan[,chu_dn]
  loai_hd: dai (HĐLĐ từ 3 tháng) | ngan (HĐ dưới 3 tháng) | khong (không HĐ, cộng tác viên)
  luong_dong_bh: tiền lương làm căn cứ đóng bảo hiểm (để trống/0 nếu không thuộc diện đóng)
  tong_thu_nhap: tổng tiền lương, tiền công, phụ cấp, thưởng trong tháng (gross, chưa trừ gì)
  an_ca: tiền ăn giữa ca · lam_them_mien: phần tiền làm thêm giờ được miễn thuế (phần trả cao hơn so với giờ thường)
  bo_phan: 6421 (bán hàng) · 6422 (quản lý) · 154 (sản xuất) · chu_dn: x nếu là chủ DNTN / chủ TNHH MTV cá nhân

  python3 tinh_luong.py bang_luong_10_2026.csv --ky 2026-10 --vung 1 --xlsx bang_luong.xlsx
"""
import argparse
import csv
import datetime as dt
import re
import sys
from collections import defaultdict

LTTV_2026 = {1: 5_310_000, 2: 4_730_000, 3: 4_140_000, 4: 3_700_000}  # NĐ 293/2025
GIAM_TRU_BAN_THAN, GIAM_TRU_NPT = 15_500_000, 6_200_000  # Luật 109/2025 Đ.10
AN_CA_TOI_DA = 1_200_000  # NĐ 253/2026
BAC = [(10e6, 0.05), (30e6, 0.10), (60e6, 0.20), (100e6, 0.30), (float("inf"), 0.35)]  # Luật 109/2025 Đ.9, theo tháng
# (DN, NLĐ) – BHXH gồm ốm đau thai sản 3% + hưu trí tử tuất 14% (DN) / 8% (NLĐ); TNLĐ-BNN 0,5% DN
TL = {"bhxh": (0.17, 0.08), "tnld": (0.005, 0.0), "bhyt": (0.03, 0.015), "bhtn": (0.01, 0.01)}
KPCD = 0.02
TK = {"bhxh": "3383", "tnld": "3383", "bhyt": "3384", "bhtn": "3385"}


def so(s):
    s = str(s or "").strip().replace(" ", "").replace("đ", "")
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


def tran_bhxh(ky):
    return 50_600_000 if ky >= dt.date(2026, 7, 1) else 46_800_000


def thue_luy_tien(tntt):
    thue, duoi = 0.0, 0.0
    for tren, ts in BAC:
        if tntt > duoi:
            thue += (min(tntt, tren) - duoi) * ts
        duoi = tren
    return round(thue)


def tinh_nguoi(r, ky, vung, lttv=None):
    cb = []
    lt = lttv or LTTV_2026[vung]
    loai = (r.get("loai_hd") or "dai").strip().lower()
    if loai not in ("dai", "ngan", "khong"):
        raise ValueError(f"{r.get('ma')}: loai_hd phải là dai/ngan/khong")
    luong_bh = so(r.get("luong_dong_bh"))
    gross = so(r.get("tong_thu_nhap"))
    an_ca, ot_mien, npt = so(r.get("an_ca")), so(r.get("lam_them_mien")), int(so(r.get("so_npt")))
    tran = tran_bhxh(ky)
    bh_nld, bh_dn = {}, {}
    if luong_bh > 0:
        if luong_bh < lt:
            cb.append(f"lương đóng BH {d(luong_bh)} thấp hơn lương tối thiểu vùng {d(lt)}")
        for k, (t_dn, t_nld) in TL.items():
            can_cu = min(luong_bh, 20 * lt if k == "bhtn" else tran)
            bh_dn[k], bh_nld[k] = round(can_cu * t_dn), round(can_cu * t_nld)
        if luong_bh > tran:
            cb.append(f"lương đóng BH vượt trần {d(tran)} – BHXH, BHYT tính trên trần")
    elif loai == "dai":
        cb.append("HĐLĐ từ 3 tháng nhưng không có lương đóng BH – kiểm tra diện bắt buộc (HĐLĐ từ đủ 1 tháng, Luật BHXH 41/2024)")
    tong_bh_nld = sum(bh_nld.values())
    khong_tinh = min(an_ca, AN_CA_TOI_DA) + ot_mien
    if an_ca > AN_CA_TOI_DA:
        cb.append(f"ăn ca {d(an_ca)} > 1,2 triệu – phần vượt tính vào thu nhập chịu thuế")
    tnct = max(gross - khong_tinh, 0)
    if loai == "dai":
        giam_tru = GIAM_TRU_BAN_THAN + npt * GIAM_TRU_NPT + tong_bh_nld
        tntt = max(tnct - giam_tru, 0)
        tncn = thue_luy_tien(tntt)
        cach = "lũy tiến"
    else:
        giam_tru, tntt = 0.0, tnct
        tncn = round(tnct * 0.10) if tnct >= 5_000_000 else 0
        cach = "10% (từ 5 triệu)" if tncn else "không khấu trừ (<5 triệu)"
        if tncn:
            cb.append("khấu trừ 10%; nếu cả năm chưa tới mức chịu thuế, cá nhân có thể làm cam kết (NĐ 253/2026)")
    if (r.get("chu_dn") or "").strip():
        cb.append("chủ DNTN/TNHH MTV cá nhân: tiền lương không được trừ khi tính TNDN (Luật 67/2025 Đ.9 k.2 điểm h)")
    return {"ma": r.get("ma", ""), "ho_ten": r.get("ho_ten", ""), "loai": loai, "bo_phan": (r.get("bo_phan") or "6422").strip(),
            "gross": gross, "luong_bh": luong_bh, "bh_nld": bh_nld, "bh_dn": bh_dn, "tong_bh_nld": tong_bh_nld,
            "tong_bh_dn": sum(bh_dn.values()), "kpcd": round(min(luong_bh, tran) * KPCD) if luong_bh else 0,
            "tnct": tnct, "giam_tru": giam_tru, "tntt": tntt, "tncn": tncn, "cach": cach,
            "thuc_nhan": gross - tong_bh_nld - tncn, "chu_dn": bool((r.get("chu_dn") or "").strip()), "canh_bao": cb}


def but_toan(ds):
    bt = []
    theo_bp = defaultdict(float)
    for x in ds:
        theo_bp[x["bo_phan"]] += x["gross"]
    for bp, v in sorted(theo_bp.items()):
        bt.append((bp, "334", v, f"Tiền lương phải trả – bộ phận {bp}"))
    bh_dn = defaultdict(float)
    for x in ds:
        for k, v in x["bh_dn"].items():
            bh_dn[(x["bo_phan"], TK[k])] += v
        if x["kpcd"]:
            bh_dn[(x["bo_phan"], "3382")] += x["kpcd"]
    for (bp, tk), v in sorted(bh_dn.items()):
        bt.append((bp, tk, v, "Bảo hiểm, KPCĐ phần DN"))
    nld = defaultdict(float)
    for x in ds:
        for k, v in x["bh_nld"].items():
            nld[TK[k]] += v
    for tk, v in sorted(nld.items()):
        if v:
            bt.append(("334", tk, v, "Khấu trừ bảo hiểm phần NLĐ"))
    tncn = sum(x["tncn"] for x in ds)
    if tncn:
        bt.append(("334", "3335", tncn, "Khấu trừ thuế TNCN"))
    bt.append(("334", "112", sum(x["thuc_nhan"] for x in ds), "Trả lương (chuyển khoản)"))
    return bt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ky", help="tháng lương YYYY-MM (xác định trần BHXH theo lương cơ sở)")
    ap.add_argument("--vung", type=int, choices=[1, 2, 3, 4], default=1, help="vùng lương tối thiểu nơi DN hoạt động")
    ap.add_argument("--luong-toi-thieu", type=so, help="ghi đè lương tối thiểu vùng (vd mức 2027 khi có nghị định)")
    ap.add_argument("--xlsx")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.file or not a.ky:
        ap.error("cần file CSV và --ky YYYY-MM")
    nam, thang = map(int, a.ky.split("-"))
    ky = dt.date(nam, thang, 1)
    if ky >= dt.date(2027, 1, 1) and not a.luong_toi_thieu:
        print("! Từ 01/01/2027 lương tối thiểu vùng thay đổi (dự kiến tăng ~7,8%) – nhập --luong-toi-thieu theo nghị định mới.")
    with open(a.file, encoding="utf-8-sig") as f:
        try:
            ds = [tinh_nguoi(r, ky, a.vung, a.luong_toi_thieu) for r in csv.DictReader(f)]
        except ValueError as e:
            print("✗ " + str(e))
            return 2
    in_bang(ds, ky, a.vung)
    if a.xlsx:
        xuat_xlsx(a.xlsx, ds, ky)
        print(f"Đã ghi {a.xlsx}")
    return 0


def in_bang(ds, ky, vung):
    print(f"BẢNG LƯƠNG THÁNG {ky:%m/%Y} – vùng {vung} – trần BHXH/BHYT {d(tran_bhxh(ky))}\n")
    print(f"{'Mã':6} {'Họ tên':22} {'Tổng TN':>13} {'BH NLĐ':>11} {'TN tính thuế':>13} {'TNCN':>11} {'Thực nhận':>13}  Cách tính TNCN")
    for x in ds:
        print(f"{x['ma']:6} {x['ho_ten'][:22]:22} {d(x['gross']):>13} {d(x['tong_bh_nld']):>11} {d(x['tntt']):>13} "
              f"{d(x['tncn']):>11} {d(x['thuc_nhan']):>13}  {x['cach']}")
    tong = lambda k: sum(x[k] for x in ds)  # noqa: E731
    print(f"{'CỘNG':29} {d(tong('gross')):>13} {d(tong('tong_bh_nld')):>11} {'':>13} {d(tong('tncn')):>11} {d(tong('thuc_nhan')):>13}")
    print(f"\nBảo hiểm phần DN: {d(tong('tong_bh_dn'))} · KPCĐ 2%: {d(tong('kpcd'))} · "
          f"Tổng chi phí lương của DN: {d(tong('gross') + tong('tong_bh_dn') + tong('kpcd'))}")
    print(f"Nộp cơ quan BHXH: {d(tong('tong_bh_dn') + tong('tong_bh_nld'))} (DN + NLĐ) · Nộp thuế TNCN: {d(tong('tncn'))}")
    print("\nBút toán:")
    for no, co, v, dg in but_toan(ds):
        if v:
            print(f"  Nợ {no:5} / Có {co:5} {d(v):>14}  {dg}")
    for x in ds:
        for c in x["canh_bao"]:
            print(f"! {x['ma']} {x['ho_ten']}: {c}")
    print("\nĐã kiểm tra phép tính. Tỷ lệ đóng, trần đóng: đối chiếu thông báo của cơ quan BHXH. TNCN cá nhân (quyết toán, "
          "người phụ thuộc, người nước ngoài): skill tncn (github.com/tndvnn/tncn).")


def xuat_xlsx(path, ds, ky):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = f"Luong {ky:%m-%Y}"
    cot = ["Mã", "Họ tên", "Loại HĐ", "Bộ phận", "Tổng thu nhập", "Lương đóng BH", "BHXH NLĐ", "BHYT NLĐ", "BHTN NLĐ",
           "Thu nhập chịu thuế", "Giảm trừ", "TN tính thuế", "Thuế TNCN", "Thực nhận", "BH phần DN", "KPCĐ"]
    ws.append(cot)
    for c in ws[1]:
        c.font = Font(bold=True)
    for i, x in enumerate(ds, start=2):
        ws.append([x["ma"], x["ho_ten"], x["loai"], x["bo_phan"], x["gross"], x["luong_bh"], x["bh_nld"].get("bhxh", 0),
                   x["bh_nld"].get("bhyt", 0), x["bh_nld"].get("bhtn", 0), x["tnct"], x["giam_tru"], x["tntt"], x["tncn"],
                   f"=E{i}-G{i}-H{i}-I{i}-M{i}", x["tong_bh_dn"], x["kpcd"]])
    n = ws.max_row
    ws.append(["", "CỘNG", "", ""] + [f"=SUM({c}2:{c}{n})" for c in "EFGHIJKLMNOP"])
    for row in ws.iter_rows(min_row=2):
        for c in row[4:]:
            c.number_format = "#,##0"
    ws.column_dimensions["B"].width = 26
    wb.save(path)


def self_test():
    import os
    import tempfile
    assert thue_luy_tien(5e6) == 250_000 and thue_luy_tien(30e6) == 2_500_000 and thue_luy_tien(60e6) == 8_500_000
    assert thue_luy_tien(100e6) == 20_500_000 and thue_luy_tien(120e6) == 27_500_000 and thue_luy_tien(0) == 0
    ky = dt.date(2026, 10, 1)
    # Ví dụ tncn: lương 30tr, đóng BH trên 30tr, 1 NPT → BH 10,5% = 3,15tr; TNTT 5,15tr → thuế 257.500
    a = tinh_nguoi({"ma": "NV1", "loai_hd": "dai", "luong_dong_bh": "30000000", "tong_thu_nhap": "30000000", "so_npt": "1"}, ky, 1)
    assert a["tong_bh_nld"] == 3_150_000 and a["tntt"] == 5_150_000 and a["tncn"] == 257_500, a
    assert a["tong_bh_dn"] == round(30e6 * 0.215) and a["kpcd"] == 600_000
    # vượt trần: BHXH/BHYT tính trên 50,6tr; BHTN trên min(80tr, 106,2tr)
    b = tinh_nguoi({"ma": "NV2", "loai_hd": "dai", "luong_dong_bh": "80000000", "tong_thu_nhap": "80000000"}, ky, 1)
    assert b["bh_nld"]["bhxh"] == 4_048_000 and b["bh_nld"]["bhyt"] == 759_000 and b["bh_nld"]["bhtn"] == 800_000
    assert any("vượt trần" in x for x in b["canh_bao"])
    assert tran_bhxh(dt.date(2026, 6, 1)) == 46_800_000
    c = tinh_nguoi({"ma": "CTV", "loai_hd": "khong", "tong_thu_nhap": "8000000"}, ky, 1)
    assert c["tncn"] == 800_000 and c["tong_bh_nld"] == 0
    e = tinh_nguoi({"ma": "CTV2", "loai_hd": "ngan", "tong_thu_nhap": "4.900.000"}, ky, 1)
    assert e["tncn"] == 0
    f = tinh_nguoi({"ma": "NV3", "loai_hd": "dai", "luong_dong_bh": "6000000", "tong_thu_nhap": "21500000", "an_ca": "1500000"}, ky, 1)
    assert f["tnct"] == 20_300_000 and any("ăn ca" in x for x in f["canh_bao"])
    bt = but_toan([a, c])
    no = sum(v for n_, c_, v, _ in bt if n_ in ("6421", "6422", "154"))
    assert no == 38_000_000 + a["tong_bh_dn"] + a["kpcd"]
    assert sum(v for n_, c_, v, _ in bt if n_ == "334") == 38_000_000  # 334 về 0 sau khi trả lương
    with tempfile.TemporaryDirectory() as t:
        xuat_xlsx(os.path.join(t, "l.xlsx"), [a, b, c], ky)
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
