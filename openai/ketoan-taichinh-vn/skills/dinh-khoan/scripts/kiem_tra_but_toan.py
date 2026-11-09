#!/usr/bin/env python3
"""Kiểm tra bút toán theo hệ thống tài khoản TT133/2016 và lập Sổ Nhật ký chung + tổng hợp phát sinh.

Đầu vào CSV (UTF-8, có dòng tiêu đề), định khoản giản đơn – mỗi dòng 1 cặp Nợ/Có, nhiều dòng cùng so_ct = 1 chứng từ:
    ngay,so_ct,dien_giai,tk_no,tk_co,so_tien
    2026-10-05,PC001,Mua văn phòng phẩm,6422,1111,1200000
Số tiền nhận dạng 1250000 · 1.250.000 · 1,250,000. Tài khoản chi tiết (vd 131-KH01, 3311A) được chấp nhận nếu bắt đầu bằng số hiệu TT133.

Kiểm tra: tài khoản có trong TT133 (gắn cờ tài khoản chỉ có ở TT200/TT99 như 521, 641, 113, 344, 347);
642/133/333/338 chưa chi tiết; tổng Nợ = tổng Có; chi tiền mặt từ 5 triệu/chứng từ (mất khấu trừ GTGT – NĐ 181/2025 Đ.26,
không được trừ chi phí TNDN – NĐ 320/2025) [ngưỡng cần kiểm tra]; Nợ 133 đối ứng bất thường.

  python3 kiem_tra_but_toan.py but_toan.csv
  python3 kiem_tra_but_toan.py but_toan.csv --xlsx so_nhat_ky_chung.xlsx --phat-sinh phat_sinh.csv
"""
import argparse
import csv
import datetime as dt
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

NGUONG_TIEN_MAT = 5_000_000
CHI_TT200 = {"521": "TT133 không có 521 – giảm trừ doanh thu ghi Nợ 511",
             "641": "TT133 gộp chi phí bán hàng vào 6421",
             "113": "TT133 không có 113 Tiền đang chuyển",
             "344": "TT133 dùng 3386 cho nhận ký quỹ",
             "244": "TT133 dùng 1386 cho ký quỹ",
             "347": "TT133 không có thuế TNDN hoãn lại",
             "243": "TT133 không có tài sản thuế TNDN hoãn lại",
             "161": "TT133 không có 161",
             "466": "TT133 không có 466"}
CAN_CHI_TIET = {"642": "dùng 6421 (bán hàng) hoặc 6422 (quản lý)",
                "133": "dùng 1331 hoặc 1332",
                "333": "dùng 3331/33311, 3334, 3335…",
                "338": "dùng 3382–3388"}


def tim_file_tk():
    for p in (Path(__file__).resolve().parent.parent / "references" / "tai-khoan-tt133.csv",
              Path(__file__).resolve().parents[3] / "shared" / "tai-khoan-tt133.csv"):
        if p.exists():
            return p
    raise FileNotFoundError("không tìm thấy tai-khoan-tt133.csv (chạy scripts/build.py để đồng bộ references)")


def doc_tai_khoan(path=None):
    with open(path or tim_file_tk(), encoding="utf-8") as f:
        return {r["so_hieu"]: r for r in csv.DictReader(f)}


def so(s):
    s = str(s).strip().replace(" ", "").replace("đ", "")
    if not s:
        raise ValueError("số tiền trống")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "." in s and re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    elif "," in s:
        s = s.replace(",", "") if re.fullmatch(r"-?\d{1,3}(,\d{3})+", s) else s.replace(",", ".")
    return float(s)


def ma_goc(tk, dm):
    """Trả về số hiệu TT133 dài nhất là tiền tố của tk (bỏ ký tự phân cách)."""
    t = re.sub(r"[^0-9A-Za-z]", "", str(tk))
    so_hieu = re.match(r"\d+", t)
    if not so_hieu:
        return None
    d = so_hieu.group(0)
    for n in range(len(d), 2, -1):
        if d[:n] in dm:
            return d[:n]
    return None


