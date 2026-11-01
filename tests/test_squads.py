import copy
import unittest
from pathlib import Path

import build


class SquadPageTests(unittest.TestCase):
    def setUp(self):
        self.data, _, _ = build.load()

    def test_spider_family_is_a_separate_editable_group(self):
        squads = self.data['lists']['squads']
        self.assertNotIn('Семья Пауков', [clan['name'] for clan in squads['squads']])
        self.assertIn('Семья Пауков', [group['name'] for group in squads['special']])
        source = Path('content/squads.html').read_text(encoding='utf-8')
        page = build.render_fragment(source, self.data)
        self.assertEqual(page.count('<h3 class="squad">Семья Пауков</h3>'), 1)
        self.assertIn('Особые объединения', page)
        self.assertIn('вне обычной системы высших и поглощённых кланов', page)
        self.assertIn('Руи — Пятая Низшая Луна', page)
        self.assertIn('Проведение особых пыток', page)
        self.assertNotIn('{{squads}}', page)

    def test_group_type_drives_output_not_its_name(self):
        data = copy.deepcopy(self.data)
        squads = data['lists']['squads']
        family = squads['special'].pop()
        family['name'] = 'Любое объединение'
        squads['squads'].append(family)
        page = build.render_squads(data)
        self.assertNotIn('Особые объединения', page)
        self.assertIn('<strong>Высший клан</strong>', page)
        self.assertIn('Любое объединение', page)
        squads['squads'].pop()
        squads['special'].append(family)
        page = build.render_squads(data)
        self.assertIn('<strong>Особое объединение</strong>', page)
        self.assertIn('Любое объединение', page)

    def test_empty_and_legacy_data(self):
        data = copy.deepcopy(self.data)
        data['lists']['squads'] = {'squads': []}
        self.assertEqual(build.render_squads(data), '')
        data['lists']['squads']['special'] = [{'name': '<Особые>', 'tasks': ['<задача>']}]
        page = build.render_squads(data)
        self.assertIn('&lt;Особые&gt;', page)
        self.assertIn('&lt;задача&gt;', page)
        self.assertNotIn('<strong>Высший клан</strong>', page)


if __name__ == '__main__':
    unittest.main()
