#!/usr/bin/env python3
"""Lập nháp Báo cáo tình hình tài chính (B01a-DNN), Kết quả kinh doanh (B02-DNN) và Bảng cân đối tài khoản (F01-DNN)
theo TT 133/2016 từ bảng cân đối số phát sinh TRƯỚC bút toán kết chuyển cuối năm.

CSV: so_hieu,ten,du_no_dau,du_co_dau,ps_no,ps_co,du_no_cuoi,du_co_cuoi
- Có thể có cả tài khoản cấp 1 và chi tiết: script chỉ cộng dòng "lá" (dòng không có tài khoản con trong file) → không cộng trùng.
- Tài khoản lưỡng tính (131, 331, 138, 338, 333…): ghi riêng TỔNG DƯ NỢ và TỔNG DƯ CÓ của các đối tượng chi tiết
  (lấy từ bảng tổng hợp công nợ), KHÔNG bù trừ thành một số.
- Bảng phải là số liệu TRƯỚC kết chuyển 911 (TK 911 không phát sinh): lợi nhuận kỳ này được cộng vào chỉ tiêu 417.

  python3 lap_bctc.py can_doi_phat_sinh.csv --ten-dn "Công ty TNHH ABC" --nam 2026 --giam-tru 15000000 --lai-vay 42000000 --xlsx bctc_2026.xlsx

Ánh xạ tài khoản → chỉ tiêu: references/mau-bctc-tt133.md (theo hướng dẫn lập TT133 – [cần kiểm tra] khi DN có nghiệp vụ đặc thù).
"""
import argparse
import csv
import io
import re
import sys

B02 = [("01", "Doanh thu bán hàng và cung cấp dịch vụ"), ("02", "Các khoản giảm trừ doanh thu"),
       ("10", "Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 − 02)"), ("11", "Giá vốn hàng bán"),
       ("20", "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ (20 = 10 − 11)"), ("21", "Doanh thu hoạt động tài chính"),
       ("22", "Chi phí tài chính"), ("23", "   Trong đó: Chi phí lãi vay"), ("24", "Chi phí quản lý kinh doanh"),
       ("30", "Lợi nhuận thuần từ hoạt động kinh doanh (30 = 20 + 21 − 22 − 24)"), ("31", "Thu nhập khác"),
       ("32", "Chi phí khác"), ("40", "Lợi nhuận khác (40 = 31 − 32)"), ("50", "Tổng lợi nhuận kế toán trước thuế (50 = 30 + 40)"),
       ("51", "Chi phí thuế TNDN"), ("60", "Lợi nhuận sau thuế thu nhập doanh nghiệp (60 = 50 − 51)")]
B02_CONG_THUC = {"10": "01-02", "20": "10-11", "30": "20+21-22-24", "40": "31-32", "50": "30+40", "60": "50-51"}

