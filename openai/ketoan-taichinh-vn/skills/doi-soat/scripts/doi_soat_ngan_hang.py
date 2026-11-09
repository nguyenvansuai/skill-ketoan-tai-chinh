#!/usr/bin/env python3
"""Đối chiếu sổ tiền gửi ngân hàng (TK 112) với sao kê ngân hàng; lập bảng điều chỉnh số dư.

Sổ (CSV): ngay,so_ct,dien_giai,thu,chi          – thu = ghi Nợ 112, chi = ghi Có 112
Sao kê (CSV): ngay,mo_ta,thu,chi                 – thu = ghi có tài khoản (tiền vào), chi = ghi nợ (tiền ra)
Ngày dạng YYYY-MM-DD hoặc DD/MM/YYYY; số tiền 1.250.000 / 1,250,000 / 1250000.

Ghép cặp: cùng chiều, cùng số tiền, ngày lệch không quá --lech-ngay (mặc định 5), ưu tiên ngày gần nhất.
Khoản chỉ có trên sao kê: phí ngân hàng, lãi, khách chuyển chưa ghi sổ → gợi ý bút toán.
Khoản chỉ có trên sổ: séc/ủy nhiệm chi chưa trừ, tiền đang chuyển, hoặc ghi sổ sai.

  python3 doi_soat_ngan_hang.py so_112.csv sao_ke.csv --so-du-so 150000000 --so-du-sao-ke 148500000 --xlsx doi_soat.xlsx
"""
import argparse
import csv
import datetime as dt
import re
import sys
import unicodedata


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
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError(f"ngày không đọc được: {s!r}")


