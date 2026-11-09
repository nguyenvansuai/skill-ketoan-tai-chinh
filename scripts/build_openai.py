#!/usr/bin/env python3
"""Sinh gói plugin cho ChatGPT / Codex (OpenAI) từ bộ skill của repo: python3 scripts/build_openai.py

Đọc scripts/openai_config.json rồi tạo (ghi đè) thư mục openai/<tên-plugin>/ theo cấu trúc portable của OpenAI:
  plugin.json (+ extensions.com.openai), skills/, mcp.json (nếu có MCP server), assets/
và file marketplace .agents/plugins/marketplace.json để cài qua Codex CLI / ChatGPT desktop.
Theo hướng dẫn "Submit your Claude Code plugin to OpenAI":
  - commands/ và agents/ (chỉ Claude hiểu) được chuyển thành skill;
  - câu chữ nhắc riêng Claude được thay bằng cách nói trung tính (bảng thay_the trong cấu hình).
Thư mục openai/ là sản phẩm sinh tự động – không sửa tay, sửa skills/ gốc rồi chạy lại script.
"""
import json
import re
import shutil
import zipfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
CH = json.loads((GOC / "scripts" / "openai_config.json").read_text(encoding="utf-8"))
TEN = CH["plugin_name"]
RA = GOC / "openai" / TEN
BO_QUA = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for k, v in re.findall(r"^([\w-]+):\s*(.*)$", m.group(1), re.M):
        meta[k] = v.strip().strip('"')
    return meta, m.group(2)


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)  # chuỗi JSON là YAML hợp lệ, an toàn với dấu hai chấm, ngoặc kép


def thay_the(text):
    for cu, moi in CH.get("thay_the", []):
        text = text.replace(cu, moi)
    text = re.sub(r"\bagent `([\w-]+)`", r"skill `\1`", text)
    text = re.sub(r"Giao (thêm )?agent", "Dùng thêm skill", text)
    return text


def ghi_skill(thu_muc, ten, mo_ta, than):
    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / "SKILL.md").write_text(f"---\nname: {ten}\ndescription: {yaml_str(mo_ta)}\n---\n\n{than.strip()}\n",
                                      encoding="utf-8")


def sao_skills():
    dich = RA / "skills"
    ten_da_co = set()
    for sk in sorted((GOC / CH.get("skills_dir", "skills")).iterdir()):
        if not (sk / "SKILL.md").exists():
            continue
        shutil.copytree(sk, dich / sk.name, ignore=BO_QUA)
        ten_da_co.add(sk.name)
        for f in (dich / sk.name).rglob("*.md"):
            f.write_text(thay_the(f.read_text(encoding="utf-8")), encoding="utf-8")
    chuyen = []
    for loai in ("commands", "agents"):
        thu_muc = GOC / loai
        if not thu_muc.exists():
            continue
        for f in sorted(thu_muc.glob("*.md")):
            meta, than = frontmatter(f.read_text(encoding="utf-8"))
            ten = meta.get("name") or f.stem
            if ten in ten_da_co:
                raise SystemExit(f"Trùng tên skill khi chuyển {loai}/{f.name}: {ten}")
            mo_ta = meta.get("description", "")
            if loai == "commands":
                goi_y = meta.get("argument-hint", "").strip('"')
                than = than.replace("$ARGUMENTS", "yêu cầu của người dùng")
                if goi_y:
                    than = f"Thông tin cần có từ người dùng: {goi_y}. Thiếu thông tin quan trọng thì hỏi gọn một lần.\n\n" + than
                mo_ta = f"Quy trình trọn gói: {mo_ta}"
            else:
                than = ("Thực hiện như một người thẩm định/phản biện độc lập: đọc lại tài liệu từ đầu, không mặc định "
                        "phần đã soạn là đúng.\n\n" + than)
            ghi_skill(dich / ten, ten, thay_the(mo_ta), thay_the(than))
            ten_da_co.add(ten)
            chuyen.append(f"{loai}/{f.name} → skills/{ten}")
    return sorted(ten_da_co), chuyen


