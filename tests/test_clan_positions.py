import unittest
from pathlib import Path

import build


class ClanPositionsTests(unittest.TestCase):
    def setUp(self):
        self.data, _, _ = build.load()

    def test_hierarchy_is_tabbed_like_privileges(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertIn('Устройство иерархии внутри кланов', page)
        self.assertEqual(page.count('class="tabs hierarchy-tabs" data-tabs'), 1)
        for tab in ('clan-upper', 'clan-lower', 'clan-cmd', 'clan-deputy',
                    'warlord', 'deathmaster', 'seer', 'council'):
            self.assertIn(f'data-tab="{tab}"', page)
            self.assertIn(f'data-panel="{tab}"', page)
        block = page[page.index('hierarchy-tabs'):page.index('class="gloss reveal"')]
        self.assertEqual(block.count('data-tab="'), 8)
        self.assertEqual(block.count('data-panel="'), 8)

    def test_positions_and_council_are_explained(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        for office in ('Военачальник', 'Мастер смерти', 'Провидец'):
            self.assertIn(f'<h3>{office}</h3>', page)
        self.assertIn('<h3>Совет 13</h3>', page)
        self.assertEqual(page.count('class="council-seat"'), 12)
        self.assertEqual(page.count('council-seat--progenitor'), 1)
        self.assertIn('Прародитель', page)

    def test_council_is_explained_without_clan_attribution(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        start = page.index('data-panel="council"')
        block = page[start:page.index('</div>', page.index('council-sum', start))]
        for clan in ('Обигири', 'Цербер', 'Полумесяц', 'Ямигири', 'Раншики'):
            self.assertNotIn(clan, block)

    def test_there_is_no_separate_council_page(self):
        self.assertNotIn('council', [p['slug'] for p in self.data['pages']])

    def test_incentives_use_only_one_item_per_reward(self):
        source = Path('content/incentives.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertIn('в каждом поощрении используется только один пункт', page)
        self.assertIn('выбирает один пункт из списка', page)


if __name__ == '__main__':
    unittest.main()
