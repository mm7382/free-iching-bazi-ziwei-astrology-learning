# -*- coding: utf-8 -*-
"""第二批：易見六十四卦（65×2）與八堂課（9×2）→ Markdown。這批沒有 <article>，正文在 div.frame。"""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from to_md import SITE, BASE, inline, convert, meta, title_of

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "courses")
SETS = {"yijian-web/hexagrams": "hexagrams", "yijian-web/lessons": "yijian-lessons"}

def body_of(h):
    """沒有 article，取 frame 之後到 </body>，並先拿掉 script/style/nav/footer/header。"""
    i = h.find('<div class="frame"')
    seg = h[i:] if i > 0 else h
    j = seg.find("</body>")
    if j > 0:
        seg = seg[:j]
    for tag in ("script", "style", "nav", "footer", "header"):
        seg = re.sub(r"<%s[^>]*>.*?</%s>" % (tag, tag), "", seg, flags=re.S | re.I)
    return seg

def canon(h):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    return m.group(1) if m else ""

def build(path, lang):
    h = open(path, encoding="utf-8").read()
    url = canon(h) or BASE + "/" + path[len(SITE) + 1:].replace("index.html", "")
    # 這批的 h1 很短（例「乾卦」），<title> 才是完整描述（例「乾卦：原文、白話與六爻解釋」），取後者
    tm = re.search(r"<title>([^<]*)", h)
    t = re.sub(r"\s*[｜|][^｜|]*$", "", tm.group(1)).strip() if tm else ""
    t = t or title_of(h)
    d = meta(h, "description")
    if lang == "zh":
        note = "> 這是鏡像版本。**原文與最新版本**在 %s" % url
        author = "作者：[Wei Chun Chuang](%s/learn/about.html)" % BASE
        lic = "白話解說文字以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hant) 授權；《周易》經傳原文屬公有領域。"
        src = "原文"
    else:
        note = "> This is a mirror. The **canonical, most up-to-date version** is at %s" % url
        author = "Written by [Wei Chun Chuang](%s/learn/en/about.html)" % BASE
        lic = "Plain-language commentary licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the classical text of the Zhou Yi is in the public domain."
        src = "Source"
    md = "# %s\n\n%s\n\n%s\n\n%s\n\n---\n\n%s\n\n---\n\n%s  \n%s: %s\n" % (
        t, note, author, "*%s*" % d if d else "", convert(body_of(h)), lic, src, url)
    return re.sub(r"\n{3,}", "\n\n", md), t, url

def run(write=False):
    rows = []
    for d, name in SETS.items():
        for p in sorted(glob.glob(os.path.join(SITE, d, "*", "index.html")),
                        key=lambda x: (not os.path.basename(os.path.dirname(x)).isdigit(),
                                       int(os.path.basename(os.path.dirname(x)))
                                       if os.path.basename(os.path.dirname(x)).isdigit() else 0)):
            code = os.path.basename(os.path.dirname(p))
            if code == "en":
                continue
            for lang, pp in (("zh", p), ("en", os.path.join(os.path.dirname(p), "en", "index.html"))):
                if not os.path.exists(pp):
                    continue
                md, t, url = build(pp, lang)
                rows.append((name, lang, code, t, len(md), url))
                if write:
                    od = os.path.join(OUT, name, lang)
                    os.makedirs(od, exist_ok=True)
                    open(os.path.join(od, code.zfill(2) if code.isdigit() else code) + ".md",
                         "w", encoding="utf-8").write(md)
    return rows

if __name__ == "__main__":
    w = len(sys.argv) > 1 and sys.argv[1] == "write"
    rows = run(w)
    import collections
    c = collections.Counter((r[0], r[1]) for r in rows)
    for k in sorted(c): print("  %-16s %s  %3d 頁" % (k[0], k[1], c[k]))
    print("  合計 %d 頁，%.0f KB" % (len(rows), sum(r[4] for r in rows) / 1024))
    bad = [(r[0], r[1], r[2], r[4]) for r in rows if r[4] < 900 or not r[3]]
    print("  可疑：", bad[:6] or "無")
    leak = [(r[0], r[2]) for r in rows if False]
    if w: print("  已寫入", OUT)
