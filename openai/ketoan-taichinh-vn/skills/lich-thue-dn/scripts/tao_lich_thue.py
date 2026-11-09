#!/usr/bin/env python3
"""Lập lịch hạn khai, nộp thuế và BCTC cả năm cho doanh nghiệp nhỏ và vừa; tự lùi hạn trùng thứ Bảy, Chủ nhật, ngày lễ;
xuất file .ics (Google Calendar, iPhone, Outlook) có nhắc trước; báo hạn đã quá và sắp tới.

Căn cứ: NĐ 252/2026/NĐ-CP Đ.10 (tháng: ngày 20 tháng sau; quý: ngày cuối tháng đầu quý sau; quyết toán năm: ngày cuối tháng
thứ 3 sau năm), Đ.24 (tạm nộp TNDN quý – TC), Đ.3 k.7 (trùng ngày nghỉ lùi sang ngày làm việc tiếp theo); NĐ 245/2026
(gia hạn nộp tiền 2026 cho DN nhỏ, siêu nhỏ – TC); NQ 198/2025 (bỏ lệ phí môn bài từ 2026).
Ngày nghỉ tự tính: thứ Bảy, Chủ nhật, 01/01, 30/04, 01/05, 02/09. Tết Âm lịch, Giỗ Tổ, nghỉ bù: thêm bằng --ngay-nghi.

  python3 tao_lich_thue.py --nam 2027 --ky-khai quy --ics lich_thue_2027.ics
  python3 tao_lich_thue.py --nam 2026 --ky-khai quy --nd245 --hom-nay 2026-11-02 --ngay-nghi 2027-02-05,2027-02-08
"""
import argparse
import calendar
import csv
import datetime as dt
import sys
import uuid

LE_CO_DINH = [(1, 1), (4, 30), (5, 1), (9, 2)]


def cuoi_thang(nam, thang):
    return dt.date(nam, thang, calendar.monthrange(nam, thang)[1])


def ngay_nghi_mac_dinh(nam_tu, nam_den):
    return {dt.date(n, m, d) for n in range(nam_tu, nam_den + 1) for m, d in LE_CO_DINH}


def lui(d, nghi):
    while d.weekday() >= 5 or d in nghi:
        d += dt.timedelta(days=1)
    return d


def lap_lich(nam, ky_khai, nghi, nd245=False, co_tncn=True):
    """Trả danh sách (hạn gốc, hạn thực tế, việc, căn cứ) cho các nghĩa vụ phát sinh trong năm tài chính `nam` (dương lịch)."""
    ds = []
    tncn = ", TNCN khấu trừ" if co_tncn else ""
    if ky_khai == "thang":
        for t in range(1, 13):
            n, m = (nam, t + 1) if t < 12 else (nam + 1, 1)
            ds.append((dt.date(n, m, 20), f"Khai, nộp GTGT{tncn} tháng {t:02d}/{nam}", "NĐ 252/2026 Đ.10"))
    for q in range(1, 5):
        thang_dau_quy_sau = 3 * q + 1
        n, m = (nam, thang_dau_quy_sau) if q < 4 else (nam + 1, 1)
        han = cuoi_thang(n, m)
        if ky_khai == "quy":
            ds.append((han, f"Khai, nộp GTGT{tncn} quý {q}/{nam}", "NĐ 252/2026 Đ.10"))
        ds.append((han, f"Tạm nộp TNDN quý {q}/{nam} (không nộp tờ khai)" + (" – lũy kế 4 quý ≥ 80% số quyết toán" if q == 4 else ""),
                   "NĐ 252/2026 Đ.24 (TC)"))
    qt = cuoi_thang(nam + 1, 3)
    ds.append((qt, f"Quyết toán TNDN năm {nam} + nộp BCTC năm {nam}", "NĐ 252/2026 Đ.10 k.5 điểm a; Luật Kế toán (90 ngày)"))
    if co_tncn:
        ds.append((qt, f"Quyết toán TNCN năm {nam} thay người lao động ủy quyền", "NĐ 252/2026 Đ.10 k.5 điểm a"))
        ds.append((dt.date(nam, 12, 31), f"NLĐ đăng ký người phụ thuộc để được giảm trừ kỳ {nam}", "NĐ 253/2026 Đ.48 (TC)"))
    if nd245 and nam == 2026:
        ds += [
            (dt.date(2026, 11, 2), "HẠN CUỐI gửi văn bản đề nghị gia hạn NĐ 245/2026 (Phụ lục II) – nộp sau không được gia hạn", "NĐ 245/2026 (TC)"),
            (dt.date(2026, 11, 2), "Nộp tiền GTGT quý II/2026 và tạm nộp TNDN quý II/2026 đã gia hạn", "NĐ 245/2026 (TC)"),
            (dt.date(2026, 11, 20), "Nộp tiền GTGT tháng 5/2026 đã gia hạn", "NĐ 245/2026 (TC)"),
            (dt.date(2026, 12, 21), "Nộp tiền GTGT tháng 6, 7, 8, 9/2026 đã gia hạn", "NĐ 245/2026 (TC)"),
            (dt.date(2026, 12, 30), "Nộp tiền GTGT quý III/2026 và tạm nộp TNDN quý III/2026 đã gia hạn", "NĐ 245/2026 (TC)"),
        ]
    return sorted(((g, lui(g, nghi), v, c) for g, v, c in ds), key=lambda x: (x[1], x[2]))


