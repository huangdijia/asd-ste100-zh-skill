"""Executable tests for static behavior, not semantic equivalence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'ste-lint.py'
spec = importlib.util.spec_from_file_location('ste_lint', SCRIPT)
lint_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_module)


class LintTests(unittest.TestCase):
    def test_positions_and_markers(self):
        for marker in ('- ', '* ', '+ ', '1. ', '2) ', '   - '):
            result = lint_module.lint(marker + '保存且', 'fixture.md')
            f, = result['findings']
            self.assertEqual((f['line'], f['col'], f['match'], f['file']),
                             (1, len(marker) + 3, '且', 'fixture.md'))

    def test_multiline_item_and_nested_items(self):
        self.assertEqual(lint_module.lint('- 保存且\n  通知用户。')['findings'], [])
        self.assertEqual(lint_module.lint('- 保存且\n\n  通知用户。')['findings'], [])
        result = lint_module.lint('- 保存\n  且\n- 通知或')
        self.assertEqual([(f['line'], f['col']) for f in result['findings']], [(2, 3), (3, 5)])
        self.assertEqual(len(lint_module.lint('- 保存且\n  - 通知或')['findings']), 2)

    def test_modality_semicolon_and_length(self):
        source = '可能应建议必须可以；不能把尝试改成成功。' + '中文说明' * 1000
        self.assertEqual(lint_module.lint(source)['findings'], [])

    def test_protected_content_and_coverage(self):
        cases = ['```python\n- 保存且\n```', '~~~~\n```\n- 保存且\n~~~~',
                 '`保存且`', '``保存`且``', '    - 保存且', '> - 保存且',
                 'https://example.com/保存且', '/配置/保存且', '“保存且”',
                 '<!-- 保存且 -->', '---\nname: 保存且\n---',
                 '[保存且](https://example.com)', 'English only.', '']
        for source in cases:
            with self.subTest(source=source):
                result = lint_module.lint(source)
                self.assertEqual(result['findings'], [])
                self.assertEqual(result['status'], 'uncovered')

    def test_operands_preserve_positions(self):
        self.assertEqual(lint_module.lint('- 合并 `左` 和 `右`')['findings'], [])
        f, = lint_module.lint('- 使用 `a` 且')['findings']
        self.assertEqual(f['col'], 10)
        f, = lint_module.lint('- 使用 https://example.com/ 且')['findings']
        self.assertEqual(f['col'], 27)

    def test_fence_character_and_length(self):
        result = lint_module.lint('````\n```\n- 保存且\n````\n- 通知或')
        self.assertEqual([f['line'] for f in result['findings']], [5])

    def test_reference_definition_does_not_swallow_prose(self):
        terms = [{'term': '检查', 'message': '核对'}]
        source = '中文引言。\n\n[ref]: https://example.com\n\n- 保存且\n检查正文。'
        result = lint_module.lint(source, terms=terms)
        self.assertEqual([(f['line'], f['rule']) for f in result['findings']],
                         [(5, 'dangling-conjunction'), (6, 'configured-term')])
        self.assertIn(6, result['covered_lines'])

    def test_url_chinese_punctuation_does_not_swallow_prose(self):
        terms = [{'term': '检查', 'message': '核对'}]
        result = lint_module.lint('访问 https://example.com。检查配置。', terms=terms)
        f, = result['findings']
        self.assertEqual((f['line'], f['col'], f['rule']), (1, 24, 'configured-term'))
        for punctuation in ('。', '！', '？', '；', '，', '、', '）'):
            with self.subTest(punctuation=punctuation):
                result = lint_module.lint('访问 https://example.com' + punctuation + '检查配置。', terms=terms)
                self.assertEqual(len(result['findings']), 1)

    def test_protected_indented_operands_remain_continuations(self):
        for indentation in ('    ', '\t', '  ', ' \t'):
            with self.subTest(indentation=repr(indentation)):
                result = lint_module.lint('- 合并 `左` 和\n' + indentation + '`右`')
                self.assertEqual(result['findings'], [])
        result = lint_module.lint('~~~\n```\n- 保存且\n~~~\n- 通知或')
        self.assertEqual([f['line'] for f in result['findings']], [5])

    def test_user_terms_literal_and_no_defaults(self):
        terms = lint_module.validate_terms({'terms': [{'term': '检查', 'message': '确认术语'}]})
        self.assertEqual(lint_module.lint('检查、验证、确认')['findings'], [])
        r = lint_module.lint('检查 `检查` https://a/检查 “检查”', terms=terms)
        self.assertEqual([(f['col'], f['match']) for f in r['findings']], [(1, '检查')])
        literal = [{'term': '检查.*', 'message': '用户提示'}]
        self.assertEqual(lint_module.lint('检查结果', terms=literal)['findings'], [])

    def test_disabled_and_partial_coverage(self):
        r = lint_module.lint('中文正文\nEnglish\n`代码`', disabled={'dangling-conjunction'})
        self.assertEqual(r['status'], 'uncovered')
        r = lint_module.lint('中文正文\nEnglish\n`代码`')
        self.assertEqual(r['covered_lines'], [1])
        self.assertEqual(r['uncovered_lines'], [2, 3])

    def test_config_validation(self):
        for config in ([], {}, {'terms': ['检查']}, {'terms': [{'term': 'check', 'message': '提示'}]},
                       {'terms': [{'term': '', 'message': '提示'}]}, {'terms': [], 'regex': True}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                lint_module.validate_terms(config)

    def test_documented_character_heuristic_limits(self):
        # Intentionally observable limitations, not a claim these phrases are wrong.
        for source in ('- 计算总和', '- 保持温和', '- 不得苟且'):
            with self.subTest(source=source):
                self.assertEqual(len(lint_module.lint(source)['findings']), 1)
        result = lint_module.lint('- 保存**且**')
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['status'], 'checked')

    def test_mixed_ascii_terms_rejected(self):
        for term in ('检查API', 'v2版本', '中文_id'):
            with self.subTest(term=term), self.assertRaisesRegex(ValueError, 'ASCII'):
                lint_module.validate_terms({'terms': [{'term': term, 'message': '核对'}]})


class CLITests(unittest.TestCase):
    def run_cli(self, *args, source='中文说明。'):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=source,
                              text=True, capture_output=True)

    def test_json_stdin_and_baseline(self):
        r = self.run_cli('--json', source='- 保存且')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)['findings'][0]['col'], 5)
        self.assertEqual(self.run_cli('--baseline', '1', source='- 保存且').returncode, 0)
        self.assertEqual(self.run_cli('--disable', 'dangling-conjunction', source='- 保存且').returncode, 2)

    def test_uncovered_overrides_baseline(self):
        r = self.run_cli('--json', '--baseline', '100', source='English')
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)['uncovered_files'], ['<stdin>'])

    def test_files_terms_and_no_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a, b, config = root / 'a.md', root / 'b.md', root / 'terms.json'
            a.write_text('- 保存且', encoding='utf-8')
            b.write_text('检查结果。', encoding='utf-8')
            config.write_text(json.dumps({'terms': [{'term': '检查', 'message': '核对含义'}]}), encoding='utf-8')
            before = {p: p.read_bytes() for p in root.iterdir()}
            r = self.run_cli('--json', '--terms', str(config), str(a), str(b))
            self.assertEqual(r.returncode, 1)
            report = json.loads(r.stdout)
            self.assertEqual(report['count'], 2)
            self.assertEqual([f['file'] for f in report['findings']], [str(a), str(b)])
            self.assertEqual(before, {p: p.read_bytes() for p in root.iterdir()})
            b.write_text('English', encoding='utf-8')
            self.assertEqual(self.run_cli(str(a), str(b)).returncode, 2)

    def test_errors(self):
        for args in (('--baseline', '-1'), ('--disable', 'unknown'), ('--unknown',),
                     ('--terms', '/missing/config.json'), ('/missing/text.md',), ('-', '-')):
            with self.subTest(args=args):
                r = self.run_cli(*args)
                self.assertEqual(r.returncode, 2)
                self.assertIn('error:', r.stderr)

    def test_selftest(self):
        r = self.run_cli('--selftest')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('selftest OK', r.stdout)


if __name__ == '__main__':
    unittest.main()