B01 = [
    ("", "TÀI SẢN"), ("110", "I. Tiền và các khoản tương đương tiền"), ("120", "II. Đầu tư tài chính"),
    ("121", "1. Chứng khoán kinh doanh"), ("122", "2. Đầu tư nắm giữ đến ngày đáo hạn"), ("123", "3. Đầu tư góp vốn vào đơn vị khác"),
    ("124", "4. Dự phòng tổn thất đầu tư tài chính (*)"), ("130", "III. Các khoản phải thu"), ("131", "1. Phải thu của khách hàng"),
    ("132", "2. Trả trước cho người bán"), ("133", "3. Vốn kinh doanh ở đơn vị trực thuộc"), ("134", "4. Phải thu khác"),
    ("135", "5. Tài sản thiếu chờ xử lý"), ("136", "6. Dự phòng phải thu khó đòi (*)"), ("140", "IV. Hàng tồn kho"),
    ("141", "1. Hàng tồn kho"), ("142", "2. Dự phòng giảm giá hàng tồn kho (*)"), ("150", "V. Tài sản cố định"),
    ("151", "- Nguyên giá"), ("152", "- Giá trị hao mòn lũy kế (*)"), ("160", "VI. Bất động sản đầu tư"), ("161", "- Nguyên giá"),
    ("162", "- Giá trị hao mòn lũy kế (*)"), ("170", "VII. Xây dựng cơ bản dở dang"), ("180", "VIII. Tài sản khác"),
    ("181", "1. Thuế GTGT được khấu trừ"), ("182", "2. Tài sản khác"), ("200", "TỔNG CỘNG TÀI SẢN"),
    ("", "NGUỒN VỐN"), ("300", "I. Nợ phải trả"), ("311", "1. Phải trả người bán"), ("312", "2. Người mua trả tiền trước"),
    ("313", "3. Thuế và các khoản phải nộp Nhà nước"), ("314", "4. Phải trả người lao động"), ("315", "5. Phải trả khác"),
    ("316", "6. Vay và nợ thuê tài chính"), ("317", "7. Phải trả nội bộ về vốn kinh doanh"), ("318", "8. Dự phòng phải trả"),
    ("319", "9. Quỹ khen thưởng, phúc lợi"), ("320", "10. Quỹ phát triển khoa học và công nghệ"), ("400", "II. Vốn chủ sở hữu"),
    ("411", "1. Vốn góp của chủ sở hữu"), ("412", "2. Thặng dư vốn cổ phần"), ("413", "3. Vốn khác của chủ sở hữu"),
    ("414", "4. Cổ phiếu quỹ (*)"), ("415", "5. Chênh lệch tỷ giá hối đoái"), ("416", "6. Các quỹ thuộc vốn chủ sở hữu"),
    ("417", "7. Lợi nhuận sau thuế chưa phân phối"), ("500", "TỔNG CỘNG NGUỒN VỐN"),
]
B01_TONG = {"120": ["121", "122", "123", "124"], "130": ["131", "132", "133", "134", "135", "136"], "140": ["141", "142"],
            "150": ["151", "152"], "160": ["161", "162"], "180": ["181", "182"],
            "200": ["110", "120", "130", "140", "150", "160", "170", "180"],
            "300": [f"3{i:02d}" for i in range(11, 21)], "400": [f"4{i:02d}" for i in range(11, 18)], "500": ["300", "400"]}


def so(s):
    s = str(s or "").strip().replace(" ", "")
    if not s or s == "-":
        return 0.0
    am = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", s):
        s = s.replace(",", "")
    v = float(s)
    return -v if am else v


class CDPS:
    def __init__(self, rows):
        self.rows = []
        for r in rows:
            ma = re.sub(r"[^0-9A-Za-z]", "", str(r["so_hieu"]))
            if not ma:
                continue
            self.rows.append({"ma": ma, "ten": r.get("ten", ""), **{k: so(r.get(k)) for k in
                              ("du_no_dau", "du_co_dau", "ps_no", "ps_co", "du_no_cuoi", "du_co_cuoi")}})
        mas = [r["ma"] for r in self.rows]
        self.la = [r for r in self.rows if not any(m != r["ma"] and m.startswith(r["ma"]) for m in mas)]

    def tong(self, cot, *tien_to, tru=()):
        return sum(r[cot] for r in self.la if r["ma"].startswith(tien_to) and not r["ma"].startswith(tuple(tru) or ("\0",)))

    def ps_rong(self, tk, ben):
        no, co = self.tong("ps_no", tk), self.tong("ps_co", tk)
        return co - no if ben == "co" else no - co


def lap_b02(c, giam_tru=0.0, lai_vay=None):
    v = {}
    v["10"] = c.ps_rong("511", "co")
    v["02"] = giam_tru
    v["01"] = v["10"] + giam_tru
    v["11"] = c.ps_rong("632", "no")
    v["21"] = c.ps_rong("515", "co")
    v["22"] = c.ps_rong("635", "no")
    v["23"] = lai_vay if lai_vay is not None else 0.0
    v["24"] = c.ps_rong("642", "no")
    v["31"] = c.ps_rong("711", "co")
    v["32"] = c.ps_rong("811", "no")
    v["51"] = c.ps_rong("821", "no")
    v["20"] = v["10"] - v["11"]
    v["30"] = v["20"] + v["21"] - v["22"] - v["24"]
    v["40"] = v["31"] - v["32"]
    v["50"] = v["30"] + v["40"]
    v["60"] = v["50"] - v["51"]
    return v


