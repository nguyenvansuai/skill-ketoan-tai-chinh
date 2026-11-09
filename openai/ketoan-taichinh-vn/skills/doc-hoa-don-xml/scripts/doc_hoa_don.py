#!/usr/bin/env python3
"""Đọc file XML hóa đơn điện tử Việt Nam (mọi nhà cung cấp: Viettel, VNPT, MISA, BKAV, EasyInvoice…) → bảng kê mua vào / bán ra,
kiểm tra số học và các dấu hiệu rủi ro, gợi ý bút toán TT133.

Thẻ đọc theo thành phần dữ liệu tại QĐ 1450/QĐ-TCT (HDon/DLHDon/TTChung, NDHDon/NBan, NMua, DSHHDVu/HHDVu, TToan, MCCQT)
– so khớp theo tên thẻ, bỏ qua namespace [cần kiểm tra định dạng cập nhật sau NĐ 254/2026].
Chỉ đọc file XML – bản PDF/ảnh chỉ là bản thể hiện, không dùng làm dữ liệu gốc.

  python3 doc_hoa_don.py thu_muc_xml/ --mst-cua-toi 0312345678
  python3 doc_hoa_don.py a.xml b.xml --mst-cua-toi 0312345678 --csv bang_ke.csv --xlsx bang_ke.xlsx
"""
import argparse
import csv
import datetime as dt
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

NGUONG_CHUYEN_KHOAN = 5_000_000
HET_GIAM_8 = dt.date(2026, 12, 31)  # NĐ 174/2025 – giảm 10% → 8% đến hết 31/12/2026


def ten(el):
    return el.tag.rsplit("}", 1)[-1]


def tim(goc, *duong):
    """Tìm phần tử con theo chuỗi tên thẻ (bỏ namespace, ở bất kỳ độ sâu nào cho thẻ đầu)."""
    hien_tai = [goc]
    for i, t in enumerate(duong):
        moi = []
        for e in hien_tai:
            nguon = e.iter() if i == 0 else list(e)
            moi += [c for c in nguon if ten(c) == t and c is not e]
        hien_tai = moi
        if not hien_tai:
            return None
    return hien_tai[0]


def tat_ca(goc, t):
    return [e for e in goc.iter() if ten(e) == t]


def gt(el, t, mac_dinh=""):
    if el is None:
        return mac_dinh
    c = next((x for x in el if ten(x) == t), None)
    return (c.text or "").strip() if c is not None and c.text else mac_dinh


def so(s):
    s = (s or "").strip().replace(",", "")
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def chuan_mst(m):
    return re.sub(r"[^0-9]", "", m or "")


def hop_le_mst(m):
    d = chuan_mst(m)
    return len(d) in (10, 12, 13)  # 10 số DN, 13 số chi nhánh (10-3), 12 số định danh cá nhân


def doc_mot(path):
    goc = ET.parse(path).getroot()
    tt = tim(goc, "TTChung")
    nban, nmua = tim(goc, "NBan"), tim(goc, "NMua")
    ttoan = tim(goc, "TToan")
    dong = []
    for h in tat_ca(goc, "HHDVu"):
        dong.append({
            "tchat": gt(h, "TChat", "1"), "stt": gt(h, "STT"), "ma": gt(h, "MHHDVu"), "ten": gt(h, "THHDVu"),
            "dvt": gt(h, "DVTinh"), "sl": so(gt(h, "SLuong")), "dgia": so(gt(h, "DGia")),
            "ck": so(gt(h, "STCKhau")), "thtien": so(gt(h, "ThTien")), "tsuat": gt(h, "TSuat"),
        })
    loai_ts = []
    for l in tat_ca(goc, "LTSuat"):
        loai_ts.append({"tsuat": gt(l, "TSuat"), "thtien": so(gt(l, "ThTien")), "tthue": so(gt(l, "TThue"))})
    ngay = gt(tt, "NLap")
    try:
        ngay_d = dt.date.fromisoformat(ngay[:10])
    except ValueError:
        ngay_d = None
    mccqt = tim(goc, "MCCQT")
    return {
        "file": str(path), "ten_hd": gt(tt, "THDon"), "mau_so": gt(tt, "KHMSHDon"), "ky_hieu": gt(tt, "KHHDon"),
        "so": gt(tt, "SHDon"), "ngay": ngay[:10], "ngay_d": ngay_d, "tien_te": gt(tt, "DVTTe", "VND"),
        "ty_gia": so(gt(tt, "TGia")) or 1.0, "httt": gt(tt, "HTTToan"),
        "ban_ten": gt(nban, "Ten"), "ban_mst": chuan_mst(gt(nban, "MST")), "ban_dc": gt(nban, "DChi"),
        "mua_ten": gt(nmua, "Ten") or gt(nmua, "HVTNMHang"), "mua_mst": chuan_mst(gt(nmua, "MST")),
        "dong": dong, "loai_ts": loai_ts,
        "tien_hang": so(gt(ttoan, "TgTCThue")), "tien_thue": so(gt(ttoan, "TgTThue")),
        "ck_tm": so(gt(ttoan, "TTCKTMai")), "tong": so(gt(ttoan, "TgTTTBSo")),
        "ma_cqt": (mccqt.text or "").strip() if mccqt is not None and mccqt.text else "",
        "co_chu_ky": any(ten(e) == "Signature" for e in goc.iter()),
    }


