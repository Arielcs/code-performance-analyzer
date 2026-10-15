import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(module_name, script):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / 'scripts' / script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


inv = load('inventory_module', 'project_inventory.py')
rep = load('report_module', 'generate_report.py')


class InventoryTests(unittest.TestCase):
    def test_distant_find_string_is_not_db_in_loop(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'example.py'
            p.write_text('for item in items:\n    print(item)\n\n# unrelated\nprint("we will find a solution")\n')
            score, signals, evidence, partial = inv.content_risk_score(p)
            self.assertEqual(score, 0)
            self.assertEqual(signals, [])
            self.assertFalse(partial)

    def test_unrelated_find_function_is_not_db_in_loop(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'example.py'
            p.write_text('for item in items:\n    print(item)\n\nfind(whatever)\n')
            score, *_ = inv.content_risk_score(p)
            self.assertEqual(score, 0)

    def test_detect_loop_repeated_db_with_line(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'example.py'
            p.write_text('for item in items:\n    repository.findById(item)\n')
            score, signals, evidence, _ = inv.content_risk_score(p)
            self.assertGreater(score, 0)
            self.assertIn(2, [x['line'] for x in evidence])
            self.assertTrue(any('loop' in x for x in signals))

    def test_no_loop_no_loop_flag(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'example.py'
            p.write_text('repository.findById(item)\n')
            _, signals, _, _ = inv.content_risk_score(p)
            self.assertFalse(any('loop' in x for x in signals))

    def test_reads_only_limited_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'large.py'
            p.write_text('a = 1\n' * 20000)
            with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Should not read all')):
                _, _, _, partial = inv.content_risk_score(p)
            self.assertTrue(partial)

    def test_skips_own_output_and_dependency_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'service.py').write_text('print(1)')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'index.js').write_text('console.log(0)')
            output = root / 'reports'
            output.mkdir()
            (output / 'old.py').write_text('findAll()')
            d = inv.inventory(root, output)
            self.assertEqual(d['total_files_considered'], 1)
            self.assertEqual(d['top_candidates_for_deep_dive'][0]['path'], 'src/service.py')
            self.assertTrue((output / 'project_inventory.json').exists())

    def test_json_has_sample_limit_and_disclaimer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'project'
            root.mkdir()
            (root / 'repository.java').write_text('class Repository {}')
            out = Path(tmp) / 'output'
            data = inv.inventory(root, out)
            self.assertIn('disclaimer', data)
            self.assertIn('content_sample_partial', json.loads((out/'project_inventory.json').read_text())['top_candidates_for_deep_dive'][0])

    def test_invalid_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                inv.inventory(root, root / 'out', max_files=0)


class ReportTests(unittest.TestCase):
    def test_rapid_reports_never_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = rep.create_report_structure(root, 'project', 'project-scan')
            p1 = Path(first['report_path'])
            p1.write_text('PREVIOUS REPORT')
            second = rep.create_report_structure(root, 'project', 'project-scan')
            self.assertNotEqual(first['folder_path'], second['folder_path'])
            self.assertEqual(p1.read_text(), 'PREVIOUS REPORT')
            self.assertTrue(Path(second['report_path']).exists())

    def test_slug_is_safe(self):
        self.assertEqual(rep.slugify('Módulo de DB.sql'), 'modulo_de_db')
        self.assertEqual(rep.slugify('../bad.txt'), 'bad')

    def test_invalid_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                rep.create_report_structure(Path(tmp), 'x', 'full-scan')


if __name__ == '__main__':
    unittest.main()