def lap_b01(c, ky, loi_nhuan_ky=0.0):
    no, co = ("du_no_cuoi", "du_co_cuoi") if ky == "cuoi" else ("du_no_dau", "du_co_dau")
    N = lambda *p, tru=(): c.tong(no, *p, tru=tru)  # noqa: E731
    C = lambda *p, tru=(): c.tong(co, *p, tru=tru)  # noqa: E731
    v = {
        "110": N("111", "112"), "121": N("121"), "122": N("128"), "123": N("228"), "124": -C("2291", "2292"),
        "131": N("131"), "132": N("331"), "133": N("1361"), "134": N("1368", "1386", "1388", "141", "334", "338"),
        "135": N("1381"), "136": -C("2293"), "141": N("151", "152", "153", "154", "155", "156", "157"), "142": -C("2294"),
        "151": N("211"), "152": -C("2141", "2142", "2143"), "161": N("217"), "162": -C("2147"), "170": N("241"),
        "181": N("133"), "182": N("242", "333"),
        "311": C("331"), "312": C("131"), "313": C("333"), "314": C("334"), "315": C("335", "3368", "338", "1388", "1386"),
        "316": C("341"), "317": C("3361"), "318": C("352"), "319": C("353"), "320": C("356"),
        "411": C("4111"), "412": C("4112") - N("4112"), "413": C("4118"), "414": -N("419"), "415": C("413") - N("413"),
        "416": C("418"), "417": C("421") - N("421") + loi_nhuan_ky,
    }
    for ma, con in B01_TONG.items():
        v[ma] = sum(v[x] for x in con)
    return v


def kiem_tra(c, v_cuoi, v_dau):
    loi, cb = [], []
    kq = ("5", "6", "7", "8")

    def du_cuoi(r, ben):
        # Bảng trước kết chuyển: TK loại 5–8 có thể để trống cột dư cuối – lấy phát sinh ròng làm số dư
        if r["ma"].startswith(kq) and not r["du_no_cuoi"] and not r["du_co_cuoi"]:
            rong = r["ps_no"] - r["ps_co"]
            return max(rong, 0) if ben == "no" else max(-rong, 0)
        return r["du_no_cuoi"] if ben == "no" else r["du_co_cuoi"]

    cap_kt = [("dư đầu kỳ", lambda r: r["du_no_dau"], lambda r: r["du_co_dau"]),
              ("phát sinh", lambda r: r["ps_no"], lambda r: r["ps_co"]),
              ("dư cuối kỳ", lambda r: du_cuoi(r, "no"), lambda r: du_cuoi(r, "co"))]
    for nhan, fn, fc in cap_kt:
        a, b = sum(fn(r) for r in c.la), sum(fc(r) for r in c.la)
        if abs(a - b) > 1:
            loi.append(f"Bảng cân đối không cân ở {nhan}: Nợ {a:,.0f} ≠ Có {b:,.0f}".replace(",", "."))
    if c.tong("ps_no", "911") or c.tong("ps_co", "911"):
        loi.append("TK 911 đã có phát sinh – cần bảng TRƯỚC bút toán kết chuyển cuối năm (hoặc bỏ các bút toán kết chuyển khỏi phát sinh).")
    for tk in ("111", "112", "15", "211"):
        if c.tong("du_co_cuoi", tk):
            cb.append(f"TK {tk}* có dư Có – tài sản âm, kiểm tra sổ")
    for nhan, v in (("cuối kỳ", v_cuoi), ("đầu kỳ", v_dau)):
        if abs(v["200"] - v["500"]) > 1:
            loi.append(f"B01a {nhan}: Tổng tài sản {v['200']:,.0f} ≠ Tổng nguồn vốn {v['500']:,.0f} (chênh {v['200'] - v['500']:,.0f})".replace(",", "."))
    return loi, cb


def d(x):
    s = f"{abs(x):,.0f}".replace(",", ".")
    return f"({s})" if x < 0 else s