def ics(ds, nhac_truoc):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//skill-ketoan-tai-chinh//lich-thue-dn//VI", "CALSCALE:GREGORIAN",
           "X-WR-CALNAME:Lịch thuế doanh nghiệp", "X-WR-TIMEZONE:Asia/Ho_Chi_Minh"]
    for goc, han, viec, cc in ds:
        mo_ta = f"Căn cứ: {cc}. Hạn gốc {goc:%d/%m/%Y}" + (f", lùi sang {han:%d/%m/%Y} do trùng ngày nghỉ" if han != goc else "") + \
                ". Nên nộp trước hạn gốc. Kiểm tra văn bản hiện hành."
        out += ["BEGIN:VEVENT", f"UID:{uuid.uuid5(uuid.NAMESPACE_URL, viec + str(han))}@ketoan", f"DTSTAMP:{now}",
                f"DTSTART;VALUE=DATE:{han:%Y%m%d}", f"DTEND;VALUE=DATE:{han + dt.timedelta(days=1):%Y%m%d}",
                f"SUMMARY:{viec}", f"DESCRIPTION:{mo_ta}"]
        for n in nhac_truoc:
            out += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{viec}", f"TRIGGER:-P{n}D", "END:VALARM"]
        out.append("END:VEVENT")
    out.append("END:VCALENDAR")
    return "\r\n".join(out) + "\r\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nam", type=int, help="năm tài chính (dương lịch)")
    ap.add_argument("--ky-khai", choices=["thang", "quy"], default="quy", help="kỳ khai GTGT, TNCN")
    ap.add_argument("--khong-tncn", action="store_true", help="DN không có khoản khấu trừ TNCN")
    ap.add_argument("--nd245", action="store_true", help="thêm các hạn gia hạn NĐ 245/2026 (DN nhỏ, siêu nhỏ, 43 ngành)")
    ap.add_argument("--ngay-nghi", default="", help="ngày nghỉ thêm (Tết, Giỗ Tổ, nghỉ bù), YYYY-MM-DD cách nhau dấu phẩy")
    ap.add_argument("--hom-nay", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--nhac-truoc", default="7,2", help="số ngày nhắc trước, vd 7,2")
    ap.add_argument("--ics")
    ap.add_argument("--csv")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.nam:
        ap.error("cần --nam")
    nghi = ngay_nghi_mac_dinh(a.nam, a.nam + 1) | {dt.date.fromisoformat(x.strip()) for x in a.ngay_nghi.split(",") if x.strip()}
    ds = lap_lich(a.nam, a.ky_khai, nghi, a.nd245, not a.khong_tncn)
    print(f"LỊCH THUẾ NĂM TÀI CHÍNH {a.nam} – khai {('tháng' if a.ky_khai == 'thang' else 'quý')} – hôm nay {a.hom_nay:%d/%m/%Y}\n")
    for goc, han, viec, cc in ds:
        con = (han - a.hom_nay).days
        tt = "ĐÃ QUÁ" if con < 0 else ("HÔM NAY" if con == 0 else (f"còn {con} ngày" if con <= 60 else ""))
        lui_txt = f" (gốc {goc:%d/%m})" if han != goc else ""
        print(f"  {han:%d/%m/%Y}{lui_txt:13} {tt:12} {viec}")
    print("\nThuế nhà thầu nước ngoài: khai theo từng lần thanh toán – không có trong lịch cố định. Lệ phí môn bài: bỏ từ 01/01/2026.")
    print("Ngày nghỉ đã tính: thứ Bảy, Chủ nhật, 01/01, 30/04, 01/05, 02/09 + ngày nhập thêm. Tết, Giỗ Tổ, nghỉ bù cần nhập --ngay-nghi.")
    print("Hạn nộp tiền = hạn nộp hồ sơ khai. Nên nộp trước hạn gốc. Đối chiếu văn bản hiện hành trước khi dựa vào lịch.")
    nhac = [int(x) for x in a.nhac_truoc.split(",") if x.strip()]
    if a.ics:
        with open(a.ics, "w", encoding="utf-8", newline="") as f:
            f.write(ics(ds, nhac))
        print(f"Đã ghi {a.ics} – nhập vào Google Calendar: Cài đặt → Nhập và xuất → Nhập.")
    if a.csv:
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["han_thuc_te", "han_goc", "viec", "can_cu"])
            for goc, han, viec, cc in ds:
                w.writerow([han.isoformat(), goc.isoformat(), viec, cc])
        print(f"Đã ghi {a.csv}")
    return 0


