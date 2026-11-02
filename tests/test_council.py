import unittest
from pathlib import Path

import build


class CouncilPageTests(unittest.TestCase):
    def setUp(self):
        self.data, _, _ = build.load()
        self.page = next(p for p in self.data['pages'] if p['slug'] == 'council')

    def test_page_is_in_menu_after_clans(self):
        slugs = [p['slug'] for p in self.data['pages']]
        self.assertEqual(slugs.index('council'), slugs.index('squads') + 1)
        self.assertEqual(self.page['nav'], 'Совет')
        self.assertEqual(self.page['sigil'], '議')

    def test_three_offices_and_thirteen_seats(self):
        source = Path('content/council.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        for office in ('Военачальник', 'Мастер смерти', 'Провидец'):
            self.assertIn(f'<h3>{office}</h3>', page)
        self.assertEqual(page.count('class="office"'), 3)
        self.assertEqual(page.count('class="seat'), 13)
        self.assertIn('Прародитель', page)
        self.assertIn('4 клана × 3 представителя', page)

    def test_no_unresolved_placeholders(self):
        source = Path('content/council.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertNotIn('{{', page)
        self.assertNotIn('&lt;@', page)


if __name__ == '__main__':
    unittest.main()