def xuat_xlsx(path, c, b01c, b01d, b02, ten_dn, nam):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "B01a-DNN"
    ws.append([ten_dn])
    ws.append([f"BÁO CÁO TÌNH HÌNH TÀI CHÍNH – Mẫu B01a-DNN (TT 133/2016) – năm {nam} – BẢN NHÁP"])
    ws.append(["Chỉ tiêu", "Mã số", "Số cuối năm", "Số đầu năm"])
    for row in ws.iter_rows(max_row=3):
        for x in row:
            x.font = Font(bold=True)
    vi_tri = {}
    for ma, ten in B01:
        r = ws.max_row + 1
        if not ma:
            ws.append([ten])
            ws.cell(r, 1).font = Font(bold=True)
            continue
        vi_tri[ma] = r
        ws.append([ten, ma, b01c[ma], b01d[ma]])
    for ma, con in B01_TONG.items():
        r = vi_tri[ma]
        for col in "CD":
            ws[f"{col}{r}"] = "=" + "+".join(f"{col}{vi_tri[x]}" for x in con)
        ws.cell(r, 1).font = Font(bold=True)
    ws.append([])
    ws.append(["Kiểm tra 200 − 500 (phải bằng 0)", "", f"=C{vi_tri['200']}-C{vi_tri['500']}", f"=D{vi_tri['200']}-D{vi_tri['500']}"])
    ws.column_dimensions["A"].width = 58
    ws2 = wb.create_sheet("B02-DNN")
    ws2.append([ten_dn])
    ws2.append([f"BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH – Mẫu B02-DNN – năm {nam} – BẢN NHÁP"])
    ws2.append(["Chỉ tiêu", "Mã số", "Năm nay"])
    vt2 = {}
    for ma, ten in B02:
        vt2[ma] = ws2.max_row + 1
        ws2.append([ten, ma, b02[ma]])
    for ma, ct in B02_CONG_THUC.items():
        bieu = re.sub(r"\d\d", lambda m: f"C{vt2[m.group(0)]}", ct)
        ws2[f"C{vt2[ma]}"] = "=" + bieu
        ws2.cell(vt2[ma], 1).font = Font(bold=True)
    ws2.column_dimensions["A"].width = 64
    ws3 = wb.create_sheet("F01-DNN")
    ws3.append(["BẢNG CÂN ĐỐI TÀI KHOẢN – Mẫu F01-DNN (dòng chi tiết cuối cùng)"])
    ws3.append(["Số hiệu", "Tên", "Dư Nợ đầu", "Dư Có đầu", "PS Nợ", "PS Có", "Dư Nợ cuối", "Dư Có cuối"])
    for r in c.la:
        ws3.append([r["ma"], r["ten"], r["du_no_dau"], r["du_co_dau"], r["ps_no"], r["ps_co"], r["du_no_cuoi"], r["du_co_cuoi"]])
    n = ws3.max_row
    ws3.append(["", "CỘNG"] + [f"=SUM({col}3:{col}{n})" for col in "CDEFGH"])
    ws3.column_dimensions["B"].width = 40
    for w in (ws, ws2, ws3):
        for row in w.iter_rows(min_row=3):
            for x in row:
                if isinstance(x.value, (int, float)) or (isinstance(x.value, str) and x.value.startswith("=")):
                    x.number_format = "#,##0;(#,##0)"
    wb.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ten-dn", default="[CẦN BỔ SUNG: tên doanh nghiệp]")
    ap.add_argument("--nam", default="[năm]")
    ap.add_argument("--giam-tru", type=so, default=0.0, help="các khoản giảm trừ doanh thu (Nợ 511 đối ứng 111/112/131) – chỉ tiêu 02")
    ap.add_argument("--lai-vay", type=so, help="chi phí lãi vay trong 635 – chỉ tiêu 23")
    ap.add_argument("--xlsx")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.file:
        ap.error("cần file bảng cân đối số phát sinh CSV")
    with open(a.file, encoding="utf-8-sig") as f:
        c = CDPS(list(csv.DictReader(f)))
    b02 = lap_b02(c, a.giam_tru, a.lai_vay)
    b01c, b01d = lap_b01(c, "cuoi", b02["60"]), lap_b01(c, "dau")
    loi, cb = kiem_tra(c, b01c, b01d)
    print(f"{a.ten_dn} – BCTC năm {a.nam} (BẢN NHÁP, TT 133/2016)\n\nB02-DNN")
    for ma, ten in B02:
        print(f"  {ma}  {ten[:62]:62} {d(b02[ma]):>18}")
    print("\nB01a-DNN                                                          Cuối năm          Đầu năm")
    for ma, ten in B01:
        if ma:
            print(f"  {ma}  {ten[:52]:52} {d(b01c[ma]):>18} {d(b01d[ma]):>16}")
        else:
            print(f"  {ten}")
    if a.lai_vay is None and b02["22"]:
        cb.append("Chưa nhập --lai-vay: chỉ tiêu 23 đang để 0")
    if not a.giam_tru:
        cb.append("Chỉ tiêu 02 = 0: nếu có chiết khấu, giảm giá, hàng bán bị trả lại (Nợ 511) thì nhập --giam-tru")
    for x in loi:
        print("✗ " + x)
    for x in cb:
        print("! " + x)
    if a.xlsx:
        xuat_xlsx(a.xlsx, c, b01c, b01d, b02, a.ten_dn, a.nam)
        print(f"Đã ghi {a.xlsx}")
    print("Đã kiểm tra phép tính. Bản nháp – kế toán trưởng/người phụ trách kế toán soát xét, lập thuyết minh B09-DNN trước khi ký nộp.")
    return 1 if loi else 0


