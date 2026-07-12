import os
import re
from datetime import datetime

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
POST_DIR = os.path.join(SITE, 'content', 'posts')
IMG_DIR = os.path.join(SITE, 'content', 'images')
OUTPUT_DIR = os.path.join(SITE, 'blog')

os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}, text
    meta = {}
    i = 1
    key = None
    while i < len(lines):
        line = lines[i]
        if line.strip() == '---':
            break
        if key and (line.startswith(' ') or line.startswith('\t')):
            meta[key] += ' ' + line.strip()
        else:
            if ': ' in line:
                parts = line.split(': ', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                if value in ('>-', '|-'):
                    meta[key] = ''
                else:
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    meta[key] = value
            elif line.strip().endswith(':'):
                key = line.strip()[:-1]
                meta[key] = ''
            else:
                key = None
        i += 1
    content = '\n'.join(lines[i+1:])
    return meta, content


def inline_replace(text):
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    return text


def markdown_to_html(md):
    html = []
    lines = md.splitlines()
    in_code = False
    in_list = False
    paragraph = []

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            html.append('<p>' + ' '.join(paragraph).strip() + '</p>')
            paragraph = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            if in_code:
                html.append('</code></pre>')
                in_code = False
            else:
                flush_paragraph()
                html.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            html.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue
        if not stripped:
            if in_list:
                html.append('</ul>')
                in_list = False
            flush_paragraph()
            continue
        if stripped.startswith('### '):
            flush_paragraph()
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append('<h3>' + inline_replace(stripped[4:]) + '</h3>')
            continue
        if stripped.startswith('## '):
            flush_paragraph()
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append('<h2>' + inline_replace(stripped[3:]) + '</h2>')
            continue
        if stripped.startswith('# '):
            flush_paragraph()
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append('<h1>' + inline_replace(stripped[2:]) + '</h1>')
            continue
        list_match = re.match(r'^[\*-]\s+(.*)', stripped)
        if list_match:
            if not in_list:
                flush_paragraph()
                html.append('<ul>')
                in_list = True
            html.append('<li>' + inline_replace(list_match.group(1)) + '</li>')
            continue
        paragraph.append(inline_replace(stripped))
    if in_list:
        html.append('</ul>')
    flush_paragraph()
    return '\n'.join(html)


def safe_slug(path):
    return path.strip().replace(' ', '-').replace('/', '-').lower()


def parse_date(value):
    if not value:
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S.%f'):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


posts = []
for filename in sorted(os.listdir(POST_DIR)):
    if not filename.endswith('.md'):
        continue
    file_path = os.path.join(POST_DIR, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    meta, body_md = parse_front_matter(raw)
    slug = meta.get('path') or os.path.splitext(filename)[0]
    slug = safe_slug(slug)
    title = meta.get('title') or slug.replace('-', ' ').title()
    intro = meta.get('intro_paragraph', '')
    date = parse_date(meta.get('date', ''))
    intro_img = meta.get('introImage', '')
    tags = [t.strip() for t in re.split(r'[# ,]+', meta.get('tags', '')) if t.strip()]
    category = tags[0] if tags else 'Blog'
    output_file = os.path.join(OUTPUT_DIR, f'{slug}.html')
    image_html = ''
    if intro_img:
        img_name = os.path.basename(intro_img)
        image_html = f'<div class="post-hero"><img src="../content/images/{img_name}" alt="{title}"></div>'
    body_html = markdown_to_html(body_md)
    date_display = date.strftime('%B %d, %Y') if date else 'Published'
    author_html = f'<p class="post-author">By {meta.get("author")}</p>' if meta.get('author') else ''
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - Aniruddha's AI & Analytics Blog</title>
  <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="../index.html" class="brand">Blog by Aniruddha</a>
      <nav class="site-nav">
        <a href="../index.html">Home</a>
        <a href="../blog.html">Blog</a>
        <a href="../portfolio.html">Portfolio</a>
        <a href="../about.html">About</a>
        <a href="../contact.html">Contact</a>
      </nav>
    </div>
  </header>
  <main class="site-main">
    <article class="blog-post-page">
      <div class="blog-post-header">
        <div class="post-meta">
          <span>{category}</span>
          <span>{date_display}</span>
          <span>{len(body_md.split())} words</span>
        </div>
        <h1>{title}</h1>
        <p class="intro-copy">{intro}</p>
        {author_html}
      </div>
      {image_html}
      <div class="blog-post-body">
        {body_html}
      </div>
      <div class="post-actions">
        <a href="../blog.html" class="button button-secondary">← Back to Blog</a>
        <a href="../contact.html" class="button button-primary">Discuss This Topic</a>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <p>&copy; 2024 Aniruddha's AI & Analytics Blog. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>'''
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    posts.append({
        'title': title,
        'slug': slug,
        'intro': intro,
        'date': date,
        'date_display': date_display,
        'category': category,
        'tags': tags,
    })

posts = sorted(posts, key=lambda item: item['date'] or datetime.min, reverse=True)

category_link_html = '\n'.join(f'            <li><a href="#">{cat}</a></li>' for cat in sorted({tag for post in posts for tag in post['tags']}))
post_cards = '\n'.join(
    f'''        <div class="post-card">
          <div class="post-card-top">
            <span>{post['category']}</span>
            <span>{post['date_display']}</span>
          </div>
          <h3>{post['title']}</h3>
          <p>{post['intro']}</p>
          <a href="blog/{post['slug']}.html" class="post-link">Read More →</a>
        </div>'''
    for post in posts
)
blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog - Aniruddha's AI & Analytics Blog</title>
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="index.html" class="brand">Blog by Aniruddha</a>
      <nav class="site-nav">
        <a href="index.html">Home</a>
        <a href="blog.html">Blog</a>
        <a href="portfolio.html">Portfolio</a>
        <a href="about.html">About</a>
        <a href="contact.html">Contact</a>
      </nav>
    </div>
  </header>
  <main class="site-main">
    <section class="page-section">
      <div class="section-heading">
        <div class="eyebrow">AI & Analytics Archive</div>
        <h2>Blog Posts</h2>
      </div>
      <div class="blog-grid">
        <div class="sidebar-card">
          <h3>Categories</h3>
          <ul>
{category_link_html}
          </ul>
        </div>
{post_cards}
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <p>&copy; 2024 Aniruddha's AI & Analytics Blog. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>'''
with open(os.path.join(SITE, 'blog.html'), 'w', encoding='utf-8') as f:
    f.write(blog_html)

latest_posts = posts[:4]
index_post_cards = '\n'.join(
    f'''        <div class="post-card">
          <div class="post-card-top">
            <span>{post['category']}</span>
            <span>{post['date_display']}</span>
          </div>
          <h3>{post['title']}</h3>
          <p>{post['intro']}</p>
          <a href="blog/{post['slug']}.html" class="post-link">Read More →</a>
        </div>'''
    for post in latest_posts
)
index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aniruddha's AI & Analytics Blog</title>
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="index.html" class="brand">Blog by Aniruddha</a>
      <nav class="site-nav">
        <a href="index.html">Home</a>
        <a href="blog.html">Blog</a>
        <a href="portfolio.html">Portfolio</a>
        <a href="about.html">About</a>
        <a href="contact.html">Contact</a>
      </nav>
    </div>
  </header>
  <main class="site-main">
    <section class="hero-section">
      <div class="hero-copy">
        <div class="eyebrow">AI & Analytics Expert</div>
        <h1>Explore the Future of Technology</h1>
        <p>Read original articles, engineering guides, and analytics insights from Aniruddha’s static blog archive.</p>
        <div class="hero-actions">
          <a href="blog.html" class="button button-primary">Browse Posts</a>
          <a href="portfolio.html" class="button button-secondary">View Portfolio</a>
        </div>
      </div>
      <div class="hero-panel">
        <div class="panel-card card-highlight">
          <span>Imported Content</span>
          <h2>Markdown Blog Archive</h2>
          <p>Real posts converted from your Gatsby markdown site, now readable in plain HTML.</p>
        </div>
        <div class="panel-card">
          <h3>Facebook Highlights</h3>
          <p>Curated summaries of the top Facebook blog posts from blogbyaniruddha.</p>
        </div>
        <div class="panel-card">
          <h3>Static UX</h3>
          <p>Fast GitHub Pages compatible HTML pages with modern AI styling.</p>
        </div>
      </div>
    </section>

    <section class="page-section">
      <div class="section-heading">
        <div class="eyebrow">Recent Imports</div>
        <h2>Latest Posts</h2>
      </div>
      <div class="post-grid">
{index_post_cards}
      </div>
    </section>

    <section class="page-section">
      <div class="section-heading">
        <div class="eyebrow">Featured Areas</div>
        <h2>What I Write About</h2>
      </div>
      <div class="feature-grid">
        <div class="feature-card">
          <h3>AI & Data Trends</h3>
          <p>Research-backed articles on AI, machine learning, and analytics strategy.</p>
        </div>
        <div class="feature-card">
          <h3>Engineering Practices</h3>
          <p>Guides for modern PHP, Composer, architecture, and code quality.</p>
        </div>
        <div class="feature-card">
          <h3>Facebook Insights</h3>
          <p>Summaries of ideas and conversations from the blogbyaniruddha Facebook page.</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="footer-inner">
      <p>&copy; 2024 Aniruddha's AI & Analytics Blog. All rights reserved.</p>
    </div>
  </footer>
</body>
</html>'''
with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

print(f'Converted {len(posts)} markdown posts to HTML pages.')
