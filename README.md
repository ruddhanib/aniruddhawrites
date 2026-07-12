# Blog by Aniruddha

A modern, static website showcasing AI and analytics expertise with a focus on upcoming technologies and trends.

## Features

- Clean, modern design with dark theme
- Responsive layout for all devices
- Blog posts on AI, analytics, and tech trends
- Portfolio showcase
- Contact information and social links
- Integration with Facebook blog posts

## Local Development

To run the site locally:

```bash
cd /path/to/ghcp-gitpage
python3 -m http.server 8000
```

Then visit `http://localhost:8000` in your browser.

## GitHub Pages Deployment

1. Push this repository to GitHub
2. Go to repository Settings > Pages
3. Select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Save and wait for deployment

The site will be available at: `https://yourusername.github.io/aniruddha-blog/`

## Structure

- `index.html` - Homepage with hero section and featured content
- `blog.html` - Blog listing page
- `portfolio.html` - Portfolio showcase
- `about.html` - About page
- `contact.html` - Contact information
- `blog/` - Individual blog post pages
- `css/styles.css` - Main stylesheet
- `content/posts/` - Blog post content (for future expansion)
- `content/images/` - Images and assets

## Customization

- Edit `css/styles.css` to modify the theme
- Update HTML files to change content
- Add new blog posts in the `blog/` directory
- Modify navigation in the header of each page

## Technologies Used

- HTML5
- CSS3 (with CSS Grid and Flexbox)
- No JavaScript frameworks (pure static site)
## Imported Markdown Archive

The original blog markdown files from `myblog-on-gatsby` are available in `content/posts/`.
These files were converted into static HTML pages under `blog/` so your real authored content is preserved.
