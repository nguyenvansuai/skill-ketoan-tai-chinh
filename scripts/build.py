#!/usr/bin/env python3
"""Đồng bộ tài liệu dùng chung, kiểm tra, sinh bản ChatGPT, marketplace và đóng gói zip.

Chạy từ thư mục gốc repo:  python3 scripts/build.py          (build đầy đủ)
                           python3 scripts/build.py --test   (thêm: chạy --self-test của mọi script)

1. Chép shared/* vào skills/<skill>/references/ theo SHARED_MAP (mỗi skill tự đủ, cài riêng lẻ được)
2. Kiểm tra frontmatter, đường dẫn references/scripts nhắc trong SKILL.md
3. Sinh chatgpt/<skill>.md: hướng dẫn dán vào Project / Custom GPT
4. Sinh .claude-plugin/marketplace.json (cài bằng /plugin trong Claude Code)
5. Đóng gói dist/<skill>.zip (upload claude.ai) và dist/tat-ca-skill.zip
"""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
SKILLS = GOC / "skills"
SHARED = GOC / "shared"

CHUNG = ["nguyen-tac-chung.md", "van-ban-hieu-luc.md"]
CHE_DO = ["che-do-ke-toan-dnnvv.md", "tai-khoan-tt133.csv"]
THUE = ["thue-dn-2026.md"]
SHARED_MAP = {
    "che-do-ke-toan": CHE_DO,
    "dinh-khoan": CHE_DO + THUE,
    "doc-hoa-don-xml": THUE,
    "doi-soat": [],
    "khoa-so-cuoi-ky": CHE_DO + THUE,
    "bao-cao-tai-chinh": CHE_DO,
    "thue-gtgt-dn": THUE,
    "thue-tndn": THUE,
    "luong-bao-hiem": THUE,
    "thue-nha-thau": THUE,
    "lich-thue-dn": THUE,
    "dong-tien-chu-dn": THUE,
}
GIOI_HAN_GPT = 8000  # ký tự tối đa ô Instructions của Custom GPT
DANH_MUC = "ke-toan-tai-chinh"


def ds_skill():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def dong_bo():
    for sk in ds_skill():
        ref = sk / "references"
        ref.mkdir(exist_ok=True)
        for f in CHUNG + SHARED_MAP.get(sk.name, []):
            shutil.copy(SHARED / f, ref / f)


def tach_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("thiếu frontmatter")
    meta = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    return meta, m.group(2).strip()


def kiem_tra():
    loi = []
    ten_skill = {sk.name for sk in ds_skill()}
    if ten_skill != set(SHARED_MAP):
        loi.append(f"SHARED_MAP không khớp thư mục skills: thừa {set(SHARED_MAP) - ten_skill}, thiếu {ten_skill - set(SHARED_MAP)}")
    for sk in ds_skill():
        try:
            meta, body = tach_frontmatter((sk / "SKILL.md").read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError) as e:
            loi.append(f"{sk.name}: SKILL.md lỗi ({e})")
            continue
        if meta.get("name") != sk.name:
            loi.append(f"{sk.name}: name trong frontmatter không khớp tên thư mục")
        if not 50 < len(meta.get("description", "")) <= 1024:
            loi.append(f"{sk.name}: description dài {len(meta.get('description', ''))} ký tự (cần 51–1024)")
        for ref in re.findall(r"`((?:references|scripts)/[\w./-]+)`", body):
            if not (sk / ref).exists():
                loi.append(f"{sk.name}: SKILL.md nhắc `{ref}` nhưng không có file")
    return loi


