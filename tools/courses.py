# -*- coding: utf-8 -*-
"""第一批：八字／紫微／星座課程頁 → Markdown 鏡像。沿用 to_md.py 的轉換函式。"""
import glob, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from to_md import SITE, BASE, inline, convert, meta, title_of

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "courses")
APPS = {"bazi-web/learn": ("bazi", "八字"), "ziwei-web/learn": ("ziwei", "紫微斗數"),
        "astrology-web/learn": ("astrology", "西洋占星")}

def body_of(h):
    m = re.search(r"<article[^>]*>(.*?)</article>", h, re.S)
    return m.group(1) if m else ""

def canon(h):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    return m.group(1) if m else ""

def build(path, app, code, lang):
    h = open(path, encoding="utf-8").read()
    url = canon(h) or BASE + "/" + path[len(SITE) + 1:].replace("index.html", "")
    t = title_of(h) or ""
    d = meta(h, "description")
    if lang == "zh":
        note = "> 這是鏡像版本。**原文與最新版本**在 %s" % url
        author = "作者：[Wei Chun Chuang](%s/learn/about.html)" % BASE
        lic = "本課程文字以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hant) 授權，標明出處即可自由轉載與改寫。"
        src = "原文"
    else:
        note = "> This is a mirror. The **canonical, most up-to-date version** is at %s" % url
        author = "Written by [Wei Chun Chuang](%s/learn/en/about.html)" % BASE
        lic = "Lesson text licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse and adapt freely with attribution."
        src = "Source"
    md = "# %s\n\n%s\n\n%s\n\n%s\n\n---\n\n%s\n\n---\n\n%s  \n%s: %s\n" % (
        t, note, author, "*%s*" % d if d else "", convert(body_of(h)), lic, src, url)
    return re.sub(r"\n{3,}", "\n\n", md), t, url

def run(write=False):
    rows = []
    for d, (app, label) in APPS.items():
        for p in sorted(glob.glob(os.path.join(SITE, d, "*", "index.html"))):
            code = os.path.basename(os.path.dirname(p))
            # en/ 是英文索引頁、review/ 是互動複習工具，都不是課程內文
            if code in ("en", "review"):
                continue
            for lang, pp in (("zh", p), ("en", os.path.join(os.path.dirname(p), "en", "index.html"))):
                if not os.path.exists(pp):
                    continue
                md, t, url = build(pp, app, code, lang)
                rows.append((app, lang, code, t, len(md), url))
                if write:
                    od = os.path.join(OUT, app, lang)
                    os.makedirs(od, exist_ok=True)
                    open(os.path.join(od, code + ".md"), "w", encoding="utf-8").write(md)
    return rows

if __name__ == "__main__":
    w = len(sys.argv) > 1 and sys.argv[1] == "write"
    rows = run(w)
    import collections
    c = collections.Counter((r[0], r[1]) for r in rows)
    for k in sorted(c): print("  %-10s %s  %3d 頁" % (k[0], k[1], c[k]))
    print("  合計 %d 頁，%.0f KB" % (len(rows), sum(r[4] for r in rows) / 1024))
    bad = [(r[0], r[1], r[2]) for r in rows if r[4] < 900 or not r[3] or not r[5]]
    print("  可疑（過短／無標題／無網址）：", bad or "無")
    if w: print("  已寫入", OUT)
