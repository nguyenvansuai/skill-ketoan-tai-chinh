#!/usr/bin/env python3
"""Xác định quy mô doanh nghiệp (siêu nhỏ / nhỏ / vừa) và gợi ý chế độ kế toán, các cổng thuế cần rà.

Tiêu chí quy mô: NĐ 80/2021/NĐ-CP Điều 5 [cần kiểm tra văn bản hiện hành]. Lao động = lao động tham gia BHXH bình quân năm;
thỏa tiêu chí lao động VÀ (doanh thu năm HOẶC tổng nguồn vốn).
Chế độ: TT133/2016 (DNNVV), TT58/2026 (siêu nhỏ, năm tài chính bắt đầu từ/sau 01/07/2026), TT99/2025 (DNNVV được chọn).
Cổng thuế (chỉ để gắn cờ rà soát, không kết luận nghĩa vụ): Luật 67/2025 Đ.10 (15%/17%/20% theo doanh thu năm trước);
Luật 09/2026 + NĐ 141/2026 (miễn TNDN ≤1 tỷ); NQ 43/2026 (giảm 30% TNDN 2026–2027 nếu doanh thu ≤10 tỷ);
khai GTGT quý nếu doanh thu năm trước ≤50 tỷ [cần kiểm tra NĐ 252/2026].

  python3 xac_dinh_quy_mo.py --linh-vuc thuong-mai-dich-vu --lao-dong 6 --doanh-thu 4.2e9 --nguon-von 1.5e9
  python3 xac_dinh_quy_mo.py --linh-vuc cong-nghiep-xay-dung --lao-dong 35 --doanh-thu 28e9 --doanh-thu-nam-truoc 25e9 \\
      --nam-tai-chinh-bat-dau 2027-01-01 --json
"""
import argparse
import datetime as dt
import json

# (lao động tối đa, doanh thu tối đa, nguồn vốn tối đa) – NĐ 80/2021 Đ.5
NGUONG = {
    "nong-lam-thuy-san": {"sieu-nho": (10, 3e9, 3e9), "nho": (100, 50e9, 20e9), "vua": (200, 200e9, 100e9)},
    "cong-nghiep-xay-dung": {"sieu-nho": (10, 3e9, 3e9), "nho": (100, 50e9, 20e9), "vua": (200, 200e9, 100e9)},
    "thuong-mai-dich-vu": {"sieu-nho": (10, 10e9, 3e9), "nho": (50, 100e9, 50e9), "vua": (100, 300e9, 100e9)},
}
TEN = {"sieu-nho": "siêu nhỏ", "nho": "nhỏ", "vua": "vừa", "lon": "lớn (ngoài DNNVV)"}
MOC_TT58 = dt.date(2026, 7, 1)


def ty(x):
    return f"{x / 1e9:,.2f} tỷ".replace(",", "X").replace(".", ",").replace("X", ".")


def xac_dinh(linh_vuc, lao_dong, doanh_thu=None, nguon_von=None):
    if lao_dong < 0 or (doanh_thu is not None and doanh_thu < 0) or (nguon_von is not None and nguon_von < 0):
        raise ValueError("số liệu không được âm")
    if doanh_thu is None and nguon_von is None:
        raise ValueError("cần ít nhất doanh thu hoặc nguồn vốn")
    for muc in ("sieu-nho", "nho", "vua"):
        ld, dt_max, nv_max = NGUONG[linh_vuc][muc]
        dat_tc = (doanh_thu is not None and doanh_thu <= dt_max) or (nguon_von is not None and nguon_von <= nv_max)
        if lao_dong <= ld and dat_tc:
            return muc
    return "lon"


def goi_y_che_do(muc, ngay_bat_dau):
    if muc == "lon":
        return ["TT 99/2025 (chế độ kế toán doanh nghiệp chung)"]
    ds = []
    if muc == "sieu-nho":
        if ngay_bat_dau and ngay_bat_dau >= MOC_TT58:
            ds.append("TT 58/2026 (siêu nhỏ, tự nguyện) – sổ theo nhóm phương pháp nộp thuế")
        else:
            ds.append("TT 58/2026 chỉ áp dụng năm tài chính bắt đầu từ/sau 01/07/2026"
                      + (f" – năm bắt đầu {ngay_bat_dau:%d/%m/%Y} chưa áp dụng" if ngay_bat_dau else " – nhập --nam-tai-chinh-bat-dau để kiểm"))
    ds.append("TT 133/2016 (DNNVV) – mặc định phổ biến")
    ds.append("TT 99/2025 (DNNVV được lựa chọn, nhất quán tối thiểu 1 năm)")
    return ds