def kiem_tra(hd, mst_toi):
    cb = []
    am = sum(-d["thtien"] if d["tchat"] == "3" else d["thtien"] for d in hd["dong"] if d["tchat"] in ("1", "3"))
    if hd["dong"] and hd["tien_hang"] and abs(am - hd["tien_hang"]) > 1:
        cb.append(f"Cộng tiền hàng các dòng {am:,.0f} ≠ TgTCThue {hd['tien_hang']:,.0f}")
    if hd["tong"] and abs(hd["tien_hang"] + hd["tien_thue"] - hd["ck_tm"] - hd["tong"]) > 1:
        cb.append("Tiền hàng + thuế − chiết khấu ≠ tổng thanh toán")
    if hd["loai_ts"] and abs(sum(l["tthue"] for l in hd["loai_ts"]) - hd["tien_thue"]) > 1:
        cb.append("Tổng thuế theo từng thuế suất ≠ TgTThue")
    for d in hd["dong"]:
        m = re.match(r"(\d+)%", d["tsuat"] or "")
        if m and d["tchat"] == "1":
            if m.group(1) not in {"0", "5", "8", "10"}:
                cb.append(f"Dòng {d['stt']}: thuế suất lạ {d['tsuat']}")
            if m.group(1) == "8" and hd["ngay_d"] and hd["ngay_d"] > HET_GIAM_8:
                cb.append(f"Dòng {d['stt']}: thuế suất 8% sau 31/12/2026 – kiểm tra còn chính sách giảm GTGT không")
    if not hd["ma_cqt"]:
        cb.append("Không thấy mã của cơ quan thuế (MCCQT) – hóa đơn không mã hoặc file chưa cấp mã; tra cứu trên hoadondientu.gdt.gov.vn")
    if not hd["co_chu_ky"]:
        cb.append("Không thấy chữ ký số trong file")
    for nhan, m in (("người bán", hd["ban_mst"]), ("người mua", hd["mua_mst"])):
        if m and not hop_le_mst(m):
            cb.append(f"MST {nhan} {m} sai độ dài")
    chieu = "?"
    if mst_toi:
        if hd["ban_mst"].startswith(mst_toi):
            chieu = "ban-ra"
        elif hd["mua_mst"].startswith(mst_toi):
            chieu = "mua-vao"
        else:
            cb.append("MST của DN không khớp người bán hay người mua")
    if hd["tien_te"] not in ("VND", "") and hd["ty_gia"] == 1.0:
        cb.append(f"Hóa đơn ngoại tệ {hd['tien_te']} nhưng không có tỷ giá")
    return chieu, [x.replace(",", ".") for x in cb]


def goi_y_but_toan(hd, chieu):
    th, tt, tong = hd["tien_hang"] - hd["ck_tm"], hd["tien_thue"], hd["tong"]
    if chieu == "mua-vao":
        return [("156/152/153/6421/6422/242/211 (tùy bản chất)", "331", th), ("1331 (1332 nếu TSCĐ)", "331", tt)]
    if chieu == "ban-ra":
        return [("131", "5111/5112/5113", th), ("131", "33311", tt)]
    return []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("duong_dan", nargs="*", help="file .xml hoặc thư mục")
    ap.add_argument("--mst-cua-toi", help="MST của doanh nghiệp để phân loại mua vào / bán ra")
    ap.add_argument("--csv")
    ap.add_argument("--xlsx")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    files = []
    for p in map(Path, a.duong_dan):
        files += sorted(p.rglob("*.xml")) if p.is_dir() else [p]
    if not files:
        ap.error("không có file XML")
    mst = chuan_mst(a.mst_cua_toi) if a.mst_cua_toi else ""
    ds, loi = [], []
    for f in files:
        try:
            hd = doc_mot(f)
        except ET.ParseError as e:
            loi.append(f"{f}: không đọc được XML ({e})")
            continue
        chieu, cb = kiem_tra(hd, mst)
        ds.append((hd, chieu, cb))
    in_ket_qua(ds, loi)
    if a.csv or a.xlsx:
        xuat(ds, a.csv, a.xlsx)
    return 0


