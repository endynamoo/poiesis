"""The page is self-contained, semantic, and its local links resolve.

A static site has no compiler to catch a typo in an asset path or a missing alt
attribute, so this suite reads index.html the way a browser would and checks the
things that break quietly in production.
"""
import json
import re
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
        for value in sheet + scripts:
            path = urlparse(value).path          # ignore a ?v= cache-buster
            self.assertGreater((ROOT / path).stat().st_size, 1000, value)

    def test_reader_audio_matches_the_passage(self):
        """The clip is real speech, and its timings cover the words on the page."""
        audio = ROOT / "assets" / "audio" / "reader.mp3"
        self.assertGreater(audio.stat().st_size, 20000, "reader.mp3 is missing or empty")

        source = INDEX.read_text(encoding="utf-8")
        block = re.search(
            r'id="reader-timings">(.*?)</script>', source, re.S
        )
        self.assertIsNotNone(block, "no reader-timings block")
        timings = json.loads(block.group(1))

        prose = re.search(
            r'<p class="reader__prose" id="prose">(.*?)</p>', source, re.S
        )
        self.assertIsNotNone(prose, "no reader passage")
        spoken = re.sub(r"<[^>]+>", "", prose.group(1)).split()

        self.assertEqual(
            len(timings["words"]), len(spoken),
            "one timing per word of the passage",
        )
        previous = 0.0
        for start, end in timings["words"]:
            self.assertGreaterEqual(start, previous - 0.001)
            self.assertLessEqual(start, end)
            self.assertLessEqual(end, timings["duration"] + 0.05)
            previous = start
        self.assertGreater(timings["duration"], 5)

    def test_the_two_demos_exist_and_are_labelled(self):
        """Both videos ship, and the pre-alpha one says so where it is seen."""
        for name, floor in (("rhapsode-demo.mp4", 1_000_000), ("opsis-demo.mp4", 1_000_000)):
            video = ROOT / "assets" / "video" / name
            self.assertTrue(video.is_file(), "missing %s" % name)
            self.assertGreater(video.stat().st_size, floor, "%s looks truncated" % name)

        source = INDEX.read_text(encoding="utf-8")
        self.assertIn('poster="assets/img/opsis-demo-poster.webp"', source)
        self.assertTrue((ROOT / "assets" / "img" / "opsis-demo-poster.webp").is_file())

        figure = re.search(
            r'<figure class="demo demo--opsis.*?</figure>', source, re.S
        )
        self.assertIsNotNone(figure, "no Opsis footage figure")
        # the clarification has to be visible text, not a title attribute
        self.assertRegex(figure.group(0), r"Alpha footage", "alpha status not stated")
        self.assertRegex(
            figure.group(0), r"<b>Alpha footage\.</b>",
            "alpha status should open the caption, not hide in the slate",
        )

    def test_the_style_grid_is_one_scene_in_several_looks(self):
        """The style demo has to be the same beat rendered again, and it moves."""
        source = INDEX.read_text(encoding="utf-8")
        start = source.index('<figure class="styles')
        end = source.index('<section class="making"', start)   # the block ends before the next section
        block = source[start:end]
        self.assertIn("</figure>", block, "style grid never closes")

        looks = re.findall(r'assets/video/style-([a-z-]+)\.mp4', block)
        self.assertGreaterEqual(len(looks), 3, "fewer than three styles shown")
        self.assertEqual(len(looks), len(set(looks)), "a style is listed twice")
        for slug in looks:
            clip = ROOT / "assets" / "video" / ("style-%s.mp4" % slug)
            self.assertTrue(clip.is_file(), "missing clip for %s" % slug)
            self.assertGreater(clip.stat().st_size, 50_000, "%s looks truncated" % slug)
            self.assertTrue(
                (ROOT / "assets" / "img" / ("style-%s.webp" % slug)).is_file(),
                "missing poster for %s" % slug,
            )
        # each tile carries a poster and a label, so it means something before it runs
        self.assertEqual(block.count('poster="assets/img/style-'), len(looks), "a tile has no poster")
        self.assertEqual(block.count("<video"), len(looks), "a style tile is not video")

        # the mechanism, stated where a reader sees it
        for claim in ("identity + style", "field on the project"):
            self.assertIn(claim, block, "the demo does not say how style works")

    def test_the_translation_block_shows_the_rendered_samples(self):
        """The four translations must be the ones the tool wrote, not retyped ones."""
        source = INDEX.read_text(encoding="utf-8")
        start = source.index('<figure class="translation')
        end = source.index("</section>", start)
        block = source[start:end]
        data = json.loads((ROOT / "docs" / "translation-demo.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["results"]), 3, "fewer than three languages shown")
        for row in data["results"]:
            self.assertIn('lang="%s"' % row["lang"], block, "no %s row" % row["label"])
            self.assertIn(row["text"], block,
                          "%s text on the page is not the text the tool rendered" % row["label"])
        self.assertEqual(block.count("<dd lang="), len(data["results"]),
                         "a row exists on the page that the tool did not render")
        # the claim that makes it local
        self.assertIn("on this machine", block, "the block does not say where it ran")

    def test_no_link_points_at_a_repository_that_is_not_public(self):
        """Opsis's repo is private until its beta, so a link to it would 404.

        Rhapsode is public and linked. When Opsis ships, the CTA can point at
        github.com/endynamoo/opsis again; until then it points at the account.
        """
        source = INDEX.read_text(encoding="utf-8")
        self.assertNotIn("github.com/endynamoo/opsis", source,
                         "Opsis is private - that link 404s for visitors")
        self.assertIn("github.com/endynamoo/rhapsode", source, "Rhapsode link is missing")

    def test_html_is_utf8_and_not_double_encoded(self):
        """A PowerShell read/write cycle double-encodes every em dash in this file."""
        text = INDEX.read_bytes().decode("utf-8")  # raises on invalid bytes
        self.assertTrue(text.startswith("<!doctype html>"), "no BOM, no leading blank line")
        for marker in ("\u00c3", "\u00c2", "\u00e2\u0080"):
            self.assertNotIn(marker, text, "mojibake: %r" % marker)
        self.assertIn("\u2014", text, "the page should still have an em dash")


if __name__ == "__main__":
    unittest.main()