def ghi_manifest(ds_skill):
    goc_claude = GOC / ".claude-plugin" / "plugin.json"
    ver = json.loads(goc_claude.read_text(encoding="utf-8")).get("version", "1.0.0") if goc_claude.exists() else CH.get("version", "1.0.0")
    oa = {
        "interface": {
            "displayName": CH["display_name"],
            "shortDescription": CH["short_description"],
            "longDescription": CH["long_description"],
            "developerName": CH.get("developer_name", "nguyenvansuai"),
            "category": CH.get("category", "Productivity"),
            "capabilities": CH.get("capabilities", ["Read", "Write"]),
            "websiteURL": CH["repository"],
            "defaultPrompt": CH["default_prompts"],
            "brandColor": CH.get("brand_color", "#1F4E79"),
            "composerIcon": "./assets/icon.png",
            "logo": "./assets/logo.png",
        }
    }
    data = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": TEN,
        "version": ver,
        "description": CH["short_description"],
        "author": {"name": CH.get("developer_name", "nguyenvansuai"), "url": "https://github.com/nguyenvansuai"},
        "homepage": CH["repository"],
        "repository": CH["repository"],
        "license": "MIT",
        "keywords": CH.get("keywords", []),
        "extensions": {"com.openai": oa},
    }
    (RA / "plugin.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ghi_mcp():
    m = CH.get("mcp")
    if not m:
        return False
    for d in m.get("thu_muc_kem", []):
        shutil.copytree(GOC / d, RA / d, ignore=BO_QUA)
    data = {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
            "mcpServers": {m["name"]: {"type": "stdio", "command": m.get("command", "python3"),
                                       "args": m["args"], "cwd": "${PLUGIN_ROOT}",
                                       "env": {"PLUGIN_MCP_NAME": m["name"]}}}}
    (RA / "mcp.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def ghi_assets():
    (RA / "assets").mkdir(parents=True, exist_ok=True)
    icon = GOC / CH.get("icon", ".claude-plugin/icon.png")
    if not icon.exists():
        raise SystemExit(f"Thiếu icon: {icon}")
    shutil.copy(icon, RA / "assets" / "icon.png")
    shutil.copy(icon, RA / "assets" / "logo.png")


def ghi_readme(ds_skill, co_mcp, chuyen):
    dong = [f"# {CH['display_name']} – gói cho ChatGPT / Codex", "",
            "Thư mục này được sinh tự động bởi `scripts/build_openai.py` – không sửa tay.", "",
            CH["long_description"], "", f"## Skill ({len(ds_skill)})", ""]
    dong += [f"- `{s}`" for s in ds_skill]
    if chuyen:
        dong += ["", "Chuyển từ lệnh/agent của bản Claude:", ""] + [f"- {c}" for c in chuyen]
    dong += ["", "## Cài đặt", "", "Xem README ở gốc repo, mục **ChatGPT / Codex**."]
    if co_mcp:
        dong += ["", "Gói có MCP server chạy cục bộ (Python 3.8+) → chỉ dùng được trên **ChatGPT desktop / Codex**. "
                 "Skill vẫn tự tính bằng `scripts/cong_cu.py` khi không có MCP."]
    (RA / "README.md").write_text("\n".join(dong) + "\n", encoding="utf-8")


def ghi_marketplace():
    p = GOC / ".agents" / "plugins" / "marketplace.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"name": CH.get("marketplace_name", GOC.name),
            "interface": {"displayName": CH["display_name"]},
            "plugins": [{"name": TEN, "source": {"source": "local", "path": f"./openai/{TEN}"},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                         "category": CH.get("category", "Productivity")}]}
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dong_goi():
    dist = GOC / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{TEN}-chatgpt.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(RA.rglob("*")):
            if f.is_file():
                z.write(f, Path(TEN) / f.relative_to(RA))
    return out


def kiem_tra(ds_skill):
    loi = []
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", TEN):
        loi.append("plugin_name phải là kebab-case")
    for s in ds_skill:
        meta, than = frontmatter((RA / "skills" / s / "SKILL.md").read_text(encoding="utf-8"))
        if meta.get("name") != s:
            loi.append(f"{s}: name trong SKILL.md khác tên thư mục")
        if not meta.get("description"):
            loi.append(f"{s}: thiếu description")
        if re.search(r"\bClaude\b|claude\.ai|\$ARGUMENTS", than):
            loi.append(f"{s}: còn nhắc Claude hoặc $ARGUMENTS")
        for ref in re.findall(r"`((?:references|scripts)/[\w./-]+\.\w+)", than):
            if not (RA / "skills" / s / ref).exists():
                loi.append(f"{s}: thiếu file {ref}")
    for f in RA.rglob("SKILL.md"):
        if re.search(r"\bClaude\b", f.read_text(encoding="utf-8")):
            loi.append(f"{f.relative_to(RA)}: còn chữ Claude")
    if len(CH["default_prompts"]) > 3:
        loi.append("default_prompts nên tối đa 3 câu")
    return loi


if __name__ == "__main__":
    shutil.rmtree(RA, ignore_errors=True)
    RA.mkdir(parents=True)
    ds, chuyen = sao_skills()
    ghi_manifest(ds)
    co_mcp = ghi_mcp()
    ghi_assets()
    ghi_readme(ds, co_mcp, chuyen)
    ghi_marketplace()
    loi = kiem_tra(ds)
    z = dong_goi()
    print(f"Gói ChatGPT/Codex: openai/{TEN}/ – {len(ds)} skill{' + MCP' if co_mcp else ''}; zip: {z.relative_to(GOC)}")
    for c in chuyen:
        print("  chuyển", c)
    if loi:
        print("LỖI:\n" + "\n".join("  - " + x for x in loi))
        raise SystemExit(1)