def cong_thue(dt_nam_truoc, dt_hien_tai):
    co = []
    can_cu = dt_nam_truoc
    if can_cu is None:
        co.append("Chưa có doanh thu năm trước → chưa xác định thuế suất TNDN 15%/17%/20% (Luật 67/2025 Đ.10); DN mới có quy tắc riêng (NĐ 320/2025 Đ.11 k.4).")
    elif can_cu <= 1e9:
        co.append(f"Doanh thu năm trước {ty(can_cu)} ≤ 1 tỷ → RÀ điều kiện miễn TNDN (Luật 09/2026, NĐ 141/2026). Không tự kết luận được miễn.")
    elif can_cu <= 3e9:
        co.append(f"Doanh thu năm trước {ty(can_cu)} ≤ 3 tỷ → thuế suất TNDN cơ sở 15% nếu đủ điều kiện (Luật 67/2025 Đ.10).")
    elif can_cu <= 50e9:
        co.append(f"Doanh thu năm trước {ty(can_cu)} trong (3; 50] tỷ → thuế suất TNDN cơ sở 17% nếu đủ điều kiện (Luật 67/2025 Đ.10).")
    else:
        co.append(f"Doanh thu năm trước {ty(can_cu)} > 50 tỷ → thuế suất TNDN 20%.")
    if dt_hien_tai is not None and dt_hien_tai <= 10e9:
        co.append(f"Doanh thu năm nay {ty(dt_hien_tai)} ≤ 10 tỷ → RÀ giảm 30% số TNDN phải nộp kỳ 2026–2027 (NQ 43/2026); nghị định hướng dẫn chưa xác minh.")
    if can_cu is not None:
        co.append("Khai GTGT theo QUÝ (doanh thu năm trước ≤ 50 tỷ)" if can_cu <= 50e9 else "Khai GTGT theo THÁNG (doanh thu năm trước > 50 tỷ)")
        co[-1] += " [cần kiểm tra NĐ 252/2026]."
    co.append("Lệ phí môn bài: không còn thu từ 01/01/2026 (NQ 198/2025 Đ.10 k.7).")
    return co


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--linh-vuc", choices=NGUONG, required=False)
    ap.add_argument("--lao-dong", type=float, help="lao động tham gia BHXH bình quân năm")
    ap.add_argument("--doanh-thu", type=float, help="tổng doanh thu năm (đồng) dùng xét quy mô")
    ap.add_argument("--nguon-von", type=float, help="tổng nguồn vốn (đồng)")
    ap.add_argument("--doanh-thu-nam-truoc", type=float, help="doanh thu căn cứ năm trước (TNDN, kỳ khai GTGT)")
    ap.add_argument("--nam-tai-chinh-bat-dau", type=dt.date.fromisoformat, help="ngày bắt đầu năm tài chính YYYY-MM-DD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.linh_vuc or a.lao_dong is None:
        ap.error("cần --linh-vuc và --lao-dong")

    muc = xac_dinh(a.linh_vuc, a.lao_dong, a.doanh_thu, a.nguon_von)
    kq = {
        "quy_mo": TEN[muc],
        "che_do_goi_y": goi_y_che_do(muc, a.nam_tai_chinh_bat_dau),
        "co_thue": cong_thue(a.doanh_thu_nam_truoc if a.doanh_thu_nam_truoc is not None else None, a.doanh_thu),
        "luu_y": ["Ngưỡng quy mô theo NĐ 80/2021 Đ.5 – [cần kiểm tra văn bản hiện hành].",
                  "Quy mô kế toán và ngưỡng thuế là hai phép kiểm khác nhau.",
                  "Đổi chế độ kế toán chỉ từ đầu năm tài chính tiếp theo; không hạch toán đan xen TT58 và TT133."],
    }
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
        return 0
    print(f"Quy mô: DN {kq['quy_mo']} (lĩnh vực {a.linh_vuc}, {a.lao_dong:g} lao động BHXH)")
    print("\nChế độ kế toán có thể áp dụng:")
    for x in kq["che_do_goi_y"]:
        print("  - " + x)
    print("\nCờ thuế cần rà:")
    for x in kq["co_thue"]:
        print("  - " + x)
    print("\nLưu ý:")
    for x in kq["luu_y"]:
        print("  - " + x)
    return 0


def self_test():
    assert xac_dinh("thuong-mai-dich-vu", 6, 4.2e9, 1.5e9) == "sieu-nho"
    assert xac_dinh("thuong-mai-dich-vu", 6, 12e9, 2e9) == "sieu-nho"      # vốn ≤3 tỷ là đủ
    assert xac_dinh("thuong-mai-dich-vu", 6, 12e9, 5e9) == "nho"
    assert xac_dinh("cong-nghiep-xay-dung", 10, 3e9) == "sieu-nho"
    assert xac_dinh("cong-nghiep-xay-dung", 11, 3e9) == "nho"
    assert xac_dinh("cong-nghiep-xay-dung", 150, 150e9) == "vua"
    assert xac_dinh("thuong-mai-dich-vu", 120, 50e9, 50e9) == "lon"
    assert any("TT 58" in x and "chưa áp dụng" in x for x in goi_y_che_do("sieu-nho", dt.date(2026, 1, 1)))
    assert any(x.startswith("TT 58/2026 (siêu nhỏ") for x in goi_y_che_do("sieu-nho", dt.date(2027, 1, 1)))
    assert any("miễn TNDN" in x for x in cong_thue(0.8e9, 0.9e9))
    assert any("17%" in x for x in cong_thue(25e9, 28e9))
    try:
        xac_dinh("thuong-mai-dich-vu", 5)
        raise AssertionError("phải báo thiếu doanh thu/nguồn vốn")
    except ValueError:
        pass
    print("self-test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