def tong_hop_chuyen_khoan(ds):
    """Hóa đơn mua vào cùng người bán, cùng ngày cộng lại từ 5 triệu → phải có chứng từ không dùng tiền mặt (NĐ 181/2025 Đ.26)."""
    nhom = defaultdict(float)
    for hd, chieu, _ in ds:
        if chieu == "mua-vao":
            nhom[(hd["ban_mst"], hd["ban_ten"], hd["ngay"])] += hd["tong"]
    return {k: v for k, v in nhom.items() if v >= NGUONG_CHUYEN_KHOAN}


def in_ket_qua(ds, loi):
    trung = defaultdict(list)
    for hd, _, _ in ds:
        trung[(hd["ban_mst"], hd["mau_so"], hd["ky_hieu"], hd["so"])].append(hd["file"])
    for chieu, nhan in (("mua-vao", "MUA VÀO"), ("ban-ra", "BÁN RA"), ("?", "CHƯA PHÂN LOẠI (thiếu --mst-cua-toi?)")):
        nhom = [x for x in ds if x[1] == chieu]
        if not nhom:
            continue
        print(f"\n=== {nhan}: {len(nhom)} hóa đơn ===")
        print(f"{'Ngày':10} {'Ký hiệu':10} {'Số':>8}  {'Đối tác':32} {'MST':14} {'Tiền hàng':>14} {'Thuế':>12} {'Tổng':>14}")
        tong = [0.0, 0.0, 0.0]
        theo_ts = defaultdict(lambda: [0.0, 0.0])
        for hd, _, cb in nhom:
            doi_tac = (hd["ban_ten"], hd["ban_mst"]) if chieu != "ban-ra" else (hd["mua_ten"], hd["mua_mst"])
            print(f"{hd['ngay']:10} {hd['ky_hieu']:10} {hd['so']:>8}  {doi_tac[0][:32]:32} {doi_tac[1]:14} "
                  f"{hd['tien_hang']:>14,.0f} {hd['tien_thue']:>12,.0f} {hd['tong']:>14,.0f}".replace(",", "."))
            for x in cb:
                print(f"{'':12}! {x}")
            tong[0] += hd["tien_hang"]
            tong[1] += hd["tien_thue"]
            tong[2] += hd["tong"]
            for l in hd["loai_ts"]:
                theo_ts[l["tsuat"]][0] += l["thtien"]
                theo_ts[l["tsuat"]][1] += l["tthue"]
        print(f"{'CỘNG':>78} {tong[0]:>14,.0f} {tong[1]:>12,.0f} {tong[2]:>14,.0f}".replace(",", "."))
        for ts, (th, tt) in sorted(theo_ts.items()):
            print(f"   Thuế suất {ts:>5}: doanh số chưa thuế {th:,.0f} – thuế {tt:,.0f}".replace(",", "."))
        if chieu in ("mua-vao", "ban-ra"):
            print("   Gợi ý bút toán (tổng hợp):")
            for n, c, t in goi_y_but_toan({"tien_hang": tong[0], "ck_tm": 0, "tien_thue": tong[1], "tong": tong[2]}, chieu):
                print(f"     Nợ {n:48} Có {c:16} {t:>14,.0f}".replace(",", "."))
    ck = tong_hop_chuyen_khoan(ds)
    if ck:
        print("\nMUA VÀO cùng người bán cùng ngày ≥ 5 triệu – cần chứng từ thanh toán không dùng tiền mặt để khấu trừ GTGT, tính chi phí:")
        for (m, t, n), v in sorted(ck.items(), key=lambda x: x[0][2]):
            print(f"   {n} {t[:40]:40} {m:14} {v:>14,.0f}".replace(",", "."))
    for k, fs in trung.items():
        if len(fs) > 1:
            print(f"\n! Trùng hóa đơn (MST bán {k[0]}, ký hiệu {k[2]}, số {k[3]}): {', '.join(fs)}")
    for x in loi:
        print("✗ " + x)
    print("\nĐã kiểm tra phép tính. Tra cứu tính hợp lệ, trạng thái hóa đơn (bị thay thế, điều chỉnh) trên hoadondientu.gdt.gov.vn trước khi kê khai.")


