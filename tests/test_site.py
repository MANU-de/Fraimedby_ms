import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit
from zipfile import ZipFile

from build import build

DIST = Path(__file__).resolve().parents[1] / "dist"


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attribute in ("href", "src"):
            if attribute in attrs:
                self.links.append(attrs[attribute])

  
class SiteTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        build()

    def test_internal_links(self):
        pages = {
            page: Links(page.read_text(encoding="utf-8"))
            for page in DIST.rglob("*.html")
        }

        for page, parsed in pages.items():
            for link in parsed.links:
                parts = urlsplit(link)

                if parts.scheme or parts.netloc:
                    continue

                if parts.path.startswith("/"):
                    target = (DIST / parts.path.lstrip("/")).resolve()
                elif parts.path:
                    target = (page.parent / parts.path).resolve()
                else:
                    target = page

                if target.is_dir():
                    target = target / "index.html"

                with self.subTest(page=page.name, link=link):
                    self.assertTrue(target.is_file(), target)

                    if parts.fragment:
                        self.assertIn(
                            parts.fragment,
                            pages[target].ids
                        )


    def test_ready_and_planned_content(self):
        home = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertEqual(home.count('data-topics='), 7)
        self.assertEqual(home.count('>Planned</p>'), 6)
        self.assertNotIn("npx frameby", home)
        lab = (DIST / "labs/authority-boundaries/index.html").read_text(encoding="utf-8")
        self.assertEqual(lab.count("<details>"), 3)
        self.assertIn("Report a reproduction", lab)
        self.assertIn("CI evidence", lab)
        self.assertIn("Reading, downloading, and running the lab are free.", (DIST / "support/index.html").read_text(encoding="utf-8"))

    def test_bundle_and_evidence(self):
        downloads = DIST / "downloads"
        bundle = downloads / "authority-boundaries-1.0.0.zip"
        expected = bundle.with_suffix(".zip.sha256").read_text().split()[0]
        self.assertEqual(hashlib.sha256(bundle.read_bytes()).hexdigest(), expected)
        with ZipFile(bundle) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn("examples/authority-boundaries/lab.yaml", archive.namelist())
        evidence = json.loads((downloads / "authority-boundaries-evidence.json").read_text(encoding="utf-8-sig"))
        self.assertEqual([row["observations"]["external_effect_count"] for row in evidence], [0, 0, 1])
        self.assertTrue(all(row["status"] == "passed" for row in evidence))
