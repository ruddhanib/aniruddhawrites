"""Generate SEO metadata and crawl-discovery files for the static site.

Update SITE_URL if the GitHub Pages site is moved to a custom domain, then run:
    python3 scripts/generate_seo.py
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://ruddhanib.github.io/aniruddha"
SITE_NAME = "Aniruddha Writes"
AUTHOR = "Aniruddha"
AUTHOR_URL = f"{SITE_URL}/about.html"
SOCIAL_URLS = [
    "https://www.linkedin.com/in/ruddhani/",
    "https://github.com/ruddhanib",
    "https://www.facebook.com/blogbyaniruddha",
]
DEFAULT_IMAGE = f"{SITE_URL}/content/images/when-data-becomes-bottleneck-unmasking-real-culprit-behind.png"

DESCRIPTIONS = {
    "index.html": "Technical essays on enterprise data platforms, AI engineering, analytics, Microsoft Fabric, Power BI and Azure.",
    "about.html": "About Aniruddha, an enterprise data platform, analytics and AI engineering practitioner.",
    "blog.html": "Articles and engineering notes on data platforms, AI, analytics architecture, PHP and cloud delivery.",
    "portfolio.html": "Enterprise architecture, analytics delivery and platform modernization experience from Aniruddha.",
    "contact.html": "Contact Aniruddha about enterprise architecture, data platforms, analytics and speaking engagements.",
    "blog/facebook-posts.html": "Selected AI, analytics and data-storytelling posts from blogbyaniruddha.",
}


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(value))).strip()


def match(pattern: str, source: str, default: str = "") -> str:
    found = re.search(pattern, source, re.I | re.S)
    return plain(found.group(1)) if found else default


def page_url(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return f"{SITE_URL}/" if relative == "index.html" else f"{SITE_URL}/{relative}"


def image_url(source: str) -> str:
    src = match(r'<img[^>]+src=["\']([^"\']+)["\']', source)
    if not src:
        return DEFAULT_IMAGE
    if src.startswith(("https://", "http://")):
        return src
    # compat: remove leading ../ if present (removeprefix not in Py3.8)
    src_clean = src[3:] if src.startswith("../") else src
    return f"{SITE_URL}/{src_clean.lstrip('/')}"


def published_date(source: str) -> Optional[str]:
    raw = match(r'<div class=["\']post-meta["\'][^>]*>.*?<span[^>]*>.*?</span>\s*<span[^>]*>(.*?)</span>', source)
    for date_format in ("%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, date_format).date().isoformat()
        except ValueError:
            pass
    return None


def json_script(data: dict) -> str:
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + encoded.replace("<", "\\u003c") + "</script>"


def structured_data(path: Path, source: str, title: str, description: str, canonical: str, article: bool) -> List[Dict[str, Any]]:
    if path.name == "index.html":
        return [{
            "@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME,
            "url": SITE_URL + "/", "publisher": {"@type": "Person", "name": AUTHOR, "url": AUTHOR_URL},
        }]
    if path.name == "about.html":
        return [{
            "@context": "https://schema.org", "@type": "Person", "name": AUTHOR,
            "url": AUTHOR_URL, "sameAs": SOCIAL_URLS,
            "jobTitle": "Data Platform and Analytics Architect",
        }]
    if not article:
        return [{
            "@context": "https://schema.org", "@type": "WebPage", "name": title,
            "description": description, "url": canonical,
        }]

    post = {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title,
        "description": description, "mainEntityOfPage": canonical, "image": image_url(source),
        "author": {"@type": "Person", "name": AUTHOR, "url": AUTHOR_URL},
        "publisher": {"@type": "Person", "name": AUTHOR, "url": AUTHOR_URL},
    }
    date = published_date(source)
    if date:
        post["datePublished"] = date
        post["dateModified"] = date
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Articles", "item": SITE_URL + "/blog.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
        ],
    }
    return [post, breadcrumb]


def metadata(path: Path, source: str) -> str:
    relative = path.relative_to(ROOT).as_posix()
    title = match(r"<h1[^>]*>(.*?)</h1>", source, match(r"<title[^>]*>(.*?)</title>", source, SITE_NAME))
    description = DESCRIPTIONS.get(relative, match(r'<p class=["\']intro-copy["\']>(.*?)</p>', source, f"{title} — {SITE_NAME}."))
    description = description[:155].rstrip(" .") + "."
    canonical = page_url(path)
    article = path.parent.name == "blog" and path.name != "facebook-posts.html"
    image = image_url(source)
    output = [
        "<!-- SEO:START -->",
        f'<meta name="description" content="{html.escape(description, quote=True)}">',
        f'<link rel="canonical" href="{canonical}">',
        '<meta name="robots" content="index, follow">',
        f'<meta property="og:type" content="{"article" if article else "website"}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'<meta property="og:description" content="{html.escape(description, quote=True)}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:image" content="{image}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'<meta name="twitter:description" content="{html.escape(description, quote=True)}">',
        f'<meta name="twitter:image" content="{image}">',
    ]
    output.extend(json_script(item) for item in structured_data(path, source, title, description, canonical, article))
    output.append("<!-- SEO:END -->")
    return "\n  ".join(output)


def update_page(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = re.sub(r"\s*<!-- SEO:START -->.*?<!-- SEO:END -->", "", source, flags=re.S)
    path.write_text(source.replace("</head>", "  " + metadata(path, source) + "\n</head>", 1), encoding="utf-8")


def write_discovery(pages: List[Path]) -> None:
    sitemap_entries = []
    for page in pages:
        sitemap_entries.append(f"  <url><loc>{page_url(page)}</loc></url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_entries) + "\n</urlset>\n", encoding="utf-8"
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )


def main() -> None:
    pages = sorted([*ROOT.glob("*.html"), *ROOT.joinpath("blog").glob("*.html")])
    for page in pages:
        update_page(page)
    write_discovery(pages)
    print(f"Updated SEO metadata on {len(pages)} pages.")


if __name__ == "__main__":
    main()
