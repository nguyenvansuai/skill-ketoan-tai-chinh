#!/usr/bin/env python3
"""Sinh qua-tang/Mau_so_ke_toan_DNNVV_TT133.xlsx: Nhật ký chung → Cân đối phát sinh → B02-DNN → B01a-DNN, toàn bộ bằng công thức.

Chạy từ gốc repo:  python3 scripts/tao_qua_tang_excel.py [--khong-vi-du]
"""
import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

GOC = Path(__file__).resolve().parent.parent
OUT = GOC / "qua-tang" / "Mau_so_ke_toan_DNNVV_TT133.xlsx"
N_NKC, N_SD = 2000, 300  # số dòng nhập liệu
NKC = f"'Nhật ký chung'!$D$6:$D${5 + N_NKC}", f"'Nhật ký chung'!$E$6:$E${5 + N_NKC}", f"'Nhật ký chung'!$F$6:$F${5 + N_NKC}"
SD = f"'Số dư đầu kỳ'!$A$6:$A${5 + N_SD}", f"'Số dư đầu kỳ'!$C$6:$C${5 + N_SD}", f"'Số dư đầu kỳ'!$D$6:$D${5 + N_SD}"

DAM = Font(bold=True)
TIEU_DE = Font(bold=True, size=14, color="1F3864")
NEN_DAU = PatternFill("solid", fgColor="DDEBF7")
NEN_NHAP = PatternFill("solid", fgColor="FFF2CC")
NEN_VI_DU = PatternFill("solid", fgColor="E2EFDA")
VIEN = Border(bottom=Side(style="thin", color="BFBFBF"))
SO = "#,##0;[Red](#,##0);-"


def f_od(p):
    return f'SUMPRODUCT((LEFT({SD[0]},{len(p)})="{p}")*{SD[1]})'


def f_oc(p):
    return f'SUMPRODUCT((LEFT({SD[0]},{len(p)})="{p}")*{SD[2]})'


def f_psn(p):
    return f'SUMPRODUCT((LEFT({NKC[0]},{len(p)})="{p}")*{NKC[2]})'


def f_psc(p):
    return f'SUMPRODUCT((LEFT({NKC[1]},{len(p)})="{p}")*{NKC[2]})'


def tieu_de(ws, dong1, dong2=None):
    ws["A1"] = dong1
    ws["A1"].font = TIEU_DE
    if dong2:
        ws["A2"] = dong2
        ws["A2"].font = Font(italic=True, color="595959")


def hang_dau(ws, r, cot):
    for i, c in enumerate(cot, start=1):
        x = ws.cell(r, i, c)
        x.font, x.fill = DAM, NEN_DAU
        x.alignment = Alignment(wrap_text=True, vertical="center")


