#!/usr/bin/env python3
"""In scripts/qua-tang-10-cau-lenh.html → qua-tang/10_cau_lenh_AI_cho_Ke_toan_DNNVV.pdf (cần Playwright + Chromium).

  python3 scripts/in_qua_tang_pdf.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

GOC = Path(__file__).resolve().parent.parent
NGUON = GOC / "scripts" / "qua-tang-10-cau-lenh.html"
DICH = GOC / "qua-tang" / "10_cau_lenh_AI_cho_Ke_toan_DNNVV.pdf"
CHAN_TRANG = ('<div style="font-size:7.5pt;color:#7f7f7f;width:100%;text-align:right;padding-right:15mm;'
              'font-family:DejaVu Sans,Arial">10 câu lệnh AI cho Kế toán DNNVV · Sự AI · '
              '<span class="pageNumber"></span>/<span class="totalPages"></span></div>')

if __name__ == "__main__":
    DICH.parent.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        trang = b.new_page()
        trang.goto(NGUON.as_uri())
        trang.pdf(path=str(DICH), format="A4", print_background=True, prefer_css_page_size=True,
                  display_header_footer=True, header_template="<div></div>", footer_template=CHAN_TRANG)
        b.close()
    print(f"Đã ghi {DICH}")
