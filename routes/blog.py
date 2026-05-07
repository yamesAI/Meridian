import os
import glob
from flask import Blueprint, render_template, abort
import frontmatter
import markdown

blog_bp = Blueprint("blog", __name__)

BLOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content", "blog")


def _load_posts():
    posts = []
    for path in glob.glob(os.path.join(BLOG_DIR, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        posts.append(
            {
                "slug": post.get("slug", os.path.splitext(os.path.basename(path))[0]),
                "title": post.get("title", "Untitled"),
                "date": post.get("date", ""),
                "meta_description": post.get("meta_description", ""),
                "saturn_return_tag": post.get("saturn_return_tag", False),
                "zodiac_tags": post.get("zodiac_tags", []),
                "lp_tags": post.get("lp_tags", []),
                "excerpt": post.content[:200].strip() + "…",
            }
        )
    return sorted(posts, key=lambda p: str(p["date"]), reverse=True)


@blog_bp.route("/blog")
def blog_index():
    posts = _load_posts()
    return render_template("blog_index.html", posts=posts)


@blog_bp.route("/blog/<slug>")
def blog_post(slug):
    path = os.path.join(BLOG_DIR, f"{slug}.md")
    if not os.path.exists(path):
        abort(404)

    with open(path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    html_content = markdown.markdown(
        post.content,
        extensions=["extra", "smarty", "toc"],
    )

    return render_template(
        "blog_post.html",
        title=post.get("title", ""),
        meta_description=post.get("meta_description", ""),
        date=post.get("date", ""),
        html_content=html_content,
        saturn_return_tag=post.get("saturn_return_tag", False),
        zodiac_tags=post.get("zodiac_tags", []),
        slug=slug,
    )