def doc_tk():
    with open(GOC / "shared" / "tai-khoan-tt133.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


VI_DU_SD = [("1111", "Tiền mặt", 20_000_000, 0), ("1121", "Tiền gửi ngân hàng", 280_000_000, 0),
            ("131", "Phải thu khách hàng (tổng dư Nợ chi tiết)", 100_000_000, 0), ("156", "Hàng hóa", 300_000_000, 0),
            ("2111", "TSCĐ hữu hình", 240_000_000, 0), ("2141", "Hao mòn TSCĐ hữu hình", 0, 40_000_000),
            ("331", "Phải trả người bán", 0, 150_000_000), ("4111", "Vốn góp của chủ sở hữu", 0, 600_000_000),
            ("4211", "LNST chưa phân phối năm trước", 0, 150_000_000)]
VI_DU_NKC = [
    ("2026-10-02", "PN01", "Mua hàng nhập kho, chưa trả", "156", "331", 50_000_000),
    ("2026-10-02", "PN01", "Thuế GTGT đầu vào 8%", "1331", "331", 4_000_000),
    ("2026-10-05", "UNC01", "Trả tiền người bán", "331", "1121", 54_000_000),
    ("2026-10-10", "HD01", "Bán hàng", "131", "5111", 90_000_000),
    ("2026-10-10", "HD01", "Thuế GTGT đầu ra 8%", "131", "33311", 7_200_000),
    ("2026-10-10", "XK01", "Giá vốn hàng bán", "632", "156", 60_000_000),
    ("2026-10-15", "BC01", "Khách trả tiền", "1121", "131", 97_200_000),
    ("2026-10-31", "BL10", "Lương tháng 10 bộ phận quản lý", "6422", "334", 25_000_000),
    ("2026-10-31", "KH10", "Khấu hao TSCĐ tháng 10", "6422", "2141", 2_000_000),
    ("2026-10-31", "PC05", "Mua văn phòng phẩm", "6422", "1111", 1_500_000),
]

# Ánh xạ tài khoản → (chỉ tiêu bên tài sản khi dư Nợ, chỉ tiêu bên nguồn vốn khi dư Có) – TT133, xem references/mau-bctc-tt133.md
ANH_XA = [("111", "110", "110s"), ("112", "110", "110s"), ("121", "121", "315"), ("128", "122", "315"), ("228", "123", "315"),
          ("133", "181", "315"), ("136", "134", "315"), ("138", "134", "315"), ("141", "134", "315"), ("15", "141", "315"),
          ("211", "151", "315"), ("217", "161", "315"), ("241", "170", "315"), ("242", "182", "315"), ("333", "182", "313"),
          ("334", "134", "314"), ("335", "134", "315"), ("336", "134", "315"), ("338", "134", "315"), ("341", "134", "316"),
          ("352", "134", "318"), ("353", "134", "319"), ("356", "134", "320")]


def lap():
    tk = doc_tk()
    wb = Workbook()

    # 1. Hướng dẫn
    ws = wb.active
    ws.title = "Hướng dẫn"
    tieu_de(ws, "MẪU SỔ KẾ TOÁN DOANH NGHIỆP NHỎ VÀ VỪA – THÔNG TƯ 133/2016/TT-BTC",
            "Quà tặng từ bộ skill-ketoan-tai-chinh · Sự AI (suai.vn) · cập nhật 11/2026 · bản tham khảo")
    huong_dan = [
        "CÁCH DÙNG",
        "1. Sheet 'Số dư đầu kỳ': nhập số dư đầu năm theo tài khoản (cấp 1 hoặc chi tiết). Tổng Nợ phải bằng tổng Có.",
        "2. Sheet 'Nhật ký chung': mỗi dòng một cặp Nợ/Có. Ghi tài khoản chi tiết TT133 (6421/6422, 1331, 33311…).",
        "3. Sheet 'Cân đối phát sinh', 'B02-DNN', 'B01a-DNN' tự tính bằng công thức – không gõ đè.",
        "4. KHÔNG ghi bút toán kết chuyển 911 trong file này: B02-DNN tự lấy doanh thu, chi phí; lợi nhuận tự cộng vào chỉ tiêu 417.",
        "5. Tài khoản lưỡng tính 131, 331: nhập tổng dư Có chi tiết của 131 và tổng dư Nợ chi tiết của 331 (từ sổ công nợ) ở ô vàng sheet B01a-DNN.",
        "6. Dòng 'Kiểm tra' phải bằng 0. Khác 0: kiểm tra số dư đầu kỳ, tài khoản gõ sai, dòng thiếu số tiền.",
        "",
        "DỮ LIỆU VÍ DỤ",
        "Các ô nền xanh lá là ví dụ minh họa – xóa trước khi nhập số liệu thật.",
        "",
        "GIỚI HẠN",
        f"- Nhật ký chung tối đa {N_NKC} dòng, số dư đầu kỳ tối đa {N_SD} tài khoản. Nhiều hơn: dùng phần mềm kế toán hoặc skill dinh-khoan, bao-cao-tai-chinh.",
        "- Chỉ tiêu 412, 413 (thặng dư vốn, vốn khác) gộp trong 411; 317 (phải trả nội bộ về vốn) gộp trong 315; 133 (vốn ở đơn vị trực thuộc) gộp trong 134.",
        "- DN siêu nhỏ áp dụng TT58/2026 có mẫu sổ, BCTC riêng (B01-DNSN, B02-DNSN) – không dùng file này.",
        "- Bản nháp tham khảo: kế toán trưởng / người phụ trách kế toán soát xét trước khi ký nộp. Đối chiếu văn bản hiện hành.",
        "",
        "Bộ skill AI đi kèm: github.com/nguyenvansuai/skill-ketoan-tai-chinh",
    ]
    for i, d in enumerate(huong_dan, start=4):
        ws.cell(i, 1, d).font = DAM if d.isupper() and d else Font()
    ws.column_dimensions["A"].width = 130

    # 2. Danh mục TK
    ws = wb.create_sheet("Danh mục TK")
    tieu_de(ws, "HỆ THỐNG TÀI KHOẢN TT133/2016 (rút gọn)")
    hang_dau(ws, 3, ["Số hiệu", "Tên tài khoản", "Cấp", "Tính chất", "Loại"])
    for r in tk:
        ws.append([r["so_hieu"], r["ten"], int(r["cap"]), {"No": "Dư Nợ", "Co": "Dư Có", "LuongTinh": "Lưỡng tính",
                   "KhongSoDu": "Không số dư"}[r["tinh_chat"]], r["loai"]])
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["E"].width = 18
    n_tk = ws.max_row

    # 3. Số dư đầu kỳ
    ws = wb.create_sheet("Số dư đầu kỳ")
    tieu_de(ws, "SỐ DƯ ĐẦU KỲ", "Nhập tài khoản cấp 1 hoặc chi tiết, không nhập trùng một số dư ở cả cấp 1 và chi tiết.")
    hang_dau(ws, 5, ["Số hiệu TK", "Tên (tự hiện)", "Dư Nợ", "Dư Có"])
    ws["A4"], ws["C4"], ws["D4"] = "CỘNG", f"=SUM(C6:C{5 + N_SD})", f"=SUM(D6:D{5 + N_SD})"
    ws["E4"] = '=IF(ROUND(C4-D4,0)=0,"✓ cân","✗ Nợ ≠ Có")'
    for c in ("A4", "C4", "D4", "E4"):
        ws[c].font = DAM
    for r in range(6, 6 + N_SD):
        ws[f"B{r}"] = f"=IFERROR(VLOOKUP(A{r}&\"\",'Danh mục TK'!$A$4:$B${n_tk},2,FALSE),IF(A{r}=\"\",\"\",\"✗ không có trong TT133\"))"
        for c in "ACD":
            ws[f"{c}{r}"].fill = NEN_NHAP
        ws[f"A{r}"].number_format = "@"
        ws[f"C{r}"].number_format = ws[f"D{r}"].number_format = SO
    for i, (a, _, no, co) in enumerate(VI_DU_SD, start=6):
        ws[f"A{i}"], ws[f"C{i}"], ws[f"D{i}"] = a, no or None, co or None
        for c in "ACD":
            ws[f"{c}{i}"].fill = NEN_VI_DU
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["C"].width = ws.column_dimensions["D"].width = 18
    ws.freeze_panes = "A6"

    # 4. Nhật ký chung
    ws = wb.create_sheet("Nhật ký chung")
    tieu_de(ws, "SỔ NHẬT KÝ CHUNG (tham khảo mẫu S03a-DNN)", "Mỗi dòng 1 cặp Nợ/Có · không ghi kết chuyển 911 · tiền mặt từ 5 triệu sẽ bị cảnh báo")
    hang_dau(ws, 5, ["Ngày", "Số CT", "Diễn giải", "TK Nợ", "TK Có", "Số tiền", "Kiểm tra"])
    ws["E4"], ws["F4"] = "CỘNG", f"=SUM(F6:F{5 + N_NKC})"
    ws["E4"].font = ws["F4"].font = DAM
    for r in range(6, 6 + N_NKC):
        ws[f"G{r}"] = (f"=IF(F{r}=\"\",\"\",IF(OR(ISNA(MATCH(LEFT(D{r},3),'Danh mục TK'!$A$4:$A${n_tk},0)),"
                       f"ISNA(MATCH(LEFT(E{r},3),'Danh mục TK'!$A$4:$A${n_tk},0))),\"✗ TK không có trong TT133\","
                       f"IF(OR(LEFT(D{r},3)=\"911\",LEFT(E{r},3)=\"911\"),\"✗ không ghi kết chuyển 911\","
                       f"IF(AND(LEFT(E{r},3)=\"111\",F{r}>=5000000,LEFT(D{r},3)<>\"112\"),\"! tiền mặt từ 5 triệu\",\"\"))))")
        for c in "ABCDEF":
            ws[f"{c}{r}"].fill = NEN_NHAP
        ws[f"D{r}"].number_format = ws[f"E{r}"].number_format = "@"
        ws[f"F{r}"].number_format = SO
    for i, (ng, ct, dg, no, co, tien) in enumerate(VI_DU_NKC, start=6):
        for c, v in zip("ABCDEF", (ng, ct, dg, no, co, tien)):
            ws[f"{c}{i}"] = v
            ws[f"{c}{i}"].fill = NEN_VI_DU
    for c, w in zip("ABCDEFG", (12, 10, 45, 9, 9, 16, 28)):
        ws.column_dimensions[c].width = w
    ws.freeze_panes = "A6"

    # 5. Cân đối phát sinh (tài khoản cấp 1)
    ws = wb.create_sheet("Cân đối phát sinh")
    tieu_de(ws, "BẢNG CÂN ĐỐI SỐ PHÁT SINH (tài khoản cấp 1, trước kết chuyển)", "Tự tính – không gõ đè")
    hang_dau(ws, 4, ["Số hiệu", "Tên tài khoản", "Dư Nợ đầu", "Dư Có đầu", "PS Nợ", "PS Có", "Dư Nợ cuối", "Dư Có cuối"])
    cap1 = [r for r in tk if r["cap"] == "1"]
    for i, r in enumerate(cap1, start=5):
        p = r["so_hieu"]
        ws[f"A{i}"], ws[f"B{i}"] = p, r["ten"]
        ws[f"C{i}"], ws[f"D{i}"] = f"=MAX({f_od(p)}-{f_oc(p)},0)", f"=MAX({f_oc(p)}-{f_od(p)},0)"
        ws[f"E{i}"], ws[f"F{i}"] = f"={f_psn(p)}", f"={f_psc(p)}"
        ws[f"G{i}"], ws[f"H{i}"] = f"=MAX(C{i}-D{i}+E{i}-F{i},0)", f"=MAX(D{i}-C{i}+F{i}-E{i},0)"
    n = 4 + len(cap1)
    ws[f"B{n + 1}"] = "CỘNG"
    for c in "CDEFGH":
        ws[f"{c}{n + 1}"] = f"=SUM({c}5:{c}{n})"
    ws[f"B{n + 2}"] = "Kiểm tra Nợ − Có (phải bằng 0)"
    ws[f"C{n + 2}"], ws[f"E{n + 2}"], ws[f"G{n + 2}"] = f"=C{n + 1}-D{n + 1}", f"=E{n + 1}-F{n + 1}", f"=G{n + 1}-H{n + 1}"
    for row in ws.iter_rows(min_row=n + 1, max_row=n + 2):
        for x in row:
            x.font = DAM
    for row in ws.iter_rows(min_row=5, max_row=n + 2, min_col=3, max_col=8):
        for x in row:
            x.number_format = SO
    ws.column_dimensions["B"].width = 42
    for c in "CDEFGH":
        ws.column_dimensions[c].width = 16
    ws.freeze_panes = "C5"
    dong_cdps = {r["so_hieu"]: i for i, r in enumerate(cap1, start=5)}

    # 6. Tính (ẩn) – số dư ròng theo tiền tố tài khoản
    wt = wb.create_sheet("Tính")
    wt.append(["Tiền tố", "Dư ròng cuối kỳ (Nợ − Có)"])
    can = sorted({p for p, _, _ in ANH_XA} | {"131", "331", "214", "2147", "2291", "2292", "2293", "2294", "411", "4112",
                                             "413", "418", "419", "421", "5", "6", "7", "8", "9"})
    dong_t = {}
    for i, p in enumerate(can, start=2):
        wt[f"A{i}"] = p
        wt[f"B{i}"] = f"={f_od(p)}-{f_oc(p)}+{f_psn(p)}-{f_psc(p)}"
        dong_t[p] = i
    R = lambda p: f"'Tính'!$B${dong_t[p]}"  # noqa: E731
    wt.sheet_state = "hidden"

    # 7. B02-DNN
    ws = wb.create_sheet("B02-DNN")
    tieu_de(ws, "BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH – Mẫu B02-DNN (TT133) – BẢN NHÁP")
    hang_dau(ws, 3, ["Chỉ tiêu", "Mã số", "Kỳ này"])
    c = lambda p, ben: f"'Cân đối phát sinh'!{ben}{dong_cdps[p]}"  # noqa: E731
    b02 = [
        ("Doanh thu bán hàng và cung cấp dịch vụ", "01", f"={c('511', 'F')}"),
        ("Các khoản giảm trừ doanh thu", "02", f"={c('511', 'E')}"),
        ("Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 − 02)", "10", "=C4-C5"),
        ("Giá vốn hàng bán", "11", f"={c('632', 'E')}-{c('632', 'F')}"),
        ("Lợi nhuận gộp (20 = 10 − 11)", "20", "=C6-C7"),
        ("Doanh thu hoạt động tài chính", "21", f"={c('515', 'F')}-{c('515', 'E')}"),
        ("Chi phí tài chính", "22", f"={c('635', 'E')}-{c('635', 'F')}"),
        ("   Trong đó: Chi phí lãi vay (nhập tay)", "23", None),
        ("Chi phí quản lý kinh doanh", "24", f"={c('642', 'E')}-{c('642', 'F')}"),
        ("Lợi nhuận thuần từ hoạt động kinh doanh (30 = 20 + 21 − 22 − 24)", "30", "=C8+C9-C10-C12"),
        ("Thu nhập khác", "31", f"={c('711', 'F')}-{c('711', 'E')}"),
        ("Chi phí khác", "32", f"={c('811', 'E')}-{c('811', 'F')}"),
        ("Lợi nhuận khác (40 = 31 − 32)", "40", "=C14-C15"),
        ("Tổng lợi nhuận kế toán trước thuế (50 = 30 + 40)", "50", "=C13+C16"),
        ("Chi phí thuế TNDN", "51", f"={c('821', 'E')}-{c('821', 'F')}"),
        ("Lợi nhuận sau thuế TNDN (60 = 50 − 51)", "60", "=C17-C18"),
    ]
    for i, (ten, ma, ct) in enumerate(b02, start=4):
        ws[f"A{i}"], ws[f"B{i}"] = ten, ma
        if ct:
            ws[f"C{i}"] = ct
        else:
            ws[f"C{i}"].fill = NEN_NHAP
        ws[f"C{i}"].number_format = SO
        if ma in ("10", "20", "30", "40", "50", "60"):
            ws[f"A{i}"].font = ws[f"C{i}"].font = DAM
    ws["A21"] = "Chỉ tiêu 02 lấy toàn bộ phát sinh Nợ 511 (TT133 không có TK 521) – vì vậy không ghi kết chuyển 911 trong file này."
    ws["A21"].font = Font(italic=True, color="595959")
    ws.column_dimensions["A"].width = 66
    ws.column_dimensions["C"].width = 18

    # 8. B01a-DNN
    ws = wb.create_sheet("B01a-DNN")
    tieu_de(ws, "BÁO CÁO TÌNH HÌNH TÀI CHÍNH – Mẫu B01a-DNN (TT133) – BẢN NHÁP, số cuối kỳ")
    ws["A3"], ws["C3"] = "Tổng dư Có chi tiết TK 131 (người mua trả trước) – từ sổ công nợ", None
    ws["A4"], ws["C4"] = "Tổng dư Nợ chi tiết TK 331 (trả trước người bán) – từ sổ công nợ", None
    for x in ("C3", "C4"):
        ws[x].fill, ws[x].number_format = NEN_NHAP, SO
    hang_dau(ws, 6, ["Chỉ tiêu", "Mã số", "Số cuối kỳ"])
    tai_san, nguon_von = {}, {}
    for p, ts, nv in ANH_XA:
        tai_san.setdefault(ts, []).append(f"MAX({R(p)},0)")
        if nv == "110s":  # tiền âm → giữ dấu ở chỉ tiêu 110 để lộ lỗi
            tai_san[ts][-1] = R(p)
        else:
            nguon_von.setdefault(nv, []).append(f"MAX(-{R(p)},0)")
    tai_san.setdefault("131", []).append(f"{R('131')}+N(C3)")
    tai_san.setdefault("132", []).append("N(C4)")
    nguon_von.setdefault("311", []).append(f"-{R('331')}+N(C4)")
    nguon_von.setdefault("312", []).append("N(C3)")
    tai_san.setdefault("124", []).append(f"{R('2291')}+{R('2292')}")
    tai_san.setdefault("136", []).append(R("2293"))
    tai_san.setdefault("142", []).append(R("2294"))
    tai_san.setdefault("152", []).append(f"{R('214')}-{R('2147')}")
    tai_san.setdefault("162", []).append(R("2147"))
    nguon_von.setdefault("411", []).append(f"-({R('411')}-{R('4112')})")
    nguon_von.setdefault("412", []).append(f"-{R('4112')}")
    nguon_von.setdefault("414", []).append(f"-{R('419')}")
    nguon_von.setdefault("415", []).append(f"-{R('413')}")
    nguon_von.setdefault("416", []).append(f"-{R('418')}")
    nguon_von.setdefault("417", []).append(f"-{R('421')}-({R('5')}+{R('6')}+{R('7')}+{R('8')}+{R('9')})")
    dong = [
        ("TÀI SẢN", None), ("I. Tiền và các khoản tương đương tiền", "110"), ("II. Đầu tư tài chính", "120"),
        ("1. Chứng khoán kinh doanh", "121"), ("2. Đầu tư nắm giữ đến ngày đáo hạn", "122"), ("3. Đầu tư góp vốn vào đơn vị khác", "123"),
        ("4. Dự phòng tổn thất đầu tư tài chính (*)", "124"), ("III. Các khoản phải thu", "130"), ("1. Phải thu của khách hàng", "131"),
        ("2. Trả trước cho người bán", "132"), ("3. Vốn kinh doanh ở đơn vị trực thuộc", "133"), ("4. Phải thu khác", "134"),
        ("5. Tài sản thiếu chờ xử lý", "135"), ("6. Dự phòng phải thu khó đòi (*)", "136"), ("IV. Hàng tồn kho", "140"),
        ("1. Hàng tồn kho", "141"), ("2. Dự phòng giảm giá hàng tồn kho (*)", "142"), ("V. Tài sản cố định", "150"),
        ("- Nguyên giá", "151"), ("- Giá trị hao mòn lũy kế (*)", "152"), ("VI. Bất động sản đầu tư", "160"), ("- Nguyên giá", "161"),
        ("- Giá trị hao mòn lũy kế (*)", "162"), ("VII. Xây dựng cơ bản dở dang", "170"), ("VIII. Tài sản khác", "180"),
        ("1. Thuế GTGT được khấu trừ", "181"), ("2. Tài sản khác", "182"), ("TỔNG CỘNG TÀI SẢN", "200"),
        ("NGUỒN VỐN", None), ("I. Nợ phải trả", "300"), ("1. Phải trả người bán", "311"), ("2. Người mua trả tiền trước", "312"),
        ("3. Thuế và các khoản phải nộp Nhà nước", "313"), ("4. Phải trả người lao động", "314"), ("5. Phải trả khác", "315"),
        ("6. Vay và nợ thuê tài chính", "316"), ("7. Phải trả nội bộ về vốn kinh doanh", "317"), ("8. Dự phòng phải trả", "318"),
        ("9. Quỹ khen thưởng, phúc lợi", "319"), ("10. Quỹ phát triển khoa học và công nghệ", "320"), ("II. Vốn chủ sở hữu", "400"),
        ("1. Vốn góp của chủ sở hữu", "411"), ("2. Thặng dư vốn cổ phần", "412"), ("3. Vốn khác của chủ sở hữu", "413"),
        ("4. Cổ phiếu quỹ (*)", "414"), ("5. Chênh lệch tỷ giá hối đoái", "415"), ("6. Các quỹ thuộc vốn chủ sở hữu", "416"),
        ("7. Lợi nhuận sau thuế chưa phân phối", "417"), ("TỔNG CỘNG NGUỒN VỐN", "500"),
    ]
    tong = {"120": ["121", "122", "123", "124"], "130": ["131", "132", "133", "134", "135", "136"], "140": ["141", "142"],
            "150": ["151", "152"], "160": ["161", "162"], "180": ["181", "182"],
            "200": ["110", "120", "130", "140", "150", "160", "170", "180"],
            "300": [f"3{i:02d}" for i in range(11, 21)], "400": [f"4{i:02d}" for i in range(11, 18)], "500": ["300", "400"]}
    vt = {}
    for i, (ten, ma) in enumerate(dong, start=7):
        ws[f"A{i}"] = ten
        if ma:
            ws[f"B{i}"] = ma
            vt[ma] = i
        else:
            ws[f"A{i}"].font = DAM
    for ma, r in vt.items():
        if ma in tong:
            continue
        bieu = tai_san.get(ma, []) + nguon_von.get(ma, [])
        ws[f"C{r}"] = "=" + "+".join(bieu) if bieu else 0
    for ma, con in tong.items():
        ws[f"C{vt[ma]}"] = "=" + "+".join(f"C{vt[x]}" for x in con)
        ws[f"A{vt[ma]}"].font = ws[f"C{vt[ma]}"].font = DAM
    for r in vt.values():
        ws[f"C{r}"].number_format = SO
        ws[f"A{r}"].border = VIEN
    k = max(vt.values()) + 2
    ws[f"A{k}"], ws[f"C{k}"] = "Kiểm tra 200 − 500 (phải bằng 0)", f"=C{vt['200']}-C{vt['500']}"
    ws[f"A{k + 1}"], ws[f"C{k + 1}"] = "Đối chiếu: LNST kỳ này trong 417 = B02-DNN chỉ tiêu 60", \
        f"=-({R('5')}+{R('6')}+{R('7')}+{R('8')}+{R('9')})-'B02-DNN'!C19"
    for x in (f"A{k}", f"C{k}", f"A{k + 1}", f"C{k + 1}"):
        ws[x].font = DAM
    ws[f"C{k}"].number_format = ws[f"C{k + 1}"].number_format = SO
    ws[f"A{k + 3}"] = ("Ánh xạ theo cách lập phổ biến của TT133 – kế toán soát lại khi có nghiệp vụ đặc thù (ngoại tệ, đầu tư, vay dài hạn, "
                       "quỹ). Chi tiết: skills/bao-cao-tai-chinh/references/mau-bctc-tt133.md")
    ws[f"A{k + 3}"].font = Font(italic=True, color="595959")
    ws.column_dimensions["A"].width = 70
    ws.column_dimensions["C"].width = 18

    wb.move_sheet("B01a-DNN", offset=-1)
    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    return OUT


if __name__ == "__main__":
    if "--khong-vi-du" in sys.argv:
        VI_DU_SD.clear()
        VI_DU_NKC.clear()
    print(f"Đã ghi {lap()}")