def chay_self_test():
    loi = []
    for sk in ds_skill():
        for py in sorted((sk / "scripts").glob("*.py")) if (sk / "scripts").exists() else []:
            r = subprocess.run([sys.executable, str(py), "--self-test"], capture_output=True, text=True, cwd=str(py.parent))
            trang_thai = "OK " if r.returncode == 0 else "LỖI"
            print(f"  [{trang_thai}] {sk.name}/scripts/{py.name}")
            if r.returncode != 0:
                loi.append(f"{sk.name}/{py.name}: self-test lỗi\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
    return loi


def sinh_chatgpt():
    out = GOC / "chatgpt"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    canh_bao = []
    for sk in ds_skill():
        meta, body = tach_frontmatter((sk / "SKILL.md").read_text(encoding="utf-8"))
        body = body.replace("references/", "file Knowledge ").replace("scripts/", "")
        huong_dan = (
            "Bạn là trợ lý kế toán – tài chính cho doanh nghiệp nhỏ và vừa Việt Nam. Luôn trả lời bằng tiếng Việt có dấu.\n"
            "Các file nhắc tới (nguyen-tac-chung.md, van-ban-hieu-luc.md, ...) đã được tải lên mục Knowledge; đọc chúng khi cần.\n"
            "Script Python (.py) chạy bằng Code Interpreter nếu được bật; nếu không, tính cẩn thận từng bước và ghi rõ chưa chạy script.\n\n"
            + body
        )
        files = sorted(f.name for f in (sk / "references").iterdir() if f.is_file())
        scripts = sorted(f.name for f in (sk / "scripts").glob("*.py")) if (sk / "scripts").exists() else []
        noi_dung = [
            f"# {sk.name} – bản dùng cho ChatGPT",
            "",
            f"**Mô tả:** {meta.get('description', '')}",
            "",
            "## Cách cài",
            "1. ChatGPT miễn phí: tạo Project mới, mở phần hướng dẫn (instructions) của Project. Bản trả phí: có thể tạo Custom GPT (Explore GPTs → Create → Configure).",
            f"2. Name: `{sk.name}`. Description: copy dòng Mô tả ở trên.",
            "3. Dán toàn bộ khối **Instructions** bên dưới vào ô hướng dẫn.",
            "4. Tải lên (Project files hoặc Knowledge) các file " + ", ".join(f"`skills/{sk.name}/references/{f}`" for f in files) + ".",
        ]
        if scripts:
            noi_dung.append("5. Bật **Code Interpreter & Data Analysis** và tải thêm " +
                            ", ".join(f"`skills/{sk.name}/scripts/{s}`" for s in scripts) + ".")
        noi_dung += ["", "## Instructions", "", "````markdown", huong_dan, "````", ""]
        (out / f"{sk.name}.md").write_text("\n".join(noi_dung), encoding="utf-8")
        if len(huong_dan) > GIOI_HAN_GPT:
            canh_bao.append(f"  ! {sk.name}: Instructions {len(huong_dan)} ký tự > {GIOI_HAN_GPT} (Custom GPT sẽ cắt; Project không giới hạn)")
    return canh_bao


def sinh_marketplace():
    """Mỗi skill là 1 plugin (source ./skills/<x>); gói trọn bộ source "./" dùng .claude-plugin/plugin.json và .mcp.json ở gốc."""
    plugins = []
    ds = ds_skill()
    for sk in ds:
        meta, _ = tach_frontmatter((sk / "SKILL.md").read_text(encoding="utf-8"))
        plugins.append({"name": sk.name, "source": f"./skills/{sk.name}",
                        "description": meta["description"], "category": DANH_MUC})
    plugins.append({
        "name": "tron-bo-skill-ke-toan",
        "source": "./",
        "description": f"Cài cả bộ {len(ds)} skill kế toán – tài chính cho DN nhỏ và vừa: " + ", ".join(sk.name for sk in ds) + ".",
        "category": DANH_MUC,
    })
    data = {
        "name": "skill-ketoan-tai-chinh",
        "description": f"Bộ {len(ds)} skill AI kế toán – tài chính cho doanh nghiệp nhỏ, vừa và siêu nhỏ Việt Nam 2026 "
                       "(TT133/2016, TT58/2026, Luật TNDN 67/2025, NĐ 252/2026, NĐ 254/2026).",
        "owner": {"name": "nguyenvansuai", "url": "https://github.com/nguyenvansuai"},
        "plugins": plugins,
    }
    out = GOC / ".claude-plugin"
    out.mkdir(exist_ok=True)
    (out / "marketplace.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dong_goi():
    dist = GOC / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    dist.mkdir()
    with zipfile.ZipFile(dist / "tat-ca-skill.zip", "w", zipfile.ZIP_DEFLATED) as tat_ca:
        for sk in ds_skill():
            with zipfile.ZipFile(dist / f"{sk.name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(sk.rglob("*")):
                    if f.is_file() and "__pycache__" not in f.parts and "tests" not in f.relative_to(sk).parts[:1]:
                        z.write(f, f.relative_to(SKILLS))
                        tat_ca.write(f, f.relative_to(SKILLS))


if __name__ == "__main__":
    import sys as _sys
    _sys.path.insert(0, str(GOC / "scripts"))
    import ket_noi
    ket_noi.chuan_bi()
    dong_bo()
    loi = kiem_tra() + ket_noi.kiem_tra()
    if "--test" in sys.argv:
        print("Chạy self-test script:")
        loi += chay_self_test()
    canh_bao = sinh_chatgpt()
    sinh_marketplace()
    dong_goi()
    ket_noi.hoan_tat()  # mcpServers cho skill lẻ + dist/<plugin>.plugin (sau dong_goi vì dong_goi xóa dist/)
    import subprocess
    subprocess.run([_sys.executable, str(GOC / "scripts" / "build_openai.py")], check=True)
    print(f"Đã build {len(ds_skill())} skill.")
    for c in canh_bao:
        print(c)
    if loi:
        print("LỖI:")
        print("\n".join("  - " + x for x in loi))
        raise SystemExit(1)
