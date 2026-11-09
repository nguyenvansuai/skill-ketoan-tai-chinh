#!/usr/bin/env python3
"""Dựng slide bài giảng 2 trang (16:9) từ file JSON: python3 tao_slide.py spec.json out.pptx"""
import json
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

FONT = "Calibri"
MONO = "Consolas"


def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


XAM_DAM, XAM, NEN, TRANG = rgb("1F2933"), rgb("52606D"), rgb("F5F7FA"), rgb("FFFFFF")
DO, DO_NHAT = rgb("B42318"), rgb("FEF3F2")


def hop(s, x, y, w, h, fill=None, line=None, radius=False):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        sh.adjustments[0] = 0.06
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.25)
    sh.shadow.inherit = False
    return sh


def chu(s, x, y, w, h, doan, co=14, mau=XAM_DAM, dam=False, font=FONT, canh=PP_ALIGN.LEFT, giua=False):
    """doan: chuỗi hoặc list các (text, {co, mau, dam, font}) theo từng đoạn."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    if giua:
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ds = doan if isinstance(doan, list) else [(doan, {})]
    for i, muc in enumerate(ds):
        text, kieu = muc if isinstance(muc, tuple) else (muc, {})
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = canh
        p.space_after = Pt(kieu.get("cach", 3))
        r = p.add_run()
        r.text = text
        r.font.name = kieu.get("font", font)
        r.font.size = Pt(kieu.get("co", co))
        r.font.bold = kieu.get("dam", dam)
        r.font.color.rgb = kieu.get("mau", mau)
    return tb


def tieu_de(s, chinh, phu, mau, so_trang):
    hop(s, 0, 0, 13.333, 1.15, fill=mau)
    chu(s, 0.5, 0.14, 11.3, 0.55, chinh, co=28, mau=TRANG, dam=True)
    chu(s, 0.5, 0.66, 11.6, 0.45, phu, co=14.5, mau=rgb("E4ECF7"))
    chu(s, 12.0, 0.36, 0.9, 0.4, so_trang, co=12, mau=rgb("E4ECF7"), canh=PP_ALIGN.RIGHT)


def cot_so_sanh(s, x, w, nhan, mau_nhan, nen, vien, buoc, tg, ket, mau_ket):
    hop(s, x, 1.42, w, 5.35, fill=nen, line=vien, radius=True)
    chu(s, x + 0.3, 1.55, w - 0.6, 0.5, nhan, co=19, mau=mau_nhan, dam=True)
    ds = [(f"{i}.  {b}", {"co": 16, "cach": 7}) for i, b in enumerate(buoc, 1)]
    chu(s, x + 0.3, 2.08, w - 0.6, 3.1, ds)
    hop(s, x + 0.3, 5.2, w - 0.6, 1.4, fill=TRANG, radius=True)
    chu(s, x + 0.45, 5.27, w - 0.9, 0.4, tg, co=16, mau=mau_ket, dam=True)
    chu(s, x + 0.45, 5.68, w - 0.9, 0.9, [(k, {"co": 13, "mau": XAM, "cach": 2}) for k in ket])


def slide1(prs, sp, mau):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    hop(s, 0, 0, 13.333, 7.5, fill=NEN)
    tieu_de(s, sp["tieu_de"], sp["tinh_huong"], mau, "1/2")
    a, b = sp["thu_cong"], sp["plugin"]
    cot_so_sanh(s, 0.45, 6.05, "Không dùng skill", DO, TRANG, rgb("F2C4BF"), a["buoc"], a["thoi_gian"], a["rui_ro"], DO)
    cot_so_sanh(s, 6.83, 6.05, "Dùng plugin " + sp["plugin_ten"], mau, TRANG, mau, b["buoc"], b["thoi_gian"], b["loi_ich"], mau)
    chu(s, 0.45, 6.95, 12.4, 0.4, "Thời gian là ước tính minh họa. Toàn bộ tên, số liệu trong ví dụ là dữ liệu giả lập để học.",
        co=11, mau=XAM)


def slide2(prs, sp, mau):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    hop(s, 0, 0, 13.333, 7.5, fill=NEN)
    d = sp["demo"]
    tieu_de(s, "Demo: " + d["ten"], d["mo_ta"], mau, "2/2")
    cot = [(0.45, 3.35, "① Đầu vào", d["dau_vao"]), (3.95, 4.75, "② Prompt", None), (8.85, 4.03, "③ Kết quả", None)]
    for x, w, nhan, _ in cot:
        hop(s, x, 1.42, w, 4.1, fill=TRANG, line=rgb("D9E2EC"), radius=True)
        chu(s, x + 0.25, 1.52, w - 0.5, 0.45, nhan, co=17, mau=mau, dam=True)
    chu(s, 0.7, 2.02, 2.9, 3.4, [(f"•  {f}", {"co": 14, "cach": 6}) for f in d["dau_vao"]])
    hop(s, 4.15, 2.02, 4.35, 3.35, fill=rgb("F0F4F8"), radius=True)
    chu(s, 4.27, 2.1, 4.12, 3.2, [(l, {"co": 13, "font": FONT, "cach": 3}) for l in d["prompt"]])
    kq = d["ket_qua"]
    chu(s, 9.1, 1.98, 3.6, 0.45, kq["nhan_so"], co=12.5, mau=XAM)
    chu(s, 9.1, 2.3, 3.6, 0.7, kq["so"], co=30, mau=mau, dam=True)
    chu(s, 9.1, 3.05, 3.6, 2.4, [(f"•  {x}", {"co": 14, "cach": 5}) for x in kq["y"]])
    hop(s, 0.45, 5.7, 12.43, 0.72, fill=TRANG, line=rgb("D9E2EC"), radius=True)
    hai_phan(s, 0.65, 5.75, 12.1, 0.64, "Khi có connector:  ", mau, d["connector"])
    hop(s, 0.45, 6.55, 12.43, 0.72, fill=DO_NHAT, radius=True)
    hai_phan(s, 0.65, 6.6, 12.1, 0.64, "Người vẫn phải:  ", DO, d["nguoi_lam"])


def hai_phan(s, x, y, w, h, nhan, mau_nhan, text):
    tb = chu(s, x, y, w, h, nhan, co=12.5, mau=mau_nhan, dam=True, giua=True)
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = text
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(12.5), False, XAM_DAM


def main(spec, out):
    sp = json.load(open(spec, encoding="utf-8"))
    mau = rgb(sp.get("mau", "#1F4E79"))
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide1(prs, sp, mau)
    slide2(prs, sp, mau)
    prs.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