MAU = """so_hieu,ten,du_no_dau,du_co_dau,ps_no,ps_co,du_no_cuoi,du_co_cuoi
111,Tiền mặt,20000000,,50000000,40000000,30000000,
1121,Tiền gửi VND,180000000,,2102000000,2049000000,233000000,
131,Phải thu KH (tổng dư Nợ / dư Có chi tiết),100000000,5000000,2211000000,2111000000,200000000,5000000
1331,GTGT được khấu trừ,,,150000000,150000000,,
156,Hàng hóa,300000000,,1500000000,1400000000,400000000,
2111,TSCĐ hữu hình,240000000,,,,240000000,
2141,Hao mòn TSCĐ,,40000000,,48000000,,88000000
242,Chi phí trả trước,,,24000000,12000000,12000000,
331,Phải trả NB (tổng dư Nợ / dư Có chi tiết),,150000000,1605000000,1650000000,5000000,200000000
33311,GTGT đầu ra,,10000000,151000000,201000000,,60000000
3334,Thuế TNDN,,,10000000,28400000,,18400000
334,Phải trả NLĐ,,,360000000,360000000,,
4111,Vốn góp,,500000000,,,,500000000
4212,LNST chưa phân phối,,135000000,,,,135000000
5111,Doanh thu hàng hóa,,,10000000,2010000000,,
515,Doanh thu tài chính,,,,2000000,,
632,Giá vốn,,,1400000000,,,
6421,Chi phí bán hàng,,,240000000,,,
6422,Chi phí quản lý,,,220000000,,,
821,Chi phí thuế TNDN,,,28400000,,,
"""


def self_test():
    c = CDPS(list(csv.DictReader(io.StringIO(MAU))))
    b02 = lap_b02(c, giam_tru=10_000_000)
    assert b02["01"] == 2_010_000_000 and b02["10"] == 2_000_000_000 and b02["20"] == 600_000_000
    assert b02["24"] == 460_000_000 and b02["30"] == 142_000_000 and round(b02["60"]) == 113_600_000
    b01c, b01d = lap_b01(c, "cuoi", b02["60"]), lap_b01(c, "dau")
    loi, cb = kiem_tra(c, b01c, b01d)
    assert not loi, loi
    assert b01c["131"] == 200_000_000 and b01c["312"] == 5_000_000 and b01c["132"] == 5_000_000 and b01c["311"] == 200_000_000
    assert b01c["150"] == 152_000_000 and round(b01c["417"]) == 248_600_000 and round(b01c["200"]) == 1_032_000_000
    assert b01d["200"] == b01d["500"] == 800_000_000
    c2 = CDPS([{"so_hieu": "131", "du_no_cuoi": "999"}, {"so_hieu": "131A", "du_no_cuoi": "1"}])
    assert c2.tong("du_no_cuoi", "131") == 1  # chỉ cộng dòng lá
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        xuat_xlsx(os.path.join(t, "b.xlsx"), c, b01c, b01d, b02, "Test", 2026)
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
