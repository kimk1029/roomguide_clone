#!/usr/bin/env python3
"""roomguide.kr 미러에서 가게 정보(gninfo/*) 본문을 추출해 JSON/CSV/Markdown 으로 저장."""
import json, csv, re, html
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).parent / "roomguide.kr"
GNINFO = ROOT / "gninfo"
OUT_JSON = Path(__file__).parent / "content.json"
OUT_CSV  = Path(__file__).parent / "content.csv"
OUT_MD   = Path(__file__).parent / "content.md"

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""
        self.text_parts = []
        self.skip_depth = 0
        self.h1 = ""
        self.in_h1 = False
        self.images = []
        self.in_main = False
        self.main_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag in ("script","style","noscript","nav","header","footer"):
            self.skip_depth += 1
        elif tag == "main" or (tag in ("section","div") and "brxe-post-content" in (a.get("class") or "")):
            self.in_main = True
            self.main_depth += 1
        elif self.in_main and tag in ("section","div","article"):
            self.main_depth += 1
        elif tag == "img" and self.in_main:
            src = a.get("src") or a.get("data-src") or ""
            if src and "icon" not in src.lower():
                self.images.append(src)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag in ("script","style","noscript","nav","header","footer"):
            self.skip_depth = max(0, self.skip_depth - 1)
        elif self.in_main and tag in ("main","section","div","article"):
            self.main_depth -= 1
            if self.main_depth <= 0:
                self.in_main = False

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1 += data
        if self.in_main:
            t = data.strip()
            if t:
                self.text_parts.append(t)

def extract(path: Path):
    ex = Extractor()
    raw = path.read_text(encoding="utf-8", errors="ignore")
    ex.feed(raw)
    title = html.unescape(ex.title.strip())
    if "페이지를 찾을 수 없" in title:
        return None
    body = "\n".join(ex.text_parts)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return {
        "slug": path.parent.name,
        "title": title.split("–")[0].strip(),
        "h1": html.unescape(ex.h1.strip()),
        "url_path": str(path.relative_to(ROOT)),
        "images": ex.images[:10],
        "body": body[:5000],
        "body_chars": len(body),
    }

def main():
    pages = sorted(GNINFO.glob("*/index.html"))
    rows = []
    for p in pages:
        item = extract(p)
        if item:
            rows.append(item)

    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["slug","title","h1","url_path","body_chars","images"], extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "images": " | ".join(r["images"])})

    md = ["# 강남룸가이드 - 가게 콘텐츠 추출\n", f"총 {len(rows)}개 페이지\n"]
    for r in rows:
        md.append(f"## {r['title']}\n")
        md.append(f"- slug: `{r['slug']}` · 본문 {r['body_chars']}자\n")
        if r["images"]:
            md.append(f"- 대표이미지: {r['images'][0]}\n")
        md.append("\n```\n" + r["body"][:600] + "\n```\n")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"OK pages={len(rows)}  ->  {OUT_JSON.name}, {OUT_CSV.name}, {OUT_MD.name}")

if __name__ == "__main__":
    main()
