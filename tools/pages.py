# -*- coding: utf-8 -*-
"""第三批：作品集頁與工具／App 介紹頁 → Markdown。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from to_md import SITE, BASE, inline, convert, meta, title_of, _BASEDIR

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "pages")

# (檔案, 輸出資料夾, 輸出檔名)
WORK = ["costume-photo", "diving", "document-kit", "lion-character",
        "reading-template", "shiftok", "sugar-boom", "visual-scenes", "yijian"]
TARGETS = [("index.html", "site", "portfolio-home")] \
    + [("work/%s.html" % w, "work", w) for w in WORK] \
    + [("bazi/index.html", "apps", "shilai-bazi-app"),
       ("ziwei/index.html", "apps", "shilai-ziwei-app"),
       ("astrology/index.html", "apps", "shilai-astrology-app"),
       ("yijian-web/index.html", "tools", "yijian-web"),
       ("yijian-web/cast/index.html", "tools", "yijian-cast"),
       ("bazi-web/index.html", "tools", "bazi-web"),
       ("ziwei-web/index.html", "tools", "ziwei-web"),
       ("astrology-web/index.html", "tools", "astrology-web"),
       ("en/index.html", "site", "all-tools-en")]

def canon(h):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    return m.group(1) if m else ""

def main_of(h):
    """沒有統一的 <article>，取 <main> 或 <body>，先剝掉 script/style/nav/footer/header。"""
    # 這批的 <article> 多半是重複的卡片（首頁就有 17 個），不是正文容器，所以 <main> 優先
    m = re.search(r"<main[^>]*>(.*?)</main>", h, re.S) or \
        re.search(r"<article[^>]*>(.*?)</article>", h, re.S) or \
        re.search(r"<body[^>]*>(.*?)</body>", h, re.S)
    seg = m.group(1) if m else h
    for tag in ("script", "style", "nav", "footer", "header"):
        seg = re.sub(r"<%s[^>]*>.*?</%s>" % (tag, tag), "", seg, flags=re.S | re.I)
    return seg

def split_en(h):
    i = h.find('<section id="en"')
    if i < 0:
        return h, None
    j = h.find("</section>", i)
    return h[:i], h[i:j if j > 0 else len(h)]

def wrap(t, d, url, bodymd, lang):
    if lang == "zh":
        note = "> 這是鏡像版本。**原文與最新版本**在 %s" % url
        author = "作者：[Wei Chun Chuang](%s/learn/about.html)" % BASE
        lic = "本頁文字以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hant) 授權；App 名稱、圖示、程式碼與介面設計不在授權範圍內。"
        src = "原文"
    else:
        note = "> This is a mirror. The **canonical, most up-to-date version** is at %s" % url
        author = "Written by [Wei Chun Chuang](%s/learn/en/about.html)" % BASE
        lic = "Page text licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); app names, icons, source code and interface design are not covered."
        src = "Source"
    md = "# %s\n\n%s\n\n%s\n\n%s\n\n---\n\n%s\n\n---\n\n%s  \n%s: %s\n" % (
        t, note, author, "*%s*" % d if d else "", bodymd, lic, src, url)
    return re.sub(r"\n{3,}", "\n\n", md)

def run(write=False):
    rows = []
    for rel, folder, name in TARGETS:
        p = os.path.join(SITE, rel)
        h = open(p, encoding="utf-8").read()
        url = canon(h) or BASE + "/" + rel.replace("index.html", "")
        tm = re.search(r"<title>([^<]*)", h)
        t = re.sub(r"\s*[｜|][^｜|]*$", "", tm.group(1)).strip() if tm else (title_of(h) or name)
        d = meta(h, "description")
        _BASEDIR[0] = "/" + (os.path.dirname(rel) + "/" if os.path.dirname(rel) else "")
        zh_part, en_part = split_en(h)
        lang0 = "en" if rel.startswith("en/") else "zh"
        outs = [(lang0, wrap(t, d, url, convert(main_of(zh_part)), lang0))]
        if en_part:
            en_t = title_of(en_part) or t
            outs.append(("en", wrap(en_t, "", url, convert(en_part), "en")))
        for lang, md in outs:
            rows.append((folder, lang, name, t, len(md), url))
            if write:
                od = os.path.join(OUT, folder, lang)
                os.makedirs(od, exist_ok=True)
                open(os.path.join(od, name + ".md"), "w", encoding="utf-8").write(md)
    return rows

if __name__ == "__main__":
    w = len(sys.argv) > 1 and sys.argv[1] == "write"
    rows = run(w)
    import collections
    c = collections.Counter((r[0], r[1]) for r in rows)
    for k in sorted(c): print("  %-8s %s  %2d 頁" % (k[0], k[1], c[k]))
    print("  合計 %d 頁，%.0f KB" % (len(rows), sum(r[4] for r in rows) / 1024))
    print("  可疑：", [(r[0], r[1], r[2], r[4]) for r in rows if r[4] < 500 or not r[3]] or "無")
    if w: print("  已寫入", OUT)
