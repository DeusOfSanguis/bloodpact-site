import unittest
from pathlib import Path

import build


class LawPageTests(unittest.TestCase):
    def setUp(self):
        self.data, _, _ = build.load()
        self.page = build.render_fragment(
            Path('content/law.html').read_text(encoding='utf-8'), self.data
        )

    def test_reprimand_levels(self):
        self.assertIn('<h3>Выговоры</h3>', self.page)
        self.assertEqual(self.page.count('class="reprimand"'), 2)
        self.assertEqual(self.page.count('class="reprimand reprimand--final"'), 1)
        for title in ('Запрет на повышение', 'Снятие привилегий', 'Статус отступника'):
            self.assertIn(title, self.page)
        self.assertIn('РПК', self.page)
        self.assertIn('Не афишируется', self.page)

    def test_reprimand_removal_and_reasons(self):
        self.assertIn('Как снять выговор?', self.page)
        self.assertIn('смотрящим лунам своего отряда', self.page)
        self.assertIn('За что назначаются выговоры?', self.page)
        reasons = self.page[self.page.index('class="reprimand-reasons"'):]
        self.assertEqual(reasons.count('<li>'), 5)
        self.assertIn('ЧС демонов', reasons)


if __name__ == '__main__':
    unittest.main()
