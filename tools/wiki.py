#!/usr/bin/env python3
"""Personal finance knowledge base — persistent wiki that compounds across analyses.

Usage: python wiki.py init | status | lint
       python wiki.py create --category entities --slug aapl --content "..." --summary "Apple"
       python wiki.py read --category entities --slug aapl
       python wiki.py update --category entities --slug aapl --content "..."
       python wiki.py search --query "discount rate" [--category playbooks]
       python wiki.py list [--category entities]
"""

import argparse
import json
import os
import re
import shutil
import tempfile
from datetime import datetime
from datetime import timedelta

WIKI_DIR = os.path.join(os.path.expanduser("~"), ".alpha-stack", "wiki")
CATEGORIES = ("entities", "playbooks", "journal", "raw")
_SCHEMA_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "wiki", "schema-template.md")


def _safe_slug(n):
    return re.sub(r"[^a-z0-9._-]", "-", n.lower().strip()).strip("-")


def _atomic_write(path, content):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _idx():
    return os.path.join(WIKI_DIR, "index.md")


def _logp():
    return os.path.join(WIKI_DIR, "log.md")


def _page_path(cat, slug):
    if cat not in CATEGORIES:
        raise ValueError(f"Invalid category '{cat}'. Must be one of: {CATEGORIES}")
    return os.path.join(WIKI_DIR, cat, f"{_safe_slug(slug)}.md")


def _cats(cat):
    if cat is None:
        return list(CATEGORIES)
    if cat not in CATEGORIES:
        raise ValueError(f"Invalid category '{cat}'. Must be one of: {CATEGORIES}")
    return [cat]


def _read_index():
    try:
        with open(_idx()) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _add_index_entry(cat, slug, summary):
    index, hdr = _read_index(), f"## {cat.title()}"
    entry = f"- [{slug}]({cat}/{slug}.md) — {summary}"
    if hdr in index:
        lines = index.split("\n")
        for i, ln in enumerate(lines):
            if ln.strip() == hdr:
                j = i + 1
                while j < len(lines) and not lines[j].startswith("## "):
                    j += 1
                lines.insert(j, entry)
                break
        _atomic_write(_idx(), "\n".join(lines))
    else:
        _atomic_write(_idx(), index.rstrip() + f"\n\n{hdr}\n{entry}\n")


def _update_index_summary(cat, slug, summary):
    index = _read_index()
    p = re.compile(
        rf"^- \[{re.escape(slug)}\]\({re.escape(cat)}/{re.escape(slug)}\.md\) — .*$",
        re.MULTILINE,
    )
    new, n = p.subn(f"- [{slug}]({cat}/{slug}.md) — {summary}", index)
    if n:
        _atomic_write(_idx(), new)


def _chk():
    if not os.path.isdir(WIKI_DIR):
        raise FileNotFoundError("Wiki not initialized. Run: python3 tools/wiki.py init")


def wiki_init():
    """Initialize wiki directory structure. Idempotent."""
    created = []
    os.makedirs(WIKI_DIR, exist_ok=True)
    for c in CATEGORIES:
        d = os.path.join(WIKI_DIR, c)
        if not os.path.isdir(d):
            os.makedirs(d)
            created.append(f"{c}/")
    schema = os.path.join(WIKI_DIR, "schema.md")
    if not os.path.exists(schema):
        if os.path.exists(_SCHEMA_SRC):
            shutil.copy2(_SCHEMA_SRC, schema)
        else:
            _atomic_write(schema, "# Alpha Stack Wiki Schema\n")
        created.append("schema.md")
    if not os.path.exists(_idx()):
        h = "# Wiki Index\n\nMaster catalog of all wiki pages.\n"
        for c in CATEGORIES:
            if c != "raw":
                h += f"\n## {c.title()}\n"
        _atomic_write(_idx(), h)
        created.append("index.md")
    if not os.path.exists(_logp()):
        _atomic_write(_logp(), "# Wiki Log\n\n")
        created.append("log.md")
    wiki_append_log("init", "Wiki initialized")
    return {"status": "initialized", "path": WIKI_DIR, "created": created}


