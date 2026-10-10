#!/usr/bin/env python3
"""Limited Chinese structural hints; never rewrite or certify meaning.

MIT: Copyright (c) 2026 huangdijia. CLI inspired by Dustin Yuchen Teng's
asd-ste100-skill snapshot 32511c6992ecb5f1971e46a2943f2e6adceedafe.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RULES = {'dangling-conjunction', 'configured-term'}
HAN = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U000323af]')
MARKER = re.compile(r'^( *)(?:[-+*]|\d+[.)])[ \t]+')
END = re.compile(r'(以及|并且|或者|且|或|与|和)[ \t]*$')
LIMITATION = '仅检查中文列表项尾连接词和用户词表；静态提示不证明语义正确或官方 STE 合规。'


def protected_text(text):
    """Replace protected characters by opaque operands, retaining source offsets.

    Supports ordinary Markdown, not all Markdown dialects. A masked operand
    cannot accidentally become a dangling conjunction after code is removed.
    """
    chars = list(text)

    def mask(start, end):
        for pos in range(start, end):
            if not chars[pos].isspace():
                chars[pos] = '\ufffc'

    fence = None
    offset = 0
    frontmatter = text.startswith('---\n') or text.startswith('---\r\n')
    for index, line in enumerate(text.splitlines(keepends=True)):
        stripped = line.strip()
        if frontmatter:
            mask(offset, offset + len(line))
            if index and stripped in ('---', '...'):
                frontmatter = False
        elif fence:
            mask(offset, offset + len(line))
            if re.fullmatch(re.escape(fence[0]) + '{' + str(fence[1]) + ',}[ \t]*', stripped):
                fence = None
        else:
            opener = re.match(r'^\s*(`{3,}|~{3,})', line)
            if opener:
                run = opener.group(1)
                fence = (run[0], len(run))
                mask(offset, offset + len(line))
            elif line.startswith('    ') or line.startswith('\t') or stripped.startswith('>'):
                # Conservative: four-space continuations are also excluded.
                mask(offset, offset + len(line))
        offset += len(line)
    patterns = [
        r'<!--.*?-->',
        r'(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)',
        r'!?\[[^\]\n]*\]\([^\n)]*\)',
        r'^[ \t]*\[[^\]\n]+\]:[^\r\n]*$',
        r'https?://[^\s<>\ufffc。！？；，、）】》”’]+',
        r'<[^>\n]+>',
        r'"[^"\n]*"|“[^”\n]*”|「[^」\n]*」|『[^』\n]*』',
        r"'[^'\n]*'",
        r'(?:[A-Za-z]:[\\/]|\./|\.\./|~/|/)[^\s，。；！？、（）\ufffc]+',
        r'[A-Za-z_][A-Za-z0-9_.:/@+%?=&~#\\-]*',
    ]
    for pattern in patterns:
        visible = ''.join(chars)
        for match in re.finditer(pattern, visible, re.S | re.M):
            mask(*match.span())
    return ''.join(chars)


def validate_terms(config):
    if not isinstance(config, dict) or set(config) != {'terms'} or not isinstance(config['terms'], list):
        raise ValueError('词表须为 {"terms": [{"term": "字面词", "message": "核对提示"}]}')
    terms = []
    for item in config['terms']:
        if not isinstance(item, dict) or set(item) != {'term', 'message'}:
            raise ValueError('每条词表只接受 term 和 message')
        if any(not isinstance(item[k], str) or not item[k].strip() or '\n' in item[k] or '\r' in item[k] for k in item):
            raise ValueError('term/message 须为非空单行字符串')
        if not HAN.search(item['term']):
            raise ValueError('term 须含中文字符；仅作字面匹配，不执行正则')
        if re.search(r'[A-Za-z0-9_]', item['term']):
            raise ValueError('term 不接受 ASCII 字母、数字或下划线；这些标识受保护，混合词无法可靠匹配')
        terms.append(item)
    return terms


def lint(text, filename='<stdin>', terms=(), disabled=()):
    visible = protected_text(text)
    lines = visible.splitlines()
    originals = text.splitlines()
    findings = []
    covered = [i + 1 for i, line in enumerate(lines) if HAN.search(line)]

    def add(index, col, rule, match, message):
        findings.append({'file': filename, 'line': index + 1, 'col': col + 1,
                         'rule': rule, 'level': 'advisory', 'match': match,
                         'message': message})

    if 'configured-term' not in disabled:
        for index, line in enumerate(lines):
            if not HAN.search(line):
                continue
            for item in terms:
                for match in re.finditer(re.escape(item['term']), line):
                    add(index, match.start(), 'configured-term', match.group(),
                        item['message'] + '（用户词表提示；请核对原意，不自动替换。）')
    if 'dangling-conjunction' not in disabled:
        for index, line in enumerate(lines):
            marker = MARKER.match(line)
            if not marker or len(marker.group(1)) > 3:
                continue
            item = [(index, line[marker.end():], marker.end())]
            following = index + 1
            while following < len(lines):
                candidate = lines[following]
                if MARKER.match(candidate):
                    break
                if not candidate.strip():
                    following += 1
                    continue
                expanded = candidate.expandtabs(4)
                indent = len(expanded) - len(expanded.lstrip(' '))
                content_indent = len(line[:marker.end()].expandtabs(4))
                if indent < content_indent:
                    break
                item.append((following, candidate, 0))
                following += 1
            meaningful = [(n, body.rstrip(), shift) for n, body, shift in item if body.strip()]
            if not meaningful or not any(HAN.search(body) for _, body, _ in item):
                continue
            n, body, shift = meaningful[-1]
            match = END.search(body)
            if match:
                add(n, shift + match.start(), 'dangling-conjunction', match.group().strip(),
                    '列表项以连接词结束，可能缺少并列内容；请核对条件范围与续行，不自动拆句。')
    findings.sort(key=lambda f: (f['line'], f['col'], f['rule'], f['message']))
    active = sorted(RULES - set(disabled) - (set() if terms else {'configured-term'}))
    return {'file': filename, 'status': 'checked' if covered and active else 'uncovered',
            'covered_lines': covered if active else [],
            'uncovered_lines': [i + 1 for i, line in enumerate(originals) if line.strip() and (i + 1 not in covered or not active)],
            'rules_checked': active, 'findings': findings,
            'reason': None if covered and active else '无可检查的中文正文或无启用的检查规则'}


def selftest():
    cases = [('普通说明可能失败；应核对。', 0, 'checked'),
             ('- 保存结果且', 1, 'checked'),
             ('```\n- 保存且\n```', 0, 'uncovered'),
             ('- 保存且\n  发送通知。', 0, 'checked'),
             ('- 合并 `左` 和 `右`', 0, 'checked'),
             ('English only.', 0, 'uncovered')]
    for source, count, status in cases:
        result = lint(source)
        if len(result['findings']) != count or result['status'] != status:
            raise RuntimeError('selftest failed: ' + repr(source))
    print('selftest OK (6 cases; static behavior only)')


def main(argv=None):
    parser = argparse.ArgumentParser(description=LIMITATION)
    parser.add_argument('files', nargs='*', help='UTF-8 文件；- 表示 stdin')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--disable', default='', help='逗号分隔规则 ID')
    parser.add_argument('--baseline', type=int, default=0, help='允许的静态提示总数；不是质量得分')
    parser.add_argument('--terms', type=Path, help='用户明确配置的 JSON 字面词表')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args(argv)
    disabled = set(args.disable.split(',')) if args.disable else set()
    if disabled - RULES or args.baseline < 0:
        parser.error('未知规则 ID 或负数 baseline')
    if args.selftest:
        if args.files or args.terms or args.disable or args.baseline or args.json:
            parser.error('--selftest 不与其他参数组合')
        selftest()
        return 0
    try:
        terms = validate_terms(json.loads(args.terms.read_text(encoding='utf-8'))) if args.terms else []
        paths = args.files or ['-']
        if paths.count('-') > 1:
            raise ValueError('stdin 只能读取一次')
        results = [lint(sys.stdin.read() if p == '-' else Path(p).read_text(encoding='utf-8'),
                        '<stdin>' if p == '-' else p, terms, disabled) for p in paths]
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    findings = [f for result in results for f in result['findings']]
    uncovered = [r['file'] for r in results if r['status'] == 'uncovered']
    code = 2 if uncovered else 1 if len(findings) > args.baseline else 0
    report = {'files': results, 'findings': findings, 'count': len(findings),
              'baseline': args.baseline, 'uncovered_files': uncovered,
              'exit_code': code, 'limitation': LIMITATION}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']}:{f['col']} {f['rule']}: {f['message']} [{f['match']}]")
        for result in results:
            print(f"{result['file']}: {result['status']}; 未覆盖行 {result['uncovered_lines']}")
        print(f'{len(findings)} 条静态提示；baseline {args.baseline}。' + LIMITATION)
    return code


if __name__ == '__main__':
    sys.exit(main())