def kiem_tra(dong, dm):
    loi, canh_bao = [], []
    ct = defaultdict(list)
    ps = defaultdict(lambda: [0.0, 0.0])
    tong_no = tong_co = 0.0
    for i, r in enumerate(dong, start=2):
        try:
            tien = so(r["so_tien"])
        except (ValueError, KeyError) as e:
            loi.append(f"Dòng {i}: số tiền không đọc được ({e})")
            continue
        if tien <= 0:
            loi.append(f"Dòng {i}: số tiền phải > 0 (đảo Nợ/Có thay vì ghi âm)")
            continue
        for ben in ("tk_no", "tk_co"):
            tk = str(r.get(ben, "")).strip()
            goc = ma_goc(tk, dm)
            ma3 = re.sub(r"\D", "", tk)[:3]
            if ma3 in CHI_TT200:
                loi.append(f"Dòng {i}: TK {tk} – {CHI_TT200[ma3]}")
            elif goc is None:
                loi.append(f"Dòng {i}: TK {tk!r} không có trong hệ thống tài khoản TT133")
            elif goc in CAN_CHI_TIET and re.sub(r"\D", "", tk) == goc:
                canh_bao.append(f"Dòng {i}: TK {tk} chưa chi tiết – {CAN_CHI_TIET[goc]}")
        g_no, g_co = ma_goc(r["tk_no"], dm), ma_goc(r["tk_co"], dm)
        if g_no and g_co:
            ps[g_no][0] += tien
            ps[g_co][1] += tien
            tong_no += tien
            tong_co += tien
            if g_no.startswith("133") and not g_co[:3] in {"111", "112", "331", "141", "333"}:
                canh_bao.append(f"Dòng {i}: Nợ {r['tk_no']} đối ứng Có {r['tk_co']} – kiểm tra hóa đơn đầu vào")
            if g_no[:1] in "56789" and g_co[:1] in "56789" and not (g_no == "911" or g_co == "911"):
                canh_bao.append(f"Dòng {i}: đối ứng {g_no}/{g_co} giữa hai tài khoản kết quả – thường chỉ qua 911")
        ct[(r.get("so_ct") or f"dòng{i}", r.get("ngay", ""))].append((g_no, g_co, tien))
    for (so_ct, ngay), ds in ct.items():
        tien_mat = sum(t for n, c, t in ds if c and c.startswith("111") and n and not n.startswith(("112", "141", "1111", "1121")))
        if tien_mat >= NGUONG_TIEN_MAT:
            co_thue = any(n and n.startswith("133") for n, c, t in ds)
            luong = any(n and n.startswith("334") for n, c, t in ds)
            vi_sao = "có thuế GTGT đầu vào → không được khấu trừ GTGT" if co_thue else ("trả lương" if luong else "khoản chi")
            canh_bao.append(f"Chứng từ {so_ct} ({ngay}): chi tiền mặt {tien_mat:,.0f} đồng ≥ 5 triệu ({vi_sao}); "
                            "không được trừ chi phí TNDN nếu không chuyển khoản [cần kiểm tra]".replace(",", "."))
    if abs(tong_no - tong_co) > 0.5:
        loi.append(f"Tổng Nợ {tong_no:,.0f} ≠ tổng Có {tong_co:,.0f}")
    return loi, canh_bao, ps, tong_no


def xuat_xlsx(path, dong, ps, dm):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "Nhat ky chung"
    ws.append(["SỔ NHẬT KÝ CHUNG (mẫu S03a-DNN – tham khảo)"])
    ws["A1"].font = Font(bold=True)
    ws.append(["Ngày", "Số CT", "Diễn giải", "TK Nợ", "TK Có", "Số tiền"])
    for c in ws[2]:
        c.font = Font(bold=True)
    for r in dong:
        try:
            tien = so(r["so_tien"])
        except ValueError:
            continue
        ws.append([r.get("ngay"), r.get("so_ct"), r.get("dien_giai"), str(r["tk_no"]), str(r["tk_co"]), tien])
    n = ws.max_row
    ws.append(["", "", "Cộng", "", "", f"=SUM(F3:F{n})"])
    ws.column_dimensions["C"].width = 40
    ws2 = wb.create_sheet("Tong hop phat sinh")
    ws2.append(["Số hiệu", "Tên tài khoản", "Phát sinh Nợ", "Phát sinh Có"])
    for c in ws2[1]:
        c.font = Font(bold=True)
    for tk in sorted(ps):
        ws2.append([tk, dm[tk]["ten"], ps[tk][0], ps[tk][1]])
    m = ws2.max_row
    ws2.append(["", "Cộng", f"=SUM(C2:C{m})", f"=SUM(D2:D{m})"])
    ws2.column_dimensions["B"].width = 45
    for w in (ws, ws2):
        for row in w.iter_rows():
            for c in row:
                if isinstance(c.value, (int, float)) or (isinstance(c.value, str) and c.value.startswith("=SUM")):
                    c.number_format = "#,##0"
    wb.save(path)