def wiki_status():
    """Return wiki health dashboard."""
    if not os.path.isdir(WIKI_DIR):
        return {"initialized": False, "path": WIKI_DIR}
    counts, sz = {}, 0
    for cat in CATEGORIES:
        d = os.path.join(WIKI_DIR, cat)
        if os.path.isdir(d):
            pgs = [f for f in os.listdir(d) if f.endswith(".md")]
            counts[cat] = len(pgs)
            for p in pgs:
                sz += os.path.getsize(os.path.join(d, p))
        else:
            counts[cat] = 0
    last = None
    if os.path.exists(_logp()):
        try:
            with open(_logp(), "rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - 4096))
                ls = [x.strip() for x in f.read().decode("utf-8", errors="replace").splitlines() if x.startswith("- ")]
            if ls:
                last = ls[-1]
        except OSError:
            pass
    return {
        "initialized": True,
        "path": WIKI_DIR,
        "pages": counts,
        "total_pages": sum(counts.values()),
        "total_size_kb": round(sz / 1024, 1),
        "last_activity": last,
    }


def wiki_create_page(category, slug, content, summary):
    """Create a new wiki page."""
    _chk()
    path, slug = _page_path(category, slug), _safe_slug(slug)
    if os.path.exists(path):
        return {"error": f"Page exists: {category}/{slug}.md. Use update."}
    _atomic_write(path, content)
    _add_index_entry(category, slug, summary)
    wiki_append_log("create", f"{category}/{slug}.md — {summary}")
    return {"status": "created", "category": category, "slug": slug, "path": path}


def wiki_read_page(category, slug):
    """Read a wiki page."""
    _chk()
    path, slug = _page_path(category, slug), _safe_slug(slug)
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        return {"error": f"Page not found: {category}/{slug}.md"}
    st = os.stat(path)
    return {
        "category": category,
        "slug": slug,
        "content": content,
        "size_bytes": st.st_size,
        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
    }


def wiki_update_page(category, slug, content, summary=None):
    """Update an existing wiki page."""
    _chk()
    path, slug = _page_path(category, slug), _safe_slug(slug)
    if not os.path.exists(path):
        return {"error": f"Page not found: {category}/{slug}.md. Use create."}
    _atomic_write(path, content)
    if summary:
        _update_index_summary(category, slug, summary)
    wiki_append_log("update", f"{category}/{slug}.md" + (f" — {summary}" if summary else ""))
    return {"status": "updated", "category": category, "slug": slug, "path": path}


def wiki_search(query, category=None):
    """Search wiki pages by content and filename."""
    _chk()
    q, matches = query.lower(), []
    for cat in _cats(category):
        d = os.path.join(WIKI_DIR, cat)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            slug, fp = fn[:-3], os.path.join(d, fn)
            nm = q in slug.lower()
            with open(fp) as f:
                lines = f.readlines()
            hits = [{"line": i, "text": ln.strip()[:120]} for i, ln in enumerate(lines, 1) if q in ln.lower()][:3]
            if nm or hits:
                matches.append({"category": cat, "slug": slug, "name_match": nm, "content_hits": hits})
    return {"query": query, "matches": matches, "count": len(matches)}


def wiki_list_pages(category=None):
    """List all wiki pages with metadata."""
    _chk()
    pages = []
    for cat in _cats(category):
        d = os.path.join(WIKI_DIR, cat)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            st = os.stat(os.path.join(d, fn))
            pages.append(
                {
                    "category": cat,
                    "slug": fn[:-3],
                    "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "size_bytes": st.st_size,
                }
            )
    return {"pages": pages, "count": len(pages)}


def wiki_lint():
    """Health-check wiki for orphan pages, dead links, stale and isolated pages."""
    _chk()
    indexed = {m.group(1) for m in re.finditer(r"- \[[^\]]+\]\(([^)]+)\)", _read_index())}
    on_disk, contents, stale = set(), {}, []
    cutoff = datetime.now() - timedelta(days=90)
    for cat in CATEGORIES:
        d = os.path.join(WIKI_DIR, cat)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith(".md"):
                continue
            rel, fp = f"{cat}/{fn}", os.path.join(d, fn)
            on_disk.add(rel)
            if datetime.fromtimestamp(os.stat(fp).st_mtime) < cutoff:
                stale.append(rel)
            with open(fp) as f:
                contents[rel] = f.read()
    isolated = []
    if on_disk:
        pat = re.compile("|".join(re.escape(r) for r in on_disk))
        for rel, txt in contents.items():
            if not any(r != rel for r in pat.findall(txt)):
                isolated.append(rel)
    issues = {
        "orphan_pages": sorted(on_disk - indexed),
        "dead_links": sorted(indexed - on_disk),
        "stale_pages": sorted(stale),
        "isolated_pages": sorted(isolated),
    }
    return {"issues": issues, "total_issues": sum(len(v) for v in issues.values()), "pages_scanned": len(on_disk)}


def wiki_append_log(action, details):
    """Append a timestamped entry to the wiki log."""
    if not os.path.exists(_logp()):
        return {"error": "Wiki not initialized"}
    entry = f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} | {action} | {details}\n"
    with open(_logp(), "a") as f:
        f.write(entry)
    return {"status": "logged", "entry": entry.strip()}


if __name__ == "__main__":
    _p = argparse.ArgumentParser(description="Alpha Stack Wiki")
    _s = _p.add_subparsers(dest="cmd")
    _s.add_parser("init")
    _s.add_parser("status")
    _s.add_parser("lint")
    for _nm, _args, _opt in [
        ("create", ["--category", "--slug", "--content", "--summary"], []),
        ("read", ["--category", "--slug"], []),
        ("update", ["--category", "--slug", "--content"], ["--summary"]),
        ("search", ["--query"], ["--category"]),
        ("list", [], ["--category"]),
    ]:
        _sp = _s.add_parser(_nm)
        for _a in _args:
            _sp.add_argument(_a, required=True)
        for _a in _opt:
            _sp.add_argument(_a, default=None)
    _a = _p.parse_args()
    _fns = {
        "init": lambda: wiki_init(),
        "status": lambda: wiki_status(),
        "lint": lambda: wiki_lint(),
        "create": lambda: wiki_create_page(_a.category, _a.slug, _a.content, _a.summary),
        "read": lambda: wiki_read_page(_a.category, _a.slug),
        "update": lambda: wiki_update_page(_a.category, _a.slug, _a.content, _a.summary),
        "search": lambda: wiki_search(_a.query, _a.category),
        "list": lambda: wiki_list_pages(_a.category),
    }
    if _a.cmd in _fns:
        print(json.dumps(_fns[_a.cmd](), indent=2, default=str))
    else:
        _p.print_help()
