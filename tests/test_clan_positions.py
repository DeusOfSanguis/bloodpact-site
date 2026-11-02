import unittest
from pathlib import Path

import build


class ClanPositionsTests(unittest.TestCase):
    def setUp(self):
        self.data, _, _ = build.load()

    def test_positions_are_part_of_the_clan_hierarchy_on_the_home_page(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertIn('Устройство иерархии внутри кланов', page)
        self.assertIn('Должности клана', page)
        for office in ('Военачальник', 'Мастер смерти', 'Провидец'):
            self.assertIn(f'<h4 class="office__name">{office}</h4>', page)
        self.assertEqual(page.count('class="office"'), 3)
        self.assertEqual(page.count('class="council-seat"'), 12)
        self.assertEqual(page.count('council-seat--progenitor'), 1)
        self.assertIn('Совет 13', page)
        self.assertIn('Прародитель', page)

    def test_council_is_explained_without_clan_attribution(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        block = page[page.index('class="council-card"'):]
        block = block[:block.index('</div>', block.index('council-card__sum'))]
        for clan in ('Обигири', 'Цербер', 'Полумесяц', 'Ямигири', 'Раншики'):
            self.assertNotIn(clan, block)

    def test_there_is_no_separate_council_page(self):
        self.assertNotIn('council', [p['slug'] for p in self.data['pages']])

    def test_incentives_use_only_one_item_per_category(self):
        source = Path('content/incentives.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertIn('в каждой категории используется только один пункт', page)


if __name__ == '__main__':
    unittest.main()
