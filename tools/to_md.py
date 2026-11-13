# -*- coding: utf-8 -*-
"""把 mm7382.github.io 的 /learn/ 與 /learn/en/ 文章轉成 Markdown 鏡像。
只讀網站、只寫 repo 目錄，不改網站任何檔案。"""
import glob, html, os, re, sys

SITE = "/Users/michaelchuang/Documents/遊戲/mm7382.github.io"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = REPO
BASE = "https://mm7382.github.io"
SKIP = {"index.html"}

def strip_en_section(h):
    """中文頁裡藏著整份英文，鏡像中文版時要切掉，避免同一檔中英混雜。"""
    i = h.find('<section id="en"')
    return h[:i] if i > 0 else h

def body_of(h):
    """中文頁切掉英文區後 </article> 也被切掉了，所以要容許沒有結尾標籤。"""
    m = re.search(r"<article[^>]*>(.*?)</article>", h, re.S)
    if m:
        return m.group(1)
    m = re.search(r"<article[^>]*>(.*)", h, re.S)
    return m.group(1) if m else ""

_BASEDIR = [""]          # 目前轉換中的頁面所在目錄，例如 "/ziwei-web/"

def absolutize(u):
    if u.startswith(("http://", "https://", "mailto:", "#")):
        return u
    if u.startswith("/"):
        return BASE + u
    if u.startswith("./"):
        u = u[2:]
    return BASE + _BASEDIR[0] + u

def inline(s):
    s = re.sub(r"<br\s*/?>", "  \n", s, flags=re.I)
    s = re.sub(r"<(strong|b)[^>]*>(.*?)</\1>", lambda m: "**%s**" % m.group(2).strip(), s, flags=re.S | re.I)
    s = re.sub(r"<(em|i)[^>]*>(.*?)</\1>", lambda m: "*%s*" % m.group(2).strip(), s, flags=re.S | re.I)
    s = re.sub(r"<code[^>]*>(.*?)</code>", lambda m: "`%s`" % m.group(1).strip(), s, flags=re.S | re.I)
    s = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
               lambda m: "[%s](%s)" % (
                   re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip(),
                   absolutize(m.group(1))),
               s, flags=re.S | re.I)
    # 區塊級結束標籤要留一個空白，否則巢狀的古文／翻譯／出處會黏成一串
    s = re.sub(r"</(p|blockquote|cite|div|li|dd|dt|figcaption|h[1-6])>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"[ \t]+", " ", s).strip()

BLOCK = re.compile(
    r"<(h1|h2|h3|h4|p|li|dt|dd|blockquote)([^>]*)>(.*?)</\1>|<(table)[^>]*>(.*?)</table>",
    re.S | re.I)

def convert(body):
    # App 下載卡片是推銷元件不是內文，而且它的標題與按鈕不在可匹配的區塊裡，
    # 只抓得到中間那句說明，留著反而是半截。整張拿掉。
    body = re.sub(r"<aside[^>]*class=\"[^\"]*app-cta[^\"]*\"[^>]*>.*?</aside>", "", body, flags=re.S | re.I)
    out, in_dl = [], False
    for m in BLOCK.finditer(body):
        tag = (m.group(1) or m.group(4)).lower()
        raw = m.group(3) if m.group(1) else m.group(5)
        if tag == "table":
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S | re.I)
            lines = []
            for ri, r in enumerate(rows):
                cells = [inline(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S | re.I)]
                if not cells:
                    continue
                lines.append("| " + " | ".join(cells) + " |")
                if ri == 0:
                    lines.append("|" + "---|" * len(cells))
            if lines:
                out.append("\n".join(lines))
            continue
        t = inline(raw)
        if not t:
            continue
        if re.match(r"^(作者：Wei Chun Chuang|Written by Wei Chun Chuang|By Wei Chun Chuang)", t):
            continue                       # 與檔頭的作者行重複
        if tag == "h1":
            continue                       # 標題另外處理，不重複
        elif tag in ("h2", "h3", "h4"):
            out.append("#" * int(tag[1]) + " " + t)
            in_dl = False
        elif tag == "li":
            out.append("- " + t)
        elif tag == "dt":
            out.append("**" + t + "**")
            in_dl = True
        elif tag == "dd":
            out.append(t)
        elif tag == "blockquote":
            out.append("> " + t)
        else:
            out.append(t)
    return "\n\n".join(out)

def meta(h, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % name, h)
    return html.unescape(m.group(1)) if m else ""

def title_of(h):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    return inline(m.group(1)) if m else ""

def build(path, lang):
    slug = os.path.basename(path)[:-5]
    h = open(path, encoding="utf-8").read()
    if lang == "zh":
        h = strip_en_section(h)
        url = "%s/learn/%s.html" % (BASE, slug)
        foot_src, foot_lic = "原文", "本文以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hant) 授權，標明出處即可自由轉載與改寫。"
        note = "> 這是鏡像版本。**原文與最新版本**在 %s" % url
        author = "作者：[Wei Chun Chuang](%s/learn/about.html)" % BASE
    else:
        url = "%s/learn/en/%s.html" % (BASE, slug)
        foot_src, foot_lic = "Source", "Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse and adapt freely with attribution."
        note = "> This is a mirror. The **canonical, most up-to-date version** is at %s" % url
        author = "Written by [Wei Chun Chuang](%s/learn/en/about.html)" % BASE
    dm = re.search(r"(20\d\d-\d\d-\d\d)", h)
    if dm:
        author += "・" + dm.group(1)
    t = title_of(h) or meta(h, "description")[:60]
    d = meta(h, "description")
    md = "# %s\n\n%s\n\n%s\n\n%s\n\n---\n\n%s\n\n---\n\n%s  \n%s: %s\n" % (
        t, note, author, "*%s*" % d if d else "", convert(body_of(h)), foot_lic, foot_src, url)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return slug, t, md, url

def run(write=False):
    rows = []
    for lang, pat, sub in (("zh", "learn/*.html", "zh"), ("en", "learn/en/*.html", "en")):
        for p in sorted(glob.glob(os.path.join(SITE, pat))):
            if os.path.basename(p) in SKIP:
                continue
            slug, t, md, url = build(p, lang)
            rows.append((lang, slug, t, len(md), url, md))
            if write:
                d = os.path.join(OUT, "articles", sub)
                os.makedirs(d, exist_ok=True)
                open(os.path.join(d, slug + ".md"), "w", encoding="utf-8").write(md)
    return rows

if __name__ == "__main__":
    w = len(sys.argv) > 1 and sys.argv[1] == "write"
    rows = run(w)
    zh = [r for r in rows if r[0] == "zh"]
    en = [r for r in rows if r[0] == "en"]
    print("中文 %d 篇、英文 %d 篇，共 %d 篇" % (len(zh), len(en), len(rows)))
    print("總字元 %d（約 %.0f KB）" % (sum(r[3] for r in rows), sum(r[3] for r in rows) / 1024))
    print("最短 3 篇：")
    for r in sorted(rows, key=lambda r: r[3])[:3]:
        print("  %-3s %-32s %5d 字元  %s" % (r[0], r[1], r[3], r[2][:40]))
    bad = [r for r in rows if r[3] < 800 or not r[2]]
    print("可疑（過短或無標題）：", [(r[0], r[1]) for r in bad] or "無")
    if w:
        print("已寫入", os.path.join(OUT, "articles"))
