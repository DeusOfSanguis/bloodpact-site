import unittest
from pathlib import Path

import build


class ClanPositionsTests(unittest.TestCase):
    def setUp(self):
        self.data, _, _ = build.load()

    def test_four_clan_roles_are_cards_not_tabs(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertIn('Устройство иерархии внутри кланов', page)
        self.assertNotIn('hierarchy-tabs', page)
        block = page[page.index('squadgrid__in'):page.index('class="council-card reveal"')]
        self.assertEqual(block.count('class="squadcard"'), 4)
        for role in ('Высшая луна', 'Низшая луна', 'КМД', 'Зам. КМД'):
            self.assertIn(f'<h4>{role}</h4>', block)
        self.assertIn('Уточнение к роли высшей луны клана', block)

    def test_council_roles_are_outside_the_hierarchy_cards(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        cards = page[page.index('squadgrid__in'):page.index('class="council-card reveal"')]
        for role in ('Военачальник', 'Мастер смерти', 'Провидец'):
            self.assertNotIn(f'<h4>{role}</h4>', cards)
            self.assertIn(f'<h4 class="council-role__name">{role}</h4>', page)
        self.assertEqual(page.count('class="council-role"'), 3)

    def test_council_seats_and_eligibility(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertIn('<h3 class="council-card__title">Совет 13</h3>', page)
        self.assertEqual(page.count('class="council-seat"'), 12)
        self.assertEqual(page.count('council-seat--progenitor'), 1)
        self.assertIn('может стать любой демон в клане — кроме Луны', page)

    def test_council_is_explained_without_clan_attribution(self):
        source = Path('content/index.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        start = page.index('class="council-card reveal"')
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
