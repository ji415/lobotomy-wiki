#!/usr/bin/env python3
"""Dump rendered article HTML from the Chinese Lobotomy Corp Fandom wiki."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API = "https://lobotomycorp.fandom.com/zh/api.php"
UA = "LobotomyWikiMirror/1.0 (https://github.com/ji415/lobotomy-wiki; personal ad-free mirror)"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PAGES_DIR = DATA / "pages"
CSS_DIR = DATA / "css"
WORKERS = 6

CSS_PAGES = [
    "MediaWiki:Common.css",
    "MediaWiki:AbnormalityBox.css",
    "MediaWiki:FlexibleWiki.css",
    "MediaWiki:异想体/style.css",
    "MediaWiki:MobileAbnormalityBox.css",
]


def api(params: dict, tries: int = 6) -> dict:
    params = {**params, "format": "json", "formatversion": "2"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    delay = 1.0
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if i < tries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            raise
    raise RuntimeError("unreachable")


def all_pages() -> list[dict]:
    pages: list[dict] = []
    cont = None
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apnamespace": 0,
            "aplimit": "500",
        }
        if cont:
            params["apcontinue"] = cont
        data = api(params)
        pages.extend(data["query"]["allpages"])
        cont = (data.get("continue") or {}).get("apcontinue")
        if not cont:
            break
    return pages


def parse_page(title: str) -> dict:
    data = api(
        {
            "action": "parse",
            "page": title,
            "prop": "text|displaytitle|categories|images|links|properties",
            "disablelimitreport": "1",
            "disableeditsection": "1",
        }
    )
    p = data.get("parse")
    if not p:
        raise RuntimeError(f"parse failed for {title}: {data}")
    html = (p.get("text") or "") if isinstance(p.get("text"), str) else (p.get("text") or {}).get("*", "")
    cats = []
    for c in p.get("categories") or []:
        if isinstance(c, str):
            cats.append(c)
        else:
            cats.append(c.get("category") or c.get("*") or "")
    links = []
    for ln in p.get("links") or []:
        if isinstance(ln, str):
            links.append(ln)
        else:
            links.append(ln.get("title") or "")
    redirect = None
    if "redirectMsg" in html or "redirectText" in html:
        m = re.search(r'class="redirectText".*?title="([^"]+)"', html, re.S)
        if m:
            redirect = html_unescape(m.group(1))
        else:
            m = re.search(r'class="redirectText".*?>([^<]+)<', html, re.S)
            if m:
                redirect = html_unescape(m.group(1).strip())
    return {
        "pageid": p.get("pageid"),
        "title": p.get("title") or title,
        "displaytitle": p.get("displaytitle") or title,
        "html": html,
        "categories": [c for c in cats if c],
        "images": p.get("images") or [],
        "links": [x for x in links if x],
        "redirect": redirect,
    }


def html_unescape(s: str) -> str:
    import html as htmlmod

    return htmlmod.unescape(s)


def dump_css() -> None:
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    for page in CSS_PAGES:
        data = api({"action": "parse", "page": page, "prop": "wikitext"})
        p = data.get("parse") or {}
        text = p.get("wikitext") or ""
        if isinstance(text, dict):
            text = text.get("*", "")
        name = page.split(":", 1)[-1].replace("/", "_")
        (CSS_DIR / name).write_text(text, encoding="utf-8")
        print(f"css {name} {len(text)}")


def page_path(pageid: int) -> Path:
    return PAGES_DIR / f"{pageid}.json"


def main() -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    print("listing pages…")
    pages = all_pages()
    print(f"found {len(pages)} ns0 pages")
    (DATA / "allpages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
    dump_css()

    todo = []
    for p in pages:
        dest = page_path(p["pageid"])
        if dest.exists() and dest.stat().st_size > 20:
            continue
        todo.append(p)
    print(f"to dump: {len(todo)} (skip {len(pages) - len(todo)})")

    ok = 0
    fail: list[str] = []

    def work(item: dict) -> tuple[bool, str]:
        title = item["title"]
        try:
            parsed = parse_page(title)
            parsed["pageid"] = parsed.get("pageid") or item["pageid"]
            page_path(item["pageid"]).write_text(
                json.dumps(parsed, ensure_ascii=False), encoding="utf-8"
            )
            return True, title
        except Exception as e:  # noqa: BLE001
            return False, f"{title}: {e}"

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(work, item) for item in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            success, msg = fut.result()
            if success:
                ok += 1
            else:
                fail.append(msg)
                print("FAIL", msg)
            if i % 25 == 0 or i == len(futs):
                print(f"progress {i}/{len(futs)} ok={ok} fail={len(fail)}")

    print(f"done ok={ok} fail={len(fail)}")
    if fail:
        (DATA / "fail.txt").write_text("\n".join(fail), encoding="utf-8")


if __name__ == "__main__":
    main()
