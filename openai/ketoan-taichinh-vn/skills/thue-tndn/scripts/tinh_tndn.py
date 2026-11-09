#!/usr/bin/env python3
"""Tính thuế TNDN kỳ 2026 cho doanh nghiệp nhỏ và vừa: quyết toán năm (từ lợi nhuận kế toán + điều chỉnh) và tạm nộp quý.

Căn cứ (xem references/van-ban-hieu-luc.md): Luật 67/2025/QH15 Đ.7 (thu nhập tính thuế), Đ.10 (15%/17%/20% theo doanh thu
kỳ trước liền kề), Đ.9 k.2 điểm h (lương chủ DNTN/TNHH MTV cá nhân không được trừ); NĐ 320/2025 Đ.11; Luật 09/2026 +
NĐ 141/2026 (miễn ≤1 tỷ – có điều kiện); NQ 43/2026 (giảm 30% số TNDN phải nộp kỳ 2026–2027 nếu doanh thu năm ≤10 tỷ);
NĐ 252/2026 Đ.24 (tạm nộp quý, tổng 4 quý ≥80% số quyết toán – TC); Luật 108/2025 Đ.16 (chậm nộp 0,03%/ngày).

Script KHÔNG tự kết luận được miễn/giảm: chỉ gắn cờ, và chỉ mô phỏng giảm 30% khi người dùng xác nhận --ap-dung-nq43.

Quyết toán năm:
  python3 tinh_tndn.py quyet-toan --loi-nhuan 850000000 --dieu-chinh dieu_chinh.csv \\
      --doanh-thu-can-cu 6.5e9 --doanh-thu-nam-nay 8.2e9 --da-tam-nop 90000000 --ngoai-le khong
  dieu_chinh.csv: noi_dung,so_tien,loai   (loai: tang | giam | mien | lo)
    "Chi tiền mặt từ 5 triệu",12000000,tang
    "Lương chủ TNHH MTV cá nhân",180000000,tang
    "Lỗ năm 2024 chuyển sang",50000000,lo
Tạm nộp quý:
  python3 tinh_tndn.py tam-nop --quy 3 --thu-nhap-luy-ke 600000000 --doanh-thu-can-cu 6.5e9 --da-tam-nop-luy-ke 60000000
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys

CHAM_NOP_NGAY = 0.0003  # 0,03%/ngày – Luật 108/2025 Đ.16
TY_LE_TAM_NOP_TOI_THIEU = 0.8  # NĐ 252/2026 Đ.24 – TC


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


def thue_suat(dt_can_cu, ngoai_le, ts_nhap=None):
    """Trả (thuế suất, ghi chú, cờ). Không tự chọn khi có ngoại lệ hoặc thiếu doanh thu căn cứ."""
    co = []
    if ts_nhap is not None:
        if not 0 < ts_nhap < 1:
            raise ValueError("--thue-suat phải là số thập phân trong (0; 1), vd 0.17")
        return ts_nhap, "thuế suất do người dùng nhập", co
    if ngoai_le != "khong":
        raise ValueError("Có/chưa rõ ngoại lệ (công ty con, liên kết, ưu đãi, ngành đặc thù) → không tự chọn thuế suất; "
                         "khai --ngoai-le khong nếu chắc chắn không có, hoặc nhập --thue-suat sau khi người hành nghề xác định")
    if dt_can_cu is None:
        raise ValueError("Thiếu --doanh-thu-can-cu (tổng doanh thu kỳ tính thuế trước liền kề, đã quy đổi 12 tháng nếu cần); "
                         "DN mới có quy tắc dự kiến riêng (NĐ 320/2025 Đ.11 k.4) → nhập --thue-suat")
    if dt_can_cu <= 1e9:
        co.append(f"Doanh thu căn cứ {d(dt_can_cu)} ≤ 1 tỷ → RÀ điều kiện MIỄN TNDN (Luật 09/2026, NĐ 141/2026). "
                  "Số dưới đây là thuế TRƯỚC miễn – không phải nghĩa vụ đã xác nhận.")
    if dt_can_cu <= 3e9:
        return 0.15, "15% – doanh thu căn cứ ≤ 3 tỷ (Luật 67/2025 Đ.10 k.3)", co
    if dt_can_cu <= 50e9:
        return 0.17, "17% – doanh thu căn cứ > 3 tỷ đến ≤ 50 tỷ (Luật 67/2025 Đ.10 k.2)", co
    return 0.20, "20% – mức chung (Luật 67/2025 Đ.10 k.1)", co


def doc_dieu_chinh(path):
    tang, giam, mien, lo = [], [], [], []
    if not path:
        return tang, giam, mien, lo
    with open(path, encoding="utf-8-sig") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            loai = (r.get("loai") or "").strip().lower()
            muc = ((r.get("noi_dung") or f"dòng {i}").strip(), so(r.get("so_tien")))
            if muc[1] < 0:
                raise ValueError(f"{path} dòng {i}: số tiền điều chỉnh phải ≥ 0, dùng cột loai để chọn tăng/giảm")
            nhom = {"tang": tang, "giam": giam, "mien": mien, "lo": lo}.get(loai)
            if nhom is None:
                raise ValueError(f"{path} dòng {i}: loai phải là tang/giam/mien/lo")
            nhom.append(muc)
    return tang, giam, mien, lo


def quyet_toan(loi_nhuan, tang, giam, mien, lo, dt_can_cu, dt_nam_nay, da_tam_nop, ngoai_le, ts_nhap=None,
               ap_dung_nq43=False, nam=2026):
    ts, ghi_chu_ts, co = thue_suat(dt_can_cu, ngoai_le, ts_nhap)
    t_tang, t_giam = sum(x[1] for x in tang), sum(x[1] for x in giam)
    t_mien, t_lo = sum(x[1] for x in mien), sum(x[1] for x in lo)
    thu_nhap_chiu_thue = loi_nhuan + t_tang - t_giam
    truoc_lo = thu_nhap_chiu_thue - t_mien
    lo_dung = min(t_lo, max(truoc_lo, 0.0))
    tntt = max(truoc_lo - lo_dung, 0.0)
    thue = round(tntt * ts)
    kq = {"nam": nam, "loi_nhuan_ke_toan": loi_nhuan, "dieu_chinh_tang": t_tang, "dieu_chinh_giam": t_giam,
          "thu_nhap_chiu_thue": thu_nhap_chiu_thue, "thu_nhap_mien": t_mien, "lo_ket_chuyen_dung": lo_dung,
          "lo_con_chuyen_tiep": t_lo - lo_dung, "thu_nhap_tinh_thue": tntt, "thue_suat": ts, "ghi_chu_thue_suat": ghi_chu_ts,
          "thue_truoc_giam": thue, "giam_nq43": 0, "thue_phai_nop": thue, "co": co}
    if truoc_lo < 0:
        co.append(f"Năm nay lỗ tính thuế {d(-truoc_lo)} → được chuyển lỗ sang các năm sau theo Luật 67/2025 [cần kiểm tra thời hạn chuyển lỗ].")
    if dt_nam_nay is not None and dt_nam_nay <= 10e9 and nam in (2026, 2027):
        if ap_dung_nq43:
            kq["giam_nq43"] = round(thue * 0.3)
            kq["thue_phai_nop"] = thue - kq["giam_nq43"]
            co.append("Đã MÔ PHỎNG giảm 30% số TNDN phải nộp (NQ 43/2026) theo xác nhận của người dùng – nghị định hướng dẫn chưa xác minh; "
                      "không phải thuế suất mới.")
        else:
            co.append(f"Doanh thu năm {nam} {d(dt_nam_nay)} ≤ 10 tỷ → RÀ giảm 30% số TNDN phải nộp (NQ 43/2026). "
                      "Chưa áp vào số dưới đây; thêm --ap-dung-nq43 nếu đã xác nhận đủ điều kiện.")
    phai_nop = kq["thue_phai_nop"]
    kq["da_tam_nop"] = da_tam_nop
    kq["nop_them"] = max(phai_nop - da_tam_nop, 0)
    kq["nop_thua"] = max(da_tam_nop - phai_nop, 0)
    kq["toi_thieu_80"] = round(phai_nop * TY_LE_TAM_NOP_TOI_THIEU)
    kq["thieu_80"] = max(kq["toi_thieu_80"] - da_tam_nop, 0)
    if kq["thieu_80"]:
        co.append(f"Tạm nộp 4 quý {d(da_tam_nop)} < 80% số quyết toán ({d(kq['toi_thieu_80'])}) → phần thiếu {d(kq['thieu_80'])} "
                  "bị tính tiền chậm nộp từ sau hạn tạm nộp quý IV (NĐ 252/2026 Đ.24 – TC).")
    return kq


def tien_cham_nop(so_tien, han_nop, ngay_nop):
    """Tính từ ngày tiếp theo ngày hết hạn đến ngày liền kề trước ngày nộp [cần kiểm tra cách đếm theo Luật 108/2025]."""
    ngay = max((ngay_nop - han_nop).days - 1, 0)
    return round(so_tien * CHAM_NOP_NGAY * ngay), ngay


def tam_nop(quy, thu_nhap_luy_ke, ts, da_tam_nop_luy_ke):
    if quy not in (1, 2, 3, 4):
        raise ValueError("--quy phải là 1–4")
    thue_luy_ke = round(max(thu_nhap_luy_ke, 0) * ts)
    nop_quy = max(thue_luy_ke - da_tam_nop_luy_ke, 0)
    return {"quy": quy, "thue_uoc_luy_ke": thue_luy_ke, "da_tam_nop_luy_ke": da_tam_nop_luy_ke, "nen_tam_nop_quy_nay": nop_quy}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="lenh")
    q = sub.add_parser("quyet-toan", help="quyết toán TNDN năm")
    q.add_argument("--loi-nhuan", type=so, required=True, help="tổng lợi nhuận kế toán trước thuế (B02-DNN chỉ tiêu 50)")
    q.add_argument("--dieu-chinh", help="CSV noi_dung,so_tien,loai (tang/giam/mien/lo)")
    q.add_argument("--doanh-thu-can-cu", type=so, help="tổng doanh thu kỳ tính thuế trước liền kề (xác định thuế suất)")
    q.add_argument("--doanh-thu-nam-nay", type=so, help="tổng doanh thu năm nay (rà NQ 43/2026)")
    q.add_argument("--da-tam-nop", type=so, default=0.0, help="tổng số đã tạm nộp 4 quý")
    q.add_argument("--ngoai-le", choices=["co", "khong", "chua-ro"], default="chua-ro",
                   help="có công ty con/liên kết, ưu đãi, thu nhập đặc thù không")
    q.add_argument("--thue-suat", type=float, help="nhập thuế suất (thập phân) khi người hành nghề đã xác định")
    q.add_argument("--ap-dung-nq43", action="store_true", help="mô phỏng giảm 30% (chỉ khi đã xác nhận đủ điều kiện)")
    q.add_argument("--nam", type=int, default=2026)
    q.add_argument("--ngay-nop", type=dt.date.fromisoformat, help="ngày dự kiến nộp phần thiếu 80%% để ước tiền chậm nộp")
    q.add_argument("--json", action="store_true")
    t = sub.add_parser("tam-nop", help="ước số tạm nộp quý")
    t.add_argument("--quy", type=int, required=True)
    t.add_argument("--thu-nhap-luy-ke", type=so, required=True, help="thu nhập tính thuế ước tính lũy kế từ đầu năm đến hết quý")
    t.add_argument("--doanh-thu-can-cu", type=so)
    t.add_argument("--ngoai-le", choices=["co", "khong", "chua-ro"], default="khong")
    t.add_argument("--thue-suat", type=float)
    t.add_argument("--da-tam-nop-luy-ke", type=so, default=0.0)
    t.add_argument("--nam", type=int, default=2026)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.lenh:
        ap.error("chọn lệnh quyet-toan hoặc tam-nop")
    try:
        if a.lenh == "quyet-toan":
            tang, giam, mien, lo = doc_dieu_chinh(a.dieu_chinh)
            kq = quyet_toan(a.loi_nhuan, tang, giam, mien, lo, a.doanh_thu_can_cu, a.doanh_thu_nam_nay, a.da_tam_nop,
                            a.ngoai_le, a.thue_suat, a.ap_dung_nq43, a.nam)
            if a.ngay_nop and kq["thieu_80"]:
                han_q4 = dt.date(a.nam + 1, 1, 31)
                while han_q4.weekday() >= 5:  # trùng thứ Bảy, Chủ nhật → lùi (NĐ 252/2026 Đ.3 k.7); lễ, Tết chưa tính
                    han_q4 += dt.timedelta(days=1)
                kq["cham_nop_80"], kq["so_ngay_cham"] = tien_cham_nop(kq["thieu_80"], han_q4, a.ngay_nop)
            if a.json:
                print(json.dumps(kq, ensure_ascii=False, indent=2))
                return 0
            in_quyet_toan(kq, tang, giam, mien, lo)
        else:
            ts, ghi_chu, co = thue_suat(a.doanh_thu_can_cu, a.ngoai_le, a.thue_suat)
            kq = tam_nop(a.quy, a.thu_nhap_luy_ke, ts, a.da_tam_nop_luy_ke)
            han = {1: f"30/04/{a.nam}", 2: f"31/07/{a.nam}", 3: f"31/10/{a.nam}", 4: f"31/01/{a.nam + 1}"}[a.quy]
            print(f"TẠM NỘP TNDN QUÝ {a.quy}/{a.nam} – thuế suất {ghi_chu}")
            print(f"  Thu nhập tính thuế ước lũy kế           {d(a.thu_nhap_luy_ke):>16}")
            print(f"  Thuế ước lũy kế                         {d(kq['thue_uoc_luy_ke']):>16}")
            print(f"  Đã tạm nộp các quý trước                {d(kq['da_tam_nop_luy_ke']):>16}")
            print(f"  → Nên tạm nộp quý này                   {d(kq['nen_tam_nop_quy_nay']):>16}")
            print(f"  Hạn gốc: {han} (ngày cuối tháng đầu quý sau; trùng ngày nghỉ lùi sang ngày làm việc tiếp theo). "
                  "Không phải nộp tờ khai tạm tính quý [cần kiểm tra TT 89/2026].")
            if a.quy == 4:
                print("  Quý IV: lũy kế 4 quý cần ≥ 80% số TNDN quyết toán dự kiến để tránh tiền chậm nộp phần thiếu.")
            if a.nam == 2026 and a.quy in (2, 3):
                print("  DN nhỏ/siêu nhỏ: kiểm tra gia hạn NĐ 245/2026 (quý II → 02/11/2026, quý III → 30/12/2026; phải gửi đề nghị trước 02/11/2026).")
            for x in co:
                print("  ! " + x)
            print("Đã kiểm tra phép tính. Đối chiếu văn bản hiện hành và hỏi cơ quan thuế quản lý trước khi kê khai.")
    except ValueError as e:
        print("✗ " + str(e))
        return 2
    return 0


def in_quyet_toan(kq, tang, giam, mien, lo):
    print(f"QUYẾT TOÁN THUẾ TNDN NĂM {kq['nam']} – BẢN NHÁP")
    print(f"  Lợi nhuận kế toán trước thuế                    {d(kq['loi_nhuan_ke_toan']):>16}")
    for nhan, ds in (("+ Điều chỉnh tăng (chi phí không được trừ…)", tang), ("− Điều chỉnh giảm", giam)):
        print(f"  {nhan:47} {d(sum(x[1] for x in ds)):>16}")
        for nd, v in ds:
            print(f"      · {nd[:45]:45} {d(v):>14}")
    print(f"  = Thu nhập chịu thuế                            {d(kq['thu_nhap_chiu_thue']):>16}")
    print(f"  − Thu nhập được miễn thuế                       {d(kq['thu_nhap_mien']):>16}")
    print(f"  − Lỗ các năm trước chuyển sang (dùng)           {d(kq['lo_ket_chuyen_dung']):>16}")
    print(f"  = Thu nhập tính thuế                            {d(kq['thu_nhap_tinh_thue']):>16}")
    print(f"  × Thuế suất {kq['ghi_chu_thue_suat']}")
    print(f"  = Thuế TNDN trước miễn, giảm                    {d(kq['thue_truoc_giam']):>16}")
    if kq["giam_nq43"]:
        print(f"  − Giảm 30% (NQ 43/2026, mô phỏng)               {d(kq['giam_nq43']):>16}")
    print(f"  = TNDN phải nộp của năm                         {d(kq['thue_phai_nop']):>16}")
    print(f"  − Đã tạm nộp 4 quý                              {d(kq['da_tam_nop']):>16}")
    print(f"  → Nộp thêm                                      {d(kq['nop_them']):>16}")
    print(f"  → Nộp thừa (bù trừ/hoàn)                        {d(kq['nop_thua']):>16}")
    if kq.get("cham_nop_80"):
        print(f"  Ước tiền chậm nộp phần thiếu 80% ({kq['so_ngay_cham']} ngày × 0,03%)  {d(kq['cham_nop_80']):>10}")
    if kq["lo_con_chuyen_tiep"]:
        print(f"  Lỗ còn chuyển sang năm sau: {d(kq['lo_con_chuyen_tiep'])}")
    print(f"\nBút toán: Nợ 821 / Có 3334 = {d(kq['thue_phai_nop'])} (điều chỉnh chênh lệch với số đã ghi nhận khi tạm nộp).")
    for x in kq["co"]:
        print("! " + x)
    print("Đã kiểm tra phép tính. Hạn quyết toán + BCTC: ngày cuối tháng thứ 3 sau năm tài chính (NĐ 252/2026 Đ.10 k.5 điểm a). "
          "Đối chiếu văn bản hiện hành và hỏi cơ quan thuế quản lý trước khi kê khai.")


def self_test():
    import io
    import os
    import tempfile
    assert thue_suat(2e9, "khong")[0] == 0.15 and thue_suat(3e9, "khong")[0] == 0.15
    assert thue_suat(3.0001e9, "khong")[0] == 0.17 and thue_suat(50e9, "khong")[0] == 0.17 and thue_suat(51e9, "khong")[0] == 0.20
    assert thue_suat(0.9e9, "khong")[2] and "MIỄN" in thue_suat(0.9e9, "khong")[2][0]
    for bad in (lambda: thue_suat(2e9, "chua-ro"), lambda: thue_suat(None, "khong"), lambda: thue_suat(2e9, "khong", 17)):
        try:
            bad()
            raise AssertionError("phải báo lỗi")
        except ValueError:
            pass
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "dc.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("noi_dung,so_tien,loai\nChi tiền mặt từ 5 triệu,12.000.000,tang\nLương chủ DN,180000000,tang\n"
                    "Hoàn nhập dự phòng đã tính thuế,2000000,giam\nLỗ 2024,50000000,lo\n")
        tang, giam, mien, lo = doc_dieu_chinh(p)
    kq = quyet_toan(850e6, tang, giam, mien, lo, 6.5e9, 8.2e9, 90e6, "khong")
    # 850 + 12 + 180 − 2 = 1.040 tr; − lỗ 50 = 990 tr × 17% = 168,3 tr
    assert kq["thu_nhap_tinh_thue"] == 990e6 and kq["thue_phai_nop"] == 168_300_000, kq
    assert kq["nop_them"] == 78_300_000 and kq["thieu_80"] == round(168_300_000 * 0.8) - 90_000_000
    assert any("NQ 43" in x for x in kq["co"]) and kq["giam_nq43"] == 0
    kq2 = quyet_toan(850e6, tang, giam, mien, lo, 6.5e9, 8.2e9, 90e6, "khong", ap_dung_nq43=True)
    assert kq2["giam_nq43"] == 50_490_000 and kq2["thue_phai_nop"] == 117_810_000
    kq3 = quyet_toan(-100e6, [], [], [], [("Lỗ", 30e6)], 2e9, 2e9, 0, "khong")
    assert kq3["thu_nhap_tinh_thue"] == 0 and kq3["lo_con_chuyen_tiep"] == 30e6 and kq3["thue_phai_nop"] == 0
    assert tien_cham_nop(10_000_000, dt.date(2027, 1, 31), dt.date(2027, 3, 31)) == (174_000, 58)
    tn = tam_nop(3, 600e6, 0.17, 60e6)
    assert tn["nen_tam_nop_quy_nay"] == 42_000_000
    buf = io.StringIO()
    old, sys.stdout = sys.stdout, buf
    try:
        in_quyet_toan(kq, tang, giam, mien, lo)
    finally:
        sys.stdout = old
    assert "168.300.000" in buf.getvalue()
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