def xuat(ds, path_csv, path_xlsx):
    cot = ["chieu", "ngay", "mau_so", "ky_hieu", "so", "ban_ten", "ban_mst", "mua_ten", "mua_mst", "tien_hang", "tien_thue", "ck_tm", "tong", "ma_cqt", "canh_bao", "file"]
    rows = [[c, hd["ngay"], hd["mau_so"], hd["ky_hieu"], hd["so"], hd["ban_ten"], hd["ban_mst"], hd["mua_ten"], hd["mua_mst"],
             hd["tien_hang"], hd["tien_thue"], hd["ck_tm"], hd["tong"], hd["ma_cqt"], " | ".join(cb), hd["file"]] for hd, c, cb in ds]
    if path_csv:
        with open(path_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(cot)
            w.writerows(rows)
        print(f"Đã ghi {path_csv}")
    if path_xlsx:
        from openpyxl import Workbook
        from openpyxl.styles import Font
        wb = Workbook()
        wb.remove(wb.active)
        for chieu, ten_sheet in (("mua-vao", "Mua vao"), ("ban-ra", "Ban ra"), ("?", "Chua phan loai")):
            r = [x for x in rows if x[0] == chieu]
            if not r:
                continue
            ws = wb.create_sheet(ten_sheet)
            ws.append(cot[1:])
            for c in ws[1]:
                c.font = Font(bold=True)
            for x in r:
                ws.append(x[1:])
            n = ws.max_row
            ws.append(["CỘNG"] + [""] * 7 + [f"=SUM({col}2:{col}{n})" for col in "IJKL"])
            for row in ws.iter_rows(min_row=2):
                for c in row[8:12]:
                    c.number_format = "#,##0"
        wb.save(path_xlsx)
        print(f"Đã ghi {path_xlsx}")


MAU = """<?xml version="1.0" encoding="UTF-8"?>
<HDon><DLHDon Id="data"><TTChung><PBan>2.1.0</PBan><THDon>HÓA ĐƠN GIÁ TRỊ GIA TĂNG</THDon><KHMSHDon>1</KHMSHDon>
<KHHDon>C26TAA</KHHDon><SHDon>{so}</SHDon><NLap>{ngay}</NLap><DVTTe>VND</DVTTe><TGia>1</TGia><HTTToan>TM/CK</HTTToan></TTChung>
<NDHDon><NBan><Ten>Công ty TNHH Bán</Ten><MST>{mban}</MST><DChi>Q1</DChi></NBan><NMua><Ten>Công ty Mua</Ten><MST>{mmua}</MST></NMua>
<DSHHDVu><HHDVu><TChat>1</TChat><STT>1</STT><THHDVu>Giấy A4</THHDVu><DVTinh>Thùng</DVTinh><SLuong>10</SLuong><DGia>300000</DGia><ThTien>3000000</ThTien><TSuat>8%</TSuat></HHDVu>
<HHDVu><TChat>1</TChat><STT>2</STT><THHDVu>Mực in</THHDVu><SLuong>2</SLuong><DGia>1000000</DGia><ThTien>2000000</ThTien><TSuat>8%</TSuat></HHDVu></DSHHDVu>
<TToan><THTTLTSuat><LTSuat><TSuat>8%</TSuat><ThTien>5000000</ThTien><TThue>400000</TThue></LTSuat></THTTLTSuat>
<TgTCThue>5000000</TgTCThue><TgTThue>{thue}</TgTThue><TTCKTMai>0</TTCKTMai><TgTTTBSo>5400000</TgTTTBSo></TToan></NDHDon></DLHDon>
<MCCQT>00ABCDEF1234567890</MCCQT><DSCKS><NBan><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"/></NBan></DSCKS></HDon>"""


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p1 = Path(d) / "a.xml"
        p1.write_text(MAU.format(so=101, ngay="2026-10-12", mban="0300000001", mmua="0312345678", thue=400000), encoding="utf-8")
        p2 = Path(d) / "b.xml"
        p2.write_text(MAU.format(so=102, ngay="2027-01-05", mban="0312345678", mmua="0300000002", thue=500000), encoding="utf-8")
        h1 = doc_mot(p1)
        assert h1["so"] == "101" and h1["tien_hang"] == 5_000_000 and h1["ma_cqt"] and h1["co_chu_ky"]
        c1, cb1 = kiem_tra(h1, "0312345678")
        assert c1 == "mua-vao" and not cb1, cb1
        h2 = doc_mot(p2)
        c2, cb2 = kiem_tra(h2, "0312345678")
        assert c2 == "ban-ra"
        assert any("8% sau 31/12/2026" in x for x in cb2) and any("thanh toán" in x for x in cb2), cb2
        assert tong_hop_chuyen_khoan([(h1, c1, cb1)])  # 5,4 triệu ≥ 5 triệu
        xuat([(h1, c1, cb1), (h2, c2, cb2)], Path(d) / "k.csv", Path(d) / "k.xlsx")
        assert (Path(d) / "k.xlsx").exists()
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