def bo_dau(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("đ", "d")


def doc(path, cot_mo_ta):
    with open(path, encoding="utf-8-sig") as f:
        out = []
        for i, r in enumerate(csv.DictReader(f), start=2):
            thu, chi = so(r.get("thu")), so(r.get("chi"))
            if thu and chi:
                raise ValueError(f"{path} dòng {i}: một dòng chỉ được có thu hoặc chi")
            if not thu and not chi:
                continue
            out.append({"id": f"{path.split('/')[-1]}:{i}", "ngay": ngay(r["ngay"]), "mo_ta": r.get(cot_mo_ta, "") or "",
                        "so_ct": r.get("so_ct", ""), "chieu": "vao" if thu else "ra", "tien": thu or chi})
        return out


def ghep(so_sach, sao_ke, lech_ngay):
    cap, con_sk = [], list(sao_ke)
    con_so = []
    for s in sorted(so_sach, key=lambda x: x["ngay"]):
        ung = [k for k in con_sk if k["chieu"] == s["chieu"] and abs(k["tien"] - s["tien"]) < 0.5
               and abs((k["ngay"] - s["ngay"]).days) <= lech_ngay]
        if ung:
            k = min(ung, key=lambda k: abs((k["ngay"] - s["ngay"]).days))
            con_sk.remove(k)
            cap.append((s, k))
        else:
            con_so.append(s)
    return cap, con_so, con_sk


def goi_y(k):
    m = bo_dau(k["mo_ta"])
    if k["chieu"] == "ra" and re.search(r"phi|fee|charge|sms|duy tri|quan ly tai khoan", m):
        return "Phí ngân hàng chưa ghi sổ: Nợ 6422 (+1331 nếu có hóa đơn) / Có 112"
    if k["chieu"] == "vao" and re.search(r"lai|interest", m):
        return "Lãi tiền gửi chưa ghi sổ: Nợ 112 / Có 515"
    if k["chieu"] == "ra" and re.search(r"thue|ngan sach|nsnn|kbnn|bhxh", m):
        return "Nộp thuế/bảo hiểm chưa ghi sổ: Nợ 333x/338x / Có 112 – xác định loại"
    if k["chieu"] == "vao":
        return "Tiền vào chưa ghi sổ: xác định người nộp → Nợ 112 / Có 131 (hoặc 3411, 4111, 711…)"
    return "Tiền ra chưa ghi sổ: xác định chứng từ → Nợ 331/334/6422… / Có 112"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("so", nargs="?")
    ap.add_argument("sao_ke", nargs="?")
    ap.add_argument("--lech-ngay", type=int, default=5)
    ap.add_argument("--so-du-so", type=so, help="số dư cuối kỳ TK 112 trên sổ")
    ap.add_argument("--so-du-sao-ke", type=so, help="số dư cuối kỳ trên sao kê")
    ap.add_argument("--xlsx")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.so or not a.sao_ke:
        ap.error("cần file sổ 112 và file sao kê")
    so_sach, sao_ke = doc(a.so, "dien_giai"), doc(a.sao_ke, "mo_ta")
    cap, con_so, con_sk = ghep(so_sach, sao_ke, a.lech_ngay)
    bao_cao(cap, con_so, con_sk, a.so_du_so, a.so_du_sao_ke)
    if a.xlsx:
        xuat(a.xlsx, cap, con_so, con_sk)
        print(f"Đã ghi {a.xlsx}")
    return 0


def d(x):
    return f"{x:,.0f}".replace(",", ".")


def bao_cao(cap, con_so, con_sk, sd_so, sd_sk):
    print(f"Khớp {len(cap)} cặp. Chỉ có trên sổ: {len(con_so)}. Chỉ có trên sao kê: {len(con_sk)}.")
    if con_sk:
        print("\nCHỈ CÓ TRÊN SAO KÊ (chưa ghi sổ):")
        for k in con_sk:
            print(f"  {k['ngay']:%d/%m/%Y} {'+' if k['chieu'] == 'vao' else '-'}{d(k['tien']):>15}  {k['mo_ta'][:50]}")
            print(f"{'':30}→ {goi_y(k)}")
    if con_so:
        print("\nCHỈ CÓ TRÊN SỔ (ngân hàng chưa ghi nhận hoặc ghi sổ sai):")
        for s in con_so:
            print(f"  {s['ngay']:%d/%m/%Y} {'+' if s['chieu'] == 'vao' else '-'}{d(s['tien']):>15}  {s['so_ct']} {s['mo_ta'][:45]}")
    if sd_so is not None and sd_sk is not None:
        sk_vao = sum(k["tien"] for k in con_sk if k["chieu"] == "vao")
        sk_ra = sum(k["tien"] for k in con_sk if k["chieu"] == "ra")
        so_vao = sum(s["tien"] for s in con_so if s["chieu"] == "vao")
        so_ra = sum(s["tien"] for s in con_so if s["chieu"] == "ra")
        dc_sk = sd_sk + so_vao - so_ra
        dc_so = sd_so + sk_vao - sk_ra
        print("\nBẢNG ĐIỀU CHỈNH SỐ DƯ")
        print(f"  Số dư theo sao kê                         {d(sd_sk):>16}")
        print(f"  + Tiền vào đã ghi sổ, NH chưa ghi nhận    {d(so_vao):>16}")
        print(f"  − Tiền ra đã ghi sổ, NH chưa trừ          {d(so_ra):>16}")
        print(f"  = Số dư sao kê sau điều chỉnh             {d(dc_sk):>16}")
        print(f"  Số dư theo sổ TK 112                      {d(sd_so):>16}")
        print(f"  + Tiền vào trên sao kê chưa ghi sổ        {d(sk_vao):>16}")
        print(f"  − Tiền ra trên sao kê chưa ghi sổ         {d(sk_ra):>16}")
        print(f"  = Số dư sổ sau điều chỉnh                 {d(dc_so):>16}")
        chenh = dc_so - dc_sk
        print(f"  CHÊNH LỆCH CÒN LẠI                        {d(chenh):>16}" + ("  ✓ khớp" if abs(chenh) < 1 else "  ✗ cần tìm nguyên nhân (ghi sai số tiền, ghi trùng, sai ngày khóa sổ)"))
    print("\nĐã kiểm tra phép tính. Bút toán điều chỉnh là gợi ý – kế toán xác nhận chứng từ trước khi ghi sổ.")


def xuat(path, cap, con_so, con_sk):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Da khop"
    ws.append(["Ngày sổ", "Số CT", "Diễn giải sổ", "Ngày sao kê", "Mô tả sao kê", "Chiều", "Số tiền"])
    for s, k in cap:
        ws.append([s["ngay"], s["so_ct"], s["mo_ta"], k["ngay"], k["mo_ta"], s["chieu"], s["tien"]])
    ws2 = wb.create_sheet("Chi co tren sao ke")
    ws2.append(["Ngày", "Mô tả", "Chiều", "Số tiền", "Gợi ý bút toán"])
    for k in con_sk:
        ws2.append([k["ngay"], k["mo_ta"], k["chieu"], k["tien"], goi_y(k)])
    ws3 = wb.create_sheet("Chi co tren so")
    ws3.append(["Ngày", "Số CT", "Diễn giải", "Chiều", "Số tiền"])
    for s in con_so:
        ws3.append([s["ngay"], s["so_ct"], s["mo_ta"], s["chieu"], s["tien"]])
    for w in wb.worksheets:
        for row in w.iter_rows(min_row=2):
            for c in row:
                if isinstance(c.value, dt.date):
                    c.number_format = "DD/MM/YYYY"
                elif isinstance(c.value, float):
                    c.number_format = "#,##0"
    wb.save(path)


def self_test():
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        p_so, p_sk = os.path.join(t, "so.csv"), os.path.join(t, "sk.csv")
        with open(p_so, "w", encoding="utf-8") as f:
            f.write("ngay,so_ct,dien_giai,thu,chi\n2026-10-02,BC01,Thu tiền KH A,11.000.000,\n"
                    "2026-10-05,UNC01,Trả NCC B,,5.400.000\n2026-10-30,UNC02,Trả NCC C,,2.000.000\n")
        with open(p_sk, "w", encoding="utf-8") as f:
            f.write("ngay,mo_ta,thu,chi\n03/10/2026,CTY A CHUYEN TIEN,11000000,\n05/10/2026,TT NCC B,,5400000\n"
                    "31/10/2026,Phi quan ly tai khoan,,22000\n31/10/2026,Tra lai tien gui,15000,\n")
        cap, con_so, con_sk = ghep(doc(p_so, "dien_giai"), doc(p_sk, "mo_ta"), 5)
        assert len(cap) == 2 and len(con_so) == 1 and len(con_sk) == 2
        assert "6422" in goi_y(con_sk[0]) and "515" in goi_y(con_sk[1])
        # sổ 100tr, sao kê = 100 − (−2tr chưa trừ) − 22k + 15k → 101.993.000
        bao_cao(cap, con_so, con_sk, 100_000_000, 101_993_000)
        xuat(os.path.join(t, "x.xlsx"), cap, con_so, con_sk)
    assert so("1.250.000") == 1250000 and so("1,250,000") == 1250000 and so("") == 0
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
