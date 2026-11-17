"""The page is self-contained, semantic, and its local links resolve.

A static site has no compiler to catch a typo in an asset path or a missing alt
attribute, so this suite reads index.html the way a browser would and checks the
things that break quietly in production.
"""
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

RESOURCE_TAGS = {"img", "script", "source", "link", "video", "audio", "iframe"}
EXTERNAL_OK = {"http", "https", "mailto"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []          # (tag, attrs dict)
        self.ids = set()
        self.anchors = []       # href="#..." targets

    def handle_starttag(self, tag, attrs):
        attr = {k: (v if v is not None else "") for k, v in attrs}
        self.tags.append((tag, attr))
        if "id" in attr:
            self.ids.add(attr["id"])
        if tag == "a" and attr.get("href", "").startswith("#"):
            self.anchors.append(attr["href"][1:])


def parse():
    page = Page()
    page.feed(INDEX.read_text(encoding="utf-8"))
    return page


def resources(page):
    """Every local resource reference, as (tag, attribute, path)."""
    for tag, attr in page.tags:
        for key in ("src", "href"):
            value = attr.get(key, "")
            if not value or value.startswith(("#", "data:", "//")):
                continue
            parsed = urlparse(value)
            if parsed.scheme in EXTERNAL_OK:
                continue
            yield tag, key, parsed.path


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.page = parse()

    def test_document_metadata(self):
        html = [a for t, a in self.page.tags if t == "html"]
        self.assertTrue(html and html[0].get("lang") == "en")
        source = INDEX.read_text(encoding="utf-8")
        self.assertRegex(source, r"<title>\s*\S.*?</title>")
        meta = {(a.get("name") or a.get("property")): a.get("content") for t, a in self.page.tags if t == "meta"}
        for key in ("description", "viewport", "og:title", "og:image", "og:description"):
            self.assertTrue(meta.get(key), "missing meta %s" % key)

    def test_one_h1(self):
        h1s = [t for t, _ in self.page.tags if t == "h1"]
        self.assertEqual(len(h1s), 1, "the page should have exactly one h1")

    def test_every_image_has_an_alt_attribute(self):
        for tag, attr in self.page.tags:
            if tag == "img":
                self.assertIn("alt", attr, "img without alt: %s" % attr.get("src"))

    def test_local_resources_exist(self):
        for tag, key, path in resources(self.page):
            self.assertTrue(
                (ROOT / path).is_file(),
                "%s %s points at missing file %s" % (tag, key, path),
            )

    def test_resources_stay_on_this_origin(self):
        for tag, attr in self.page.tags:
            if tag not in RESOURCE_TAGS:
                continue
            for key in ("src", "href"):
                value = attr.get(key, "")
                if not value:
                    continue
                scheme = urlparse(value).scheme
                self.assertNotIn(
                    scheme, {"http", "https"},
                    "%s loads a third-party resource: %s" % (tag, value),
                )

    def test_anchor_targets_exist(self):
        for target in self.page.anchors:
            self.assertIn(target, self.page.ids, "no element with id %r" % target)

    def test_no_inline_handlers(self):
        for tag, attr in self.page.tags:
            for key in attr:
                self.assertFalse(
                    key.startswith("on"),
                    "inline handler %s on <%s>" % (key, tag),
                )

    def test_stylesheet_and_script_are_local_and_used(self):
        sheet = [a["href"] for t, a in self.page.tags if t == "link" and a.get("rel") == "stylesheet"]
        scripts = [a["src"] for t, a in self.page.tags if t == "script" and a.get("src")]
        self.assertEqual(len(sheet), 1)
        self.assertEqual(len(scripts), 1)
        for path in sheet + scripts:
            self.assertGreater((ROOT / path).stat().st_size, 1000, path)


if __name__ == "__main__":
    unittest.main()
