# Mirror build scripts

These scripts regenerate the Markdown mirror from the website source. The website is canonical; this repository is a mirror and does **not** update itself.

## Usage

```bash
bash tools/sync.sh        # regenerate only, then review `git status`
bash tools/sync.sh push   # regenerate, commit and push if anything changed
```

`sync.sh` reads the site from `/Users/michaelchuang/Documents/遊戲/mm7382.github.io` and never writes to it.

## What each script does

| Script | Covers | Output |
|---|---|---|
| `to_md.py` | `/learn/` beginner articles, zh + en | `articles/` |
| `courses.py` | Bazi, Zi Wei Dou Shu and astrology lessons | `courses/bazi`, `courses/ziwei`, `courses/astrology` |
| `yijian.py` | all 64 hexagrams and the 8 I Ching lessons | `courses/hexagrams`, `courses/yijian-lessons` |
| `pages.py` | portfolio, tool and app pages | `pages/` |
| `build_indexes.py` | rebuilds the three index READMEs | `*/README.md` |

`build_indexes.py` must run after the converters. The converters only write article files, so skipping it leaves stale indexes.

## Things that bite

- **Three different page layouts.** `/learn/` and the course lessons use `<article>`; the hexagram and I Ching lesson pages put their content in `div.frame`; the portfolio and tool pages use `<article>` for repeated cards, so those read `<main>` instead.
- **The Chinese article pages carry the full English text** inside a CSS-hidden `<section id="en">`. `to_md.py` strips it for the Chinese mirror — which also removes the closing `</article>`, so its body extractor tolerates a missing end tag.
- **App download cards** (`aside.app-cta`) are stripped: their heading and button sit outside any block tag, so only a fragment would survive.
- **Nested tags need a separator.** Closing block tags and tags inside link text become a space, otherwise `六爻順序Yin, yang…` runs together.
- **`Source:` appears in body text too.** The English hexagram pages cite Wikisource that way, so `build_indexes.py` takes the *last* `Source:` line and requires it to be an `mm7382.github.io` URL.
