#!/usr/bin/env python3
"""Build an ad-free static wiki from dumped Fandom parse HTML."""

from __future__ import annotations

import hashlib
import html as htmlmod
import json
import os
import re
import shutil
import urllib.request
from pathlib import Path

from lxml import html as lhtml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DIST = ROOT / "dist"
SCRIPTS = ROOT / "scripts"
FANDOM = "https://lobotomycorp.fandom.com/zh/wiki/"

NAV = [
    ("导航", [("首页", "index.html")]),
    (
        "异想体",
        [
            ("异想体总览", "pages/异想体.html"),
            ("给新人的评级建议", "pages/给新人选择异想体的评级建议.html"),
            ("ZAYIN", "pages/ZAYIN.html"),
            ("TETH", "pages/TETH.html"),
            ("HE", "pages/HE.html"),
            ("WAW", "pages/WAW.html"),
            ("ALEPH", "pages/ALEPH.html"),
            ("工具异想体", "pages/异想体/工具异想体.html"),
        ],
    ),
    (
        "设施与人员",
        [
            ("部门", "pages/部门.html"),
            ("职员", "pages/职员.html"),
            ("游戏机制", "pages/游戏机制.html"),
            ("伤害机制", "pages/伤害机制/等级压制.html"),
        ],
    ),
    (
        "一日流程",
        [
            ("考验", "pages/考验.html"),
            ("黎明", "pages/黎明.html"),
            ("正午", "pages/正午.html"),
            ("黄昏", "pages/黄昏.html"),
            ("午夜", "pages/午夜.html"),
            ("逆卡巴拉能量熔毁", "pages/逆卡巴拉能量熔毁.html"),
        ],
    ),
    (
        "后期内容",
        [
            ("抑制核心", "pages/抑制核心.html"),
            ("构筑部挑战", "pages/构筑部.html"),
            ("挑战模式", "pages/挑战模式.html"),
            ("剧情", "pages/剧情.html"),
        ],
    ),
    (
        "E.G.O",
        [
            ("E.G.O 装备", "pages/E.G.O_装备.html"),
            ("E.G.O 武器", "pages/E.G.O_武器.html"),
            ("E.G.O 护甲", "pages/E.G.O_护甲.html"),
            ("E.G.O 饰品", "pages/E.G.O_饰品.html"),
        ],
    ),
]

RISK_CLASS = {
    "ZAYIN": "risk-zayin",
    "TETH": "risk-teth",
    "HE": "risk-he",
    "WAW": "risk-waw",
    "ALEPH": "risk-aleph",
}


def slugify(title: str) -> str:
    s = title.replace(" ", "_").replace(":", "_")
    parts = [p for p in s.split("/") if p and p not in (".", "..")]
    return "/".join(parts) or "index"


def relpath(from_file: Path, to_file: Path) -> str:
    return os.path.relpath(to_file, from_file.parent).replace("\\", "/")