def doc_csv(path_or_text):
    if isinstance(path_or_text, io.StringIO):
        return list(csv.DictReader(path_or_text))
    with open(path_or_text, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--xlsx", help="xuất Sổ Nhật ký chung + tổng hợp phát sinh ra Excel")
    ap.add_argument("--phat-sinh", help="xuất CSV phát sinh theo tài khoản (so_hieu,ps_no,ps_co)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.file:
        ap.error("cần file CSV bút toán")
    dm = doc_tai_khoan()
    dong = doc_csv(a.file)
    loi, cb, ps, tong = kiem_tra(dong, dm)
    print(f"Đã đọc {len(dong)} dòng bút toán. Tổng phát sinh: {tong:,.0f} đồng.".replace(",", "."))
    print(f"\nLỖI ({len(loi)}):" if loi else "\nKhông có lỗi chặn.")
    for x in loi:
        print("  ✗ " + x)
    if cb:
        print(f"\nCẢNH BÁO ({len(cb)}):")
        for x in cb:
            print("  ! " + x)
    print("\nTổng hợp phát sinh theo tài khoản:")
    for tk in sorted(ps):
        print(f"  {tk:6} {dm[tk]['ten'][:42]:42} Nợ {ps[tk][0]:>16,.0f}  Có {ps[tk][1]:>16,.0f}".replace(",", "."))
    if a.phat_sinh:
        with open(a.phat_sinh, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["so_hieu", "ps_no", "ps_co"])
            for tk in sorted(ps):
                w.writerow([tk, round(ps[tk][0]), round(ps[tk][1])])
        print(f"\nĐã ghi {a.phat_sinh}")
    if a.xlsx:
        xuat_xlsx(a.xlsx, dong, ps, dm)
        print(f"Đã ghi {a.xlsx}")
    print("Đã kiểm tra phép tính. Bút toán là bản nháp – kế toán viên xác nhận trước khi ghi sổ chính thức.")
    return 1 if loi else 0


def self_test():
    dm = doc_tai_khoan()
    assert so("1.250.000") == 1250000 and so("1,250,000") == 1250000 and so("1250000") == 1250000 and so("1.250.000,5") == 1250000.5
    assert ma_goc("131-KH01", dm) == "131" and ma_goc("33311", dm) == "33311" and ma_goc("6421", dm) == "6421" and ma_goc("999", dm) is None
    du_lieu = io.StringIO(
        "ngay,so_ct,dien_giai,tk_no,tk_co,so_tien\n"
        "2026-10-01,PN01,Mua hàng,156,331,10.000.000\n"
        "2026-10-01,PN01,Thuế GTGT,1331,331,1.000.000\n"
        "2026-10-02,PC01,Chi tiếp khách,6422,1111,6.000.000\n"
        "2026-10-02,PC01,Thuế GTGT,1331,1111,480.000\n"
        "2026-10-03,BH01,Bán hàng,131,5111,20000000\n"
        "2026-10-03,BH01,Thuế,131,33311,2000000\n"
        "2026-10-04,X01,Chiết khấu,521,131,100000\n"
        "2026-10-05,X02,Chi phí,642,1121,300000\n")
    dong = doc_csv(du_lieu)
    loi, cb, ps, tong = kiem_tra(dong, dm)
    assert any("521" in x for x in loi), loi
    assert any("PC01" in x and "khấu trừ" in x for x in cb), cb
    assert any("642" in x and "chưa chi tiết" in x for x in cb), cb
    assert ps["156"][0] == 10_000_000 and ps["331"][1] == 11_000_000
    assert abs(tong - 39_480_000 - 300_000) < 1
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        xuat_xlsx(Path(d) / "t.xlsx", dong, ps, dm)
        assert (Path(d) / "t.xlsx").stat().st_size > 0
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
