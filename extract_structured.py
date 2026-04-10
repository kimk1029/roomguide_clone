#!/usr/bin/env python3
"""roomguide.kr 미러에서 가게 정보를 구조화해서 추출 (v2)
- 지역/업종/상호/룸수/1부주대/2부주대/TC/RT/영업시간/가격표/본문/이미지/전화번호
"""
import json, re, html
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).parent / "roomguide.kr"
GNINFO = ROOT / "gninfo"
OUT = Path(__file__).parent / "stores.json"

# ---------- HTML → 텍스트/이미지 추출 ----------
class TextExtractor(HTMLParser):
    SKIP_TAGS = {"script","style","noscript","nav","header","footer","svg"}
    def __init__(self):
        super().__init__()
        self.text = []
        self.images = []
        self.skip = 0
        self.title = []
        self.in_title = False
        self.h1 = []
        self.in_h1 = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP_TAGS:
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.in_h1 = True
        if tag == "img" and self.skip == 0:
            src = a.get("src") or a.get("data-src") or ""
            if src and not any(x in src.lower() for x in ("icon","logo","emoji","sprite")):
                if src not in self.images:
                    self.images.append(src)
    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_h1:
            self.h1.append(data)
        if self.skip == 0:
            t = data.strip()
            if t:
                self.text.append(t)

def html_to_lines(path: Path):
    ex = TextExtractor()
    ex.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return {
        "lines": ex.text,
        "images": ex.images,
        "title": html.unescape(" ".join(ex.title)).strip(),
        "h1": html.unescape(" ".join(ex.h1)).strip(),
    }

# ---------- 줄 단위 텍스트에서 필드 파싱 ----------
PRICE_LABELS = {"룸":"rooms", "1부 주대":"price_1bu", "2부 주대":"price_2bu",
                "TC":"tc", "RT":"rt"}

def parse_store(lines):
    """라벨/값이 인접한 두 줄로 나오는 패턴을 파싱"""
    info = {}
    # 모든 라벨이 값 다음 줄에 위치하는 패턴 (값 → 라벨)
    label_map = {"지역":"region","업종":"category","상호":"name", **PRICE_LABELS}
    for i, ln in enumerate(lines):
        if ln in label_map and i > 0:
            info[label_map[ln]] = lines[i-1]

    # 영업상태
    for ln in lines:
        if ln in ("(영업중)","(영업종료)","영업중","영업종료"):
            info["status"] = ln.strip("()")
            break

    # 발행/수정일
    for ln in lines:
        m = re.match(r"발행일\s*(.+)", ln)
        if m: info["published"] = m.group(1).strip()
        m = re.match(r"수정일\s*(.+)", ln)
        if m: info["updated"] = m.group(1).strip()

    # 영업시간 (HH:MM~HH:MM 패턴)
    hours = []
    for ln in lines:
        m = re.findall(r"\d{1,2}:\d{2}\s*~\s*\d{1,2}:\d{2}", ln)
        hours.extend(m)
    if hours:
        info["hours"] = list(dict.fromkeys(hours))

    # 가격표 (1인/2인/3인/4인 → 총액)
    table = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^(\d)인$", ln)
        if m and i+1 < len(lines):
            nxt = lines[i+1]
            mp = re.match(r"^(\d+)\s*만원$", nxt)
            if mp:
                table.setdefault("by_persons", []).append({
                    "persons": int(m.group(1)),
                    "total_manwon": int(mp.group(1)),
                })
    if table:
        info["price_table"] = table

    # 본문 (라벨 영역 이후의 긴 문장들)
    body_start = 0
    for i, ln in enumerate(lines):
        if ln == "RT" and i+1 < len(lines):
            body_start = i + 2
            break
    body = []
    for ln in lines[body_start:]:
        if ln in ("인기글","하이퍼블릭 전체보기","쩜오 전체보기","셔츠룸 전체보기",
                  "레깅스룸 전체보기","호스트바 전체보기","가라오케 전체보기","클럽 전체보기"):
            break
        if len(ln) > 15:  # 짧은 라벨/UI 텍스트 제외
            body.append(ln)
    info["body"] = "\n\n".join(body)

    return info

def main():
    pages = sorted(GNINFO.glob("*/index.html"))
    stores = []
    for p in pages:
        data = html_to_lines(p)
        if "페이지를 찾을 수 없" in data["title"]:
            continue
        store = parse_store(data["lines"])
        store.update({
            "slug": p.parent.name,
            "title": data["title"].split("–")[0].strip().split("|")[0].strip(),
            "h1": data["h1"],
            "tel": "010-7604-4361",
            "url_path": str(p.relative_to(ROOT)),
            "images": data["images"][:8],
        })
        stores.append(store)

    OUT.write_text(json.dumps(stores, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(stores)} stores -> {OUT.name}")
    # 카테고리별 카운트
    from collections import Counter
    cnt = Counter(s.get("category","?") for s in stores)
    for k,v in cnt.most_common():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
