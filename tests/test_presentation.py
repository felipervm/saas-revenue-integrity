"""Published artifact checks supplement, rather than replace, finance invariants."""
import base64
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from build import render_pages


class PresentationTests(unittest.TestCase):
    def test_rebuild_is_deterministic_and_embeds_local_assets(self):
        payload = json.loads((ROOT/'data/analysis.json').read_text(encoding='utf-8'))
        before = (ROOT/'index.html').read_bytes()
        render_pages(payload)
        self.assertEqual(before, (ROOT/'index.html').read_bytes())
        self.assertEqual(before, (ROOT/'site/index.html').read_bytes())
        html = before.decode('utf-8')
        image = re.search(r'src="data:image/jpeg;base64,([^"]+)"', html)
        self.assertIsNotNone(image)
        self.assertEqual(base64.b64decode(image.group(1)), (ROOT/'site/assets/felipe-mattos.jpg').read_bytes())
        self.assertNotRegex(html, r'/\* (STYLES|APP|RESULTS|PORTRAIT) \*/')

    def test_in_page_links_have_unique_targets(self):
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)))
        for target in re.findall(r'href="#([^"]+)"', html):
            self.assertIn(target, ids)

    def test_research_links_resolve_to_local_artifacts(self):
        html = (ROOT/'site/template.html').read_text(encoding='utf-8')
        paths = re.findall(r'https://github.com/felipervm/saas-revenue-integrity/blob/main/([^"\s]+)', html)
        self.assertGreater(len(paths), 4)
        for path in paths:
            self.assertTrue((ROOT/path).is_file(), path)


if __name__ == '__main__':
    unittest.main()