def self_test():
    nghi = ngay_nghi_mac_dinh(2026, 2027)
    assert lui(dt.date(2026, 10, 31), nghi) == dt.date(2026, 11, 2)      # thứ Bảy → thứ Hai
    assert lui(dt.date(2027, 1, 31), nghi) == dt.date(2027, 2, 1)        # Chủ nhật → thứ Hai
    assert lui(dt.date(2027, 3, 31), nghi) == dt.date(2027, 3, 31)       # thứ Tư
    assert lui(dt.date(2027, 4, 30), nghi) == dt.date(2027, 5, 3)        # thứ Sáu lễ, thứ Bảy lễ, Chủ nhật → thứ Hai
    ds = lap_lich(2026, "quy", nghi, nd245=True)
    viec = {v: h for g, h, v, c in ds}
    assert viec["Khai, nộp GTGT, TNCN khấu trừ quý 3/2026"] == dt.date(2026, 11, 2)
    assert viec["Tạm nộp TNDN quý 4/2026 (không nộp tờ khai) – lũy kế 4 quý ≥ 80% số quyết toán"] == dt.date(2027, 2, 1)
    assert viec["Quyết toán TNDN năm 2026 + nộp BCTC năm 2026"] == dt.date(2027, 3, 31)
    assert any("NĐ 245" in v for v in viec)
    dt_thang = lap_lich(2027, "thang", ngay_nghi_mac_dinh(2027, 2028))
    thang = [h for g, h, v, c in dt_thang if v.startswith("Khai, nộp GTGT, TNCN khấu trừ tháng")]
    assert len(thang) == 12 and thang[0] == dt.date(2027, 2, 22)        # 20/02/2027 là thứ Bảy
    noi_dung = ics(ds, [7, 2])
    assert noi_dung.count("BEGIN:VEVENT") == len(ds) and "TRIGGER:-P7D" in noi_dung
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
