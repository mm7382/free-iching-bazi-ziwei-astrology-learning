# -*- coding: utf-8 -*-
"""重建三份索引 README。四支轉換器只產文章檔，不產索引，少跑這支會留下舊索引。"""
import glob, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def info(p):
    """取檔尾那行來源網址。正文裡也可能出現 "Source: [Wikisource...]"（六十四卦英文頁就有），
    所以必須取最後一筆、而且限定是本站網址，否則索引會連到錯的地方。"""
    s = open(p, encoding="utf-8").read()
    urls = re.findall(r"^(?:原文|Source): (https://mm7382\.github\.io/\S*)$", s, re.M)
    if not urls:
        raise SystemExit("找不到檔尾來源網址：%s" % p)
    return (os.path.basename(p)[:-3],
            re.search(r"^# (.+)$", s, re.M).group(1),
            urls[-1])

def listing(folder, sub):
    en = [info(p) for p in sorted(glob.glob(os.path.join(REPO, folder, sub, "en", "*.md")))]
    zh = [info(p) for p in sorted(glob.glob(os.path.join(REPO, folder, sub, "zh", "*.md")))]
    return en, zh

def section(prefix, en, zh, head_en="### English", head_zh="### 繁體中文"):
    L = []
    if en:
        L.append(head_en + "\n")
        L += ["- [%s](%s/en/%s.md) — [source](%s)" % (t, prefix, s, u) for s, t, u in en]
        L.append("")
    if zh:
        L.append(head_zh + "\n")
        L += ["- [%s](%s/zh/%s.md) — [原文](%s)" % (t, prefix, s, u) for s, t, u in zh]
    return L

def articles():
    en, zh = listing("articles", "")
    L = ["# Beginner articles (full text mirror)\n",
         "Full text of the %d beginner articles from <https://mm7382.github.io/learn/>, in Traditional Chinese and English.\n" % len(en),
         "These are **mirrors**. The canonical, most up-to-date version of every article is on the site itself; each file links back to its source. Text licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse, translate and adapt it freely with attribution to Wei Chun Chuang.\n",
         "Topics: the I Ching (易經), Bazi / Four Pillars (八字), Zi Wei Dou Shu (紫微斗數) and Western astrology. Free to read, no account, no advertising.\n",
         "\n## English\n"]
    L += ["- [%s](en/%s.md) — [source](%s)" % (t, s, u) for s, t, u in en]
    L.append("\n## 繁體中文\n")
    L += ["- [%s](zh/%s.md) — [原文](%s)" % (t, s, u) for s, t, u in zh]
    L.append("")
    return "articles/README.md", "\n".join(L), len(en) + len(zh)

def courses():
    BLOCKS = [("bazi", "Bazi / Four Pillars (八字)", "20 lessons"),
              ("ziwei", "Zi Wei Dou Shu (紫微斗數)", "36 lessons"),
              ("astrology", "Western astrology (西洋占星)", "36 lessons"),
              ("yijian-lessons", "I Ching introductory lessons (易經八堂課)", "8 lessons"),
              ("hexagrams", "All 64 hexagrams (六十四卦)", "64 hexagrams, each with the classical text and a plain-language reading")]
    L = ["# Course lessons and all 64 hexagrams (full text mirror)\n",
         "Full text of the free web lessons and hexagram pages from <https://mm7382.github.io/>, in Traditional Chinese and English.\n",
         "These are **mirrors**. The canonical, most up-to-date version of every page is on the site itself; each file links back to its source. Free to read, no account, no advertising.\n",
         "The commentary and lesson text is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse, translate and adapt it freely with attribution to Wei Chun Chuang. The classical text of the Zhou Yi quoted on the hexagram pages is in the public domain.\n"]
    n = 0
    for app, label, note in BLOCKS:
        en, zh = listing("courses", app)
        n += len(en) + len(zh)
        L.append("\n## %s — %s\n" % (label, note))
        L += section(app, en, zh)
    L.append("")
    return "courses/README.md", "\n".join(L), n

def pages():
    BLOCKS = [("site", "Site overview"), ("tools", "Free web tools"),
              ("apps", "Apps"), ("work", "Portfolio / work")]
    L = ["# Site, tools, apps and portfolio pages (mirror)\n",
         "Mirrors of the remaining pages of <https://mm7382.github.io/>: the portfolio, the free browser tools and the app pages.\n",
         "The canonical, most up-to-date version of every page is on the site itself; each file links back to its source. Page text is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); app names, icons, source code and interface design are not covered.\n",
         "\n**Not mirrored**, deliberately: the two site-index pages (pure link lists — this repository's own README and indexes already serve that purpose), the page templates, the personal records tool and the 'coming soon' placeholder. None of them carry article text.\n"]
    n = 0
    for folder, label in BLOCKS:
        en, zh = listing("pages", folder)
        if not en and not zh:
            continue
        n += len(en) + len(zh)
        L.append("\n## %s\n" % label)
        L += section(folder, en, zh)
    L.append("")
    return "pages/README.md", "\n".join(L), n

if __name__ == "__main__":
    for fn in (articles, courses, pages):
        rel, text, n = fn()
        open(os.path.join(REPO, rel), "w", encoding="utf-8").write(text)
        print("  %-22s %3d 條" % (rel, n))
    # 壞連結檢查
    bad = []
    for rel in ("articles/README.md", "courses/README.md", "pages/README.md"):
        base = os.path.join(REPO, os.path.dirname(rel))
        for u in re.findall(r"\]\((?!https?:|#)([^)]+)\)", open(os.path.join(REPO, rel), encoding="utf-8").read()):
            if not os.path.exists(os.path.join(base, u)):
                bad.append((rel, u))
    print("  壞連結：", bad or "無")
