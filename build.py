"""Render Frameby as static HTML from the shared catalog."""
import hashlib
import json
from html import escape
from pathlib import Path
import re
from shutil import copy2
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
SOURCE = ROOT / "src"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def text(value):
    return escape(str(value), quote=True)


def render(template, values):
    return re.sub(r"{{(\w+)}}", lambda match: values[match[1]], template)


def write(route, content):
    target = DIST / route / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def page(title, body):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{text(title)} | Framedby</title><link rel="stylesheet" href="../assets/site.css"></head>
<body class="reader"><main><a href="../">Home</a><h1>{text(title)}</h1>{body}</main></body></html>"""


def https(value):
    url = urlsplit(value)
    if url.scheme != "https" or not url.hostname or url.username or url.password:
        raise ValueError("Expected an HTTPS link")
    return text(value)



def card(lab, number):
    status = text(lab["status"])
    topics = text("|".join(lab["topics"]))
    title = text(lab["title"])
    summary = text(lab["summary"])
    tags = "".join(f"<span>{text(topic)}</span>" for topic in lab["topics"])
    available = bool(lab.get("bundle"))
    when = f'Approx. {int(lab["minutes"])} min' if lab.get("minutes") else "Research roadmap"
    footer = (f'<a class="framedby-lab-cta" href="labs/{text(lab["slug"])}/">Inspect Lab &rarr;</a>'
              if available else '<span class="framedby-lab-planned">In planning</span>')
    return f"""<article data-topics="{topics}" class="framedby-lab-card">
<div class="framedby-lab-top"><span class="framedby-lab-number">LAB #{number:02d}</span>
<span class="framedby-lab-status" data-status="{status}">{status}</span></div>
<h3 class="framedby-lab-title">{title}</h3>
<p class="framedby-lab-summary">{summary}</p>
<div class="framedby-lab-tags">{tags}</div>
<div class="framedby-lab-bottom"><span class="framedby-lab-runtime">{text(when)}</span>{footer}</div>
</article>"""


def build():
    site = read_json(CONTENT / "site.json")
    labs = read_json(CONTENT / "labs.json")
    slugs = set()
    for lab in labs:
        slug = lab["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
            raise ValueError(f"Invalid or duplicate slug: {slug}")
        slugs.add(slug)
        if lab["status"] not in {"Planned", "Experimental", "Verified"}:
            raise ValueError(f"Invalid status: {lab['status']}")
    repo = site["repository"]
    if repo and not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("Repository must use owner/name")
    repository_link = f"https://github.com/{repo}" if repo else "contribute/"
    featured = next(lab for lab in labs if lab.get("bundle"))
    topics = ["all", *sorted({topic for lab in labs for topic in lab["topics"]})]
    filters = "".join(
        f'<button type="button" data-filter="{text(topic)}" aria-pressed="{str(topic == "all").lower()}" '
        f'class="rounded border border-zinc-700 px-3 py-1 text-sm">{text(topic.title() if topic == "all" else topic)}</button>'
        for topic in topics
    )
    write("", render((SOURCE / "home.html").read_text(encoding="utf-8"), {
        "featured_title": text(featured["title"]), "featured_command": text(featured["command"]),
        "featured_url": f'labs/{text(featured["slug"])}/', "repository_link": text(repository_link),
        "filters": filters, "cards": "".join(card(lab, i) for i, lab in enumerate(labs, 1)),
    }))
    for lab in labs:
        if not lab.get("bundle"):
            continue
        slug = lab["slug"]
        bundle = CONTENT / "downloads" / lab["bundle"]
        expected = bundle.with_suffix(".zip.sha256").read_text(encoding="ascii").split()[0]
        if hashlib.sha256(bundle.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Checksum mismatch: {bundle.name}")
        if slug == "indirect-injection":
            evidence = read_json(CONTENT / "downloads" / f"{slug}-evidence.json")
            if (evidence.get("lab_id") != "flf-002" or evidence.get("lab_version") != lab["version"]
                    or evidence.get("all_passed") is not True
                    or not all(evidence.get("assertions", {}).values())):
                raise ValueError("Indirect injection evidence does not match its experimental release")
            issue_body = f"Lab: {slug}\nVersion: {lab['version']}\nPlatform:\nCommand:\nExpected:\nObserved:\n"
            issue = "../../contribute/" if not repo else f"https://github.com/{repo}/issues/new?" + urlencode({
                "title": f"Reproduction: {slug} {lab['version']}", "body": issue_body,
            })
            excerpt = {"type": evidence["type"], "all_passed": evidence["all_passed"],
                       "assertions": evidence["assertions"]}
            write(f"labs/{slug}", render((SOURCE / "injection-detail.html").read_text(encoding="utf-8"), {
                **{key: text(value) for key, value in lab.items()},
                "issue": text(issue), "evidence": text(json.dumps(excerpt, indent=2)),
            }))
            continue
        evidence = read_json(CONTENT / "downloads" / f"{slug}-evidence.json")
        if any(row["lab_version"] != lab["version"] or row["status"] != "passed" for row in evidence):
            raise ValueError("Evidence must match the verified lab version")
        excerpt = next(row for row in evidence if row["scenario_id"] == "unauthorized-write")
        issue_body = f"Lab: {slug}\nVersion: {lab['version']}\nPlatform:\nCommand:\nExpected result:\nObserved result:\n"
        issue = "../../contribute/" if not repo else f"https://github.com/{repo}/issues/new?" + urlencode({
            "title": f"Reproduction: {slug} {lab['version']}", "body": issue_body,
        })
        run = lab.get("verificationRun")
        verification = f'<a href="{https(run)}">Passing CI run</a>' if run else "Local run recorded. Hosted CI evidence pending."
        write(f"labs/{slug}", render((SOURCE / "detail.html").read_text(encoding="utf-8"), {
            **{key: text(value) for key, value in lab.items()},
            "cases": "".join(f"<details><summary>{text(q)}</summary><p>{text(a)}</p></details>" for q, a in lab["cases"]),
            "issue": text(issue), "verification": verification,
            "evidence": text(json.dumps({key: excerpt[key] for key in ("scenario_id", "status", "observations")}, indent=2)),
        }))
    donation = site["donationUrl"]
    support = f'<p><a href="{https(donation)}">Make an optional donation</a></p>' if donation else "<p>Optional donations are planned. A donation link will appear here when one is available.</p>"
    write("guide", (SOURCE / "guide.html").read_text(encoding="utf-8"))
    write("support", page("Support Framedby", support + "<p>Reading, downloading, and running the lab are free.</p>"))
    issue_link = f'<p><a href="{repository_link}/issues/new">Open a GitHub issue</a></p>' if repo else "<p>The repository destination has yet to be configured.</p>"
    write("contribute", page("Report a reproduction", "<p>Include the lab name and version, platform, command, expected result, and observed result. Remove secrets before sharing logs.</p>" + issue_link))
    for files, folder in ((SOURCE / "assets", "assets"), (CONTENT / "downloads", "downloads")):
        target = DIST / folder
        target.mkdir(parents=True, exist_ok=True)
        for file in files.iterdir():
            copy2(file, target / file.name)
    (DIST / ".nojekyll").touch()


if __name__ == "__main__":
    build()