def strip_tags(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmlmod.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def fix_lazy_images(fragment: lhtml.HtmlElement) -> None:
    for img in fragment.xpath(".//img"):
        src = img.get("data-src") or img.get("data-original")
        if not src:
            srcset = img.get("data-srcset") or ""
            if srcset:
                src = srcset.split(",")[0].strip().split(" ")[0]
        if src:
            img.set("src", src)
        img.set("referrerpolicy", "no-referrer")
        cls = img.get("class") or ""
        if "lazyload" in cls:
            img.set("class", cls.replace("lazyload", "").strip())
        for attr in ("data-src", "data-srcset", "data-original"):
            if attr in img.attrib:
                del img.attrib[attr]


def rewrite_links(fragment: lhtml.HtmlElement, current: Path, title_to_file: dict[str, Path]) -> None:
    for a in fragment.xpath(".//a[@href]"):
        href = a.get("href") or ""
        if href.startswith("//"):
            a.set("href", "https:" + href)
            continue
        if not href.startswith("/zh/wiki/") and not href.startswith("/wiki/"):
            continue
        raw = href.split("/wiki/", 1)[-1]
        raw = raw.split("?", 1)[0]
        frag = ""
        if "#" in raw:
            raw, frag = raw.split("#", 1)
            frag = "#" + frag
        title = htmlmod.unescape(urllib_unquote(raw)).replace("_", " ")
        # restore underscores that are part of codes by using original decoded path
        decoded = htmlmod.unescape(urllib_unquote(raw))
        lookup = decoded.replace("_", " ")
        dest = title_to_file.get(lookup) or title_to_file.get(decoded)
        if dest is None:
            a.set("href", FANDOM + decoded + frag)
            a.set("rel", "noopener noreferrer")
            continue
        a.set("href", relpath(current, dest) + frag)


def urllib_unquote(s: str) -> str:
    import urllib.parse

    return urllib.parse.unquote(s)


def inner_html(el: lhtml.HtmlElement) -> str:
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(lhtml.tostring(child, encoding="unicode", method="html"))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def clean_article_html(raw: str, current: Path, title_to_file: dict[str, Path]) -> str:
    raw = raw.replace('src="//', 'src="https://').replace("src='//", "src='https://")
    try:
        fragment = lhtml.fragment_fromstring(raw, create_parent="div")
    except Exception:
        return raw
    fix_lazy_images(fragment)
    rewrite_links(fragment, current, title_to_file)
    return inner_html(fragment)


def nav_html(current: Path) -> str:
    parts = []
    for group, items in NAV:
        parts.append(f"<h2>{group}</h2>")
        for label, target in items:
            dest = DIST / target
            href = relpath(current, dest)
            cls = RISK_CLASS.get(label, "")
            extra = f' class="{cls}"' if cls else ""
            parts.append(f'<a href="{href}"{extra}>{label}</a>')
    return "\n".join(parts)


def page_shell(title: str, body: str, current: Path, *, heading: str | None, notice: str | None = None) -> str:
    assets = DIST / "assets"
    css1 = relpath(current, assets / "wiki.css")
    css2 = relpath(current, assets / "site.css")
    js = relpath(current, assets / "app.js")
    home = relpath(current, DIST / "index.html")
    search = relpath(current, DIST / "search.html")
    h1 = f'<h1 class="page-title">{htmlmod.escape(heading)}</h1>' if heading else ""
    note = f'<div class="notice-strip">{notice}</div>' if notice else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#12110e">
  <meta name="referrer" content="no-referrer">
  <title>{htmlmod.escape(title)}</title>
  <link rel="icon" href="{relpath(current, DIST / 'assets' / 'favicon.svg')}" type="image/svg+xml">
  <link rel="stylesheet" href="{css1}">
  <link rel="stylesheet" href="{css2}">
</head>
<body>
  <a class="skip" href="#content">跳到正文</a>
  <header class="topbar">
    <button class="menu-btn" type="button" aria-label="打开菜单">☰</button>
    <a class="logo" href="{home}"><b>LOBOTOMY CORP</b><span>脑叶公司 Wiki</span></a>
    <form class="searchbox" action="{search}" method="get" role="search">
      <input type="search" name="q" placeholder="搜索异想体、部门、机制、剧情…" aria-label="搜索">
      <button type="submit">搜索</button>
    </form>
    <span class="badge">无广告镜像</span>
  </header>
  <div class="shell">
    <aside class="sidebar">{nav_html(current)}</aside>
    <main id="content" class="page-content article-content">{note}{h1}{body}</main>
  </div>
  <footer class="site-footer">本站为无广告静态镜像，方便查阅攻略，不含 Fandom 广告与追踪脚本。正文来自
    <a href="https://lobotomycorp.fandom.com/zh/" rel="noopener noreferrer">脑叶公司 Wiki</a>
    （CC BY-SA）。《脑叶公司》及相关名称、立绘与设定归 Project Moon 所有，本站与官方无隶属关系。</footer>
  <script src="{js}" defer></script>
</body>
</html>
"""


CSS_URL_RE = re.compile(r"url\(([^)]+)\)")
ASSET_UA = "Mozilla/5.0 (compatible; LobotomyWikiMirror/1.0; +https://github.com/ji415/lobotomy-wiki)"
MAX_REMOTE_BYTES = 800_000


def localize_css_urls(css: str) -> str:
    cache = DATA / "remote-cache"
    cache.mkdir(parents=True, exist_ok=True)
    dest_dir = DIST / "assets" / "remote"
    dest_dir.mkdir(parents=True, exist_ok=True)

    def fetch(url: str) -> str | None:
        path = url.split("?", 1)[0]
        ext = ".bin"
        if "." in path.rsplit("/", 1)[-1]:
            cand = "." + path.rsplit(".", 1)[-1].lower()
            if cand in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".woff", ".woff2"}:
                ext = cand
        name = hashlib.sha1(url.encode()).hexdigest()[:16] + ext
        cached = cache / name
        if not cached.exists():
            req = urllib.request.Request(url, headers={"User-Agent": ASSET_UA, "Accept": "*/*"})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
            except Exception as e:  # noqa: BLE001
                print("asset fail", url[:80], e)
                return None
            if len(data) > MAX_REMOTE_BYTES:
                print("asset skip large", len(data), url[:80])
                return None
            cached.write_bytes(data)
        shutil.copyfile(cached, dest_dir / name)
        return "remote/" + name

    def repl(match: re.Match[str]) -> str:
        raw = match.group(1).strip().strip("\"'")
        if not raw.startswith("http"):
            return match.group(0)
        local = fetch(raw)
        if not local:
            return match.group(0)
        return f'url("{local}")'

    return CSS_URL_RE.sub(repl, css)


def build_wiki_css() -> str:
    chunks = [
        """/* Theme variables used by imported wiki CSS */
:root {
  --theme-page-background-color: #1b1914;
  --theme-page-background-color--rgb: 27, 25, 20;
  --theme-page-background-color--secondary: #12110e;
  --theme-page-text-color: #e6e1d1;
  --theme-link-color: #e8c35a;
  --theme-link-color--rgb: 232, 195, 90;
  --theme-accent-color: #c9a227;
  --theme-accent-color--hover: #dbce7a;
  --theme-page-accent-mix-color: #5a5340;
  --custom-accent-border-color: #afcfe2;
  --custom-accent-highlight-color: var(--theme-accent-color--hover);
  --custom-notice-blue-background-color: var(--theme-accent-color);
  --custom-notice-blue-border-color: var(--custom-accent-border-color);
  --custom-notice-red-background-color: hsl(0, 80%, 10%);
  --custom-notice-red-border-color: hsl(0, 60%, 50%);
  --custom-notice-purple-background-color: hsl(228, 80%, 10%);
  --custom-notice-purple-border-color: hsl(243, 60%, 50%);
  --custom-notice-green-background-color: hsl(84, 80%, 10%);
  --custom-notice-green-border-color: hsl(84, 60%, 50%);
  --custom-notice-yellow-background-color: hsl(59, 80%, 10%);
  --custom-notice-yellow-border-color: hsl(59, 60%, 50%);
  --custom-notice-orange-background-color: hsl(28, 80%, 10%);
  --custom-notice-orange-border-color: hsl(28, 60%, 50%);
  --custom-notice-pink-background-color: hsl(324, 80%, 10%);
  --custom-color-red: #CB2742;
  --custom-color-white: #EFECC0;
  --custom-color-black: #A561AF;
  --custom-color-blue: #3FCCBD;
  --custom-color-zayin: #1DF900;
  --custom-color-teth: #13A2FF;
  --custom-color-he: #FFF900;
  --custom-color-waw: #7B2BF3;
  --custom-color-aleph: #FF0000;
  --custom-color-dfo: #DF00D0;
}
.page-content, .article-content, .page__main {
  background-color: transparent;
  color: var(--theme-page-text-color);
}
"""
    ]
    order = [
        "Common.css",
        "AbnormalityBox.css",
        "FlexibleWiki.css",
        "异想体_style.css",
        "MobileAbnormalityBox.css",
    ]
    for name in order:
        path = DATA / "css" / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"@import[^;]+;", "", text)
        chunks.append(f"\n/* ==== {name} ==== */\n{text}\n")
    return "\n".join(chunks)


def load_pages() -> list[dict]:
    pages = []
    for path in sorted((DATA / "pages").glob("*.json")):
        pages.append(json.loads(path.read_text(encoding="utf-8")))
    return pages


def main() -> None:
    pages = load_pages()
    if not pages:
        raise SystemExit("no dumped pages; run scripts/dump_wiki.py first")

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    (DIST / "pages").mkdir()
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    title_to_file: dict[str, Path] = {}
    records = []
    for p in pages:
        title = p["title"]
        slug = slugify(title)
        dest = DIST / "pages" / f"{slug}.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        title_to_file[title] = dest
        title_to_file[title.replace(" ", "_")] = dest
        records.append((p, dest, slug))

    home_src = None
    search_items = []
    for p, dest, slug in records:
        raw = p.get("html") or ""
        body = clean_article_html(raw, dest, title_to_file)
        heading = strip_tags(p.get("displaytitle") or p["title"])
        if p.get("redirect"):
            target = p["redirect"]
            tdest = title_to_file.get(target) or title_to_file.get(target.replace(" ", "_"))
            if tdest is not None:
                href = relpath(dest, tdest)
            else:
                href = FANDOM + target.replace(" ", "_")
            body = (
                f'<div class="redirect-box">重定向到：<a href="{href}">{htmlmod.escape(target)}</a></div>'
                f'<meta http-equiv="refresh" content="0;url={href}">'
                f"{body}"
            )
        html_out = page_shell(
            f"{heading} · 脑叶公司 Wiki",
            body,
            dest,
            heading=heading,
        )
        dest.write_text(html_out, encoding="utf-8")
        if p["title"] == "脑叶公司 Wiki":
            home_src = (p, body)
        if p.get("redirect"):
            continue
        text = strip_tags(raw)[:400]
        search_items.append(
            {
                "title": p["title"],
                "display": heading,
                "href": relpath(DIST / "search.html", dest),
                "categories": p.get("categories") or [],
                "text": text,
                "snippet": text[:160],
            }
        )

    # homepage
    home = DIST / "index.html"
    if home_src:
        home_page, _ = home_src
        home_body = clean_article_html(home_page.get("html") or "", home, title_to_file)
        home.write_text(
            page_shell(
                "脑叶公司 Wiki · 无广告镜像",
                home_body,
                home,
                heading=None,
                notice="这是无广告静态镜像，版式与条目尽量贴近原中文 Wiki，便于打游戏时查攻略。图片仍从原站图床加载。",
            ),
            encoding="utf-8",
        )
    else:
        home.write_text(
            page_shell("脑叶公司 Wiki", "<p>首页条目尚未导出。</p>", home, heading="脑叶公司 Wiki"),
            encoding="utf-8",
        )

    search = DIST / "search.html"
    search.write_text(
        page_shell(
            "搜索 · 脑叶公司 Wiki",
            '<p class="crumbs">搜索结果 · <span id="q-display"></span></p><div id="search-results" class="search-results" data-assets="./assets/"></div>',
            search,
            heading="搜索",
        ),
        encoding="utf-8",
    )

    (DIST / "404.html").write_text(
        page_shell(
            "未找到 · 脑叶公司 Wiki",
            '<p>没有这份档案。请从首页或搜索再找一次。</p><p><a href="index.html">返回首页</a></p>',
            DIST / "404.html",
            heading="档案缺失",
        ),
        encoding="utf-8",
    )

    (DIST / "assets" / "wiki.css").write_text(localize_css_urls(build_wiki_css()), encoding="utf-8")
    shutil.copyfile(SCRIPTS / "site.css", DIST / "assets" / "site.css")
    shutil.copyfile(SCRIPTS / "app.js", DIST / "assets" / "app.js")
    (DIST / "assets" / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" fill="#12110e"/>'
        '<text x="16" y="23" text-anchor="middle" font-size="18" font-family="serif" fill="#dbce7a">L</text>'
        "</svg>",
        encoding="utf-8",
    )
    (DIST / "assets" / "search.json").write_text(
        json.dumps(search_items, ensure_ascii=False), encoding="utf-8"
    )

    print(f"built {len(records)} pages, {len(search_items)} searchable, dist={DIST}")


if __name__ == "__main__":
    main()
