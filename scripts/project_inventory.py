#!/usr/bin/env python3
"""Inventário leve para priorizar *candidatos* à análise; não diagnostica gargalos.

Uso: python3 scripts/project_inventory.py --project-root . --output-root /tmp/inventory
Requer Python 3.9+; sem dependências externas.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path

IGNORE_DIRS = {
    '.git', 'node_modules', 'dist', 'build', 'target', 'out', 'coverage', '.cache',
    '.next', '.nuxt', '.angular', '.gradle', '.mvn', 'vendor', 'bin', 'obj',
    '.idea', '.vscode', '__pycache__', '.pytest_cache', '.venv', 'venv',
    '.terraform', '.serverless', 'elm-stuff', '_build', 'performance-analysis-reports',
}
IGNORE_SUFFIXES = {'.map', '.min.js', '.min.css', '.pyc', '.class', '.o', '.a', '.so', '.dll'}
IGNORE_FILENAMES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Gemfile.lock',
    'poetry.lock', 'Pipfile.lock', 'Cargo.lock',
}
ROLE_KEYWORDS = {
    'entrada/api': ['controller', 'route', 'resolver', 'handler', 'endpoint', 'router', 'resource'],
    'regra de negócio': ['service', 'usecase', 'use_case', 'use-case', 'application', 'domain', 'interactor'],
    'banco de dados': ['repository', 'dao', 'mapper', 'query', 'prisma', 'entity', 'migration', 'schema'],
    'job/worker': ['job', 'scheduler', 'worker', 'consumer', 'listener', 'queue', 'task', 'batch', 'cron'],
    'integração externa': ['client', 'gateway', 'grpc', 'kafka', 'rabbit', 'storage', 'provider', 'adapter'],
    'renderização/frontend': ['component', 'page', 'template', 'pipe', 'directive', 'widget', 'screen'],
    'configuração': ['config', 'settings', 'env', 'docker', 'compose', 'application', 'properties', 'yaml'],
    'utilitário sensível': ['parser', 'serializer', 'mapper', 'converter', 'processor', 'transformer'],
}
CONFIG_FILES = {
    'pom.xml', 'build.gradle', 'settings.gradle', 'package.json', 'angular.json',
    'nest-cli.json', 'requirements.txt', 'pyproject.toml', 'setup.py', 'manage.py',
    'docker-compose.yml', 'docker-compose.yaml', 'Dockerfile', 'application.properties',
    'application.yml', 'application.yaml', 'tsconfig.json', 'vite.config.ts',
    'vite.config.js', 'webpack.config.js', 'next.config.js', 'nuxt.config.ts',
    'svelte.config.js', 'go.mod', 'Cargo.toml', 'composer.json',
}
LANG_BY_EXT = {
    '.java': 'Java', '.kt': 'Kotlin', '.ts': 'TypeScript', '.tsx': 'TypeScript/React',
    '.js': 'JavaScript', '.jsx': 'JavaScript/React', '.py': 'Python', '.sql': 'SQL',
    '.go': 'Go', '.php': 'PHP', '.rb': 'Ruby', '.rs': 'Rust', '.cs': 'C#',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.c': 'C', '.h': 'C/C++ Header',
    '.html': 'HTML', '.vue': 'Vue', '.svelte': 'Svelte', '.ex': 'Elixir',
    '.exs': 'Elixir', '.scala': 'Scala', '.swift': 'Swift', '.dart': 'Dart',
    '.scss': 'SCSS', '.css': 'CSS', '.xml': 'XML', '.yml': 'YAML', '.yaml': 'YAML',
    '.json': 'JSON', '.graphql': 'GraphQL', '.gql': 'GraphQL', '.proto': 'Protobuf',
}
CODE_EXTENSIONS = {'.java', '.kt', '.ts', '.tsx', '.js', '.jsx', '.py', '.sql',
                   '.go', '.php', '.rb', '.rs', '.cs', '.cpp', '.cc', '.cxx', '.c'}
CONTENT_READ_LIMIT = 8_000

# Sinais simples e explícitos, jamais usados isoladamente para afirmar um gargalo.
STATIC_SIGNALS = (
    (re.compile(r'\bSELECT\s+\*\s+FROM\b', re.I), 2, 'SELECT * (avaliar projeção/volume)'),
    (re.compile(r'\b(?:findAll|find_all|getAll|listAll|fetchAll)\s*\(', re.I), 2,
     'listagem ampla possível (verificar filtros/paginação)'),
    (re.compile(r'\b(?:readlines|deepcopy)\s*\('), 1, 'cópia/leitura integral possível'),
    (re.compile(r'\b(?:iterrows|itertuples)\s*\('), 2, 'iteração Pandas (avaliar escala)'),
    (re.compile(r'\b(?:synchronized\s*\(|\.lock\s*\(|\.acquire\s*\()'), 1,
     'uso de lock (avaliar contenção)'),
    (re.compile(r'\bwhile\s+True\s*:'), 1, 'loop persistente (avaliar saída)'),
)
LOOP_START = re.compile(r'\b(?:for\s*\(|for\s+\w+\s+in\b|while\s*\(|\.forEach\s*\(|\.each\s+do\b)')
COSTLY_CALL = re.compile(
    r'\b(?:execute(?:Query|Update)?|query|fetch|open)\s*\('
    r'|\b(?:requests|axios|urllib)\.(?:get|post|put|request)\s*\('
    r'|\b(?:repository|repo|dao)\.\w+\s*\('
    r'|\.findBy[A-Z]\w*\s*\('
    r'|\b(?:httpClient|webClient)\.\w+\s*\('
)


def _blank_literals(line: str) -> str:
    """Remove literais/comentários simples sem fundir linhas; sem pretensão de parser."""
    # Tratamento deliberadamente conservador: certos casos complexos (template string,
    # multiline string, regex literal) podem escapar; resultados são apenas triagem.
    line = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
    line = re.sub(r"'(?:\\.|[^'\\])*'", "''", line)
    line = re.sub(r'`(?:\\.|[^`\\])*`', '``', line)
    return re.sub(r'//.*$|#.*$', '', line)


def _in_loop_body(lines: list[str], index: int) -> list[tuple[int, str]]:
    """Retorna pequenas janelas locais, com limite de bloco para Python.

    Não infere aninhamento completo em linguagens com chaves; os sinais permanecem
    heurísticos e exigem leitura humana.
    """
    start_line = lines[index]
    python_style = bool(re.search(r'\bfor\s+\w+\s+in\b[^:]*:\s*$', start_line))
    base_indent = len(start_line) - len(start_line.lstrip())
    out = []
    for j in range(index + 1, min(len(lines), index + 9)):
        line = lines[j]
        if python_style and line.strip() and len(line) - len(line.lstrip()) <= base_indent:
            break
        if not python_style and j > index + 1 and line.lstrip().startswith('}'):
            break
        out.append((j + 1, line))
    return out


def content_risk_score(path: Path) -> tuple[int, list[str], list[dict], bool]:
    """Lê só 8 KiB (aprox.) e retorna indicadores, linhas e flag de amostra parcial."""
    if path.suffix.lower() not in CODE_EXTENSIONS:
        return 0, [], [], False
    try:
        with path.open('rb') as handle:
            raw = handle.read(CONTENT_READ_LIMIT + 1)
    except (OSError, UnicodeError):
        return 0, [], [], False
    partial = len(raw) > CONTENT_READ_LIMIT
    clean_lines = [_blank_literals(x) for x in raw[:CONTENT_READ_LIMIT].decode('utf-8', 'replace').splitlines()]
    # SQL preserva palavras-chave fora dos literais; nunca trate query como execução.
    score, evidence, signals = 0, [], set()
    for number, line in enumerate(clean_lines, 1):
        for pattern, pts, label in STATIC_SIGNALS:
            if pattern.search(line) and label not in signals:
                signals.add(label)
                evidence.append({'line': number, 'signal': label})
                score += pts
        if LOOP_START.search(line):
            for body_line, body in _in_loop_body(clean_lines, number - 1):
                if COSTLY_CALL.search(body):
                    label = 'loop com operação potencialmente custosa (verificar fluxo)'
                    if label not in signals:
                        signals.add(label)
                        evidence.append({'line': body_line, 'signal': label})
                        score += 3
                    break
    return score, sorted(signals), evidence, partial


def should_ignore(path: Path, root: Path) -> tuple[bool, str]:
    if path.is_symlink():
        return True, 'link simbólico ignorado'
    if any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
        return True, 'diretório gerado/dependências'
    if path.name in IGNORE_FILENAMES:
        return True, f'lock/dependência: {path.name}'
    if any(path.name.endswith(suffix) for suffix in IGNORE_SUFFIXES):
        return True, 'artefato compilado/gerado'
    return False, ''


def detect_role(path: Path) -> str:
    name = '/'.join(path.parts).lower()
    roles = [role for role, keys in ROLE_KEYWORDS.items() if any(k in name for k in keys)]
    return ', '.join(roles) if roles else 'não classificado'


def name_risk_score(path: Path, role: str) -> int:
    value = '/'.join(path.parts).lower()
    points = {'banco de dados': 4, 'job/worker': 4, 'entrada/api': 3,
              'renderização/frontend': 2, 'configuração': 2}
    score = sum(num for key, num in points.items() if key in role)
    if any(x in value for x in ('report', 'relatorio', 'import', 'export', 'download', 'upload', 'batch')):
        score += 2
    if path.name in CONFIG_FILES:
        score += 2
    if any(x in value for x in ('test', 'spec', 'mock', 'fixture', '__test__', '.test.', '.spec.')):
        score -= 4
    return score


def inventory(root: Path, output_root: Path, max_files: int = 5000, top_n: int = 30) -> dict:
    root, output_root = root.resolve(), output_root.resolve()
    if not root.is_dir():
        raise ValueError(f'project-root inválido: {root}')
    if max_files <= 0 or top_n <= 0:
        raise ValueError('max-files e top-n devem ser positivos')
    output_root.mkdir(parents=True, exist_ok=True)
    files, skipped, by_language, by_role, configs = [], Counter(), Counter(), Counter(), []
    # Pruna diretórios antes do traversal, evitando caminhar por node_modules/build.
    for base, dirs, names in os.walk(root, followlinks=False):
        base_path = Path(base)
        usable = []
        for d in dirs:
            current = base_path / d
            if d in IGNORE_DIRS or current.is_symlink():
                skipped['diretórios ignorados (não percorridos)'] += 1
            elif current.resolve() == output_root or output_root in current.parents:
                skipped['pasta de saída (não percorrida)'] += 1
            else:
                usable.append(d)
        dirs[:] = sorted(usable)
        for name in sorted(names):
            path = base_path / name
            if path == output_root or output_root in path.parents:
                skipped['pasta de saída'] += 1
                continue
            if not path.is_file():
                continue
            ignored, reason = should_ignore(path, root)
            if ignored:
                skipped[reason] += 1
                continue
            if len(files) >= max_files:
                skipped['limite max-files alcançado (parcial)'] += 1
                continue
            rel, ext = path.relative_to(root), path.suffix.lower()
            role = detect_role(rel)
            cs, signals, details, partial = content_risk_score(path)
            item = {
                'path': rel.as_posix(), 'extension': ext or 'sem extensão',
                'language': LANG_BY_EXT.get(ext, 'Outro/Desconhecido'),
                'role': role, 'priority_score': name_risk_score(rel, role) + cs,
                'name_score': name_risk_score(rel, role), 'content_score': cs,
                'content_signals': signals, 'content_signal_evidence': details,
                'content_sample_partial': partial, 'size_bytes': path.stat().st_size,
            }
            files.append(item)
            by_language[item['language']] += 1
            by_role[role] += 1
            if name in CONFIG_FILES:
                configs.append(rel.as_posix())
    selected = sorted(files, key=lambda r: (r['priority_score'], r['size_bytes']), reverse=True)[:top_n]
    data = {
        'project_root': str(root), 'disclaimer': 'Triagem heurística; não constitui diagnóstico de gargalo.',
        'top_n': top_n, 'total_files_considered': len(files),
        'inventory_may_be_partial': bool(skipped['limite max-files alcançado (parcial)']),
        'ignored_summary': dict(skipped), 'languages': dict(by_language),
        'roles': dict(by_role), 'config_files': configs,
        'top_candidates_for_deep_dive': selected,
    }
    (output_root / 'project_inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    md = [
        '# Inventário de Projeto — Triagem para análise de performance', '',
        '> **Aviso:** a pontuação é heurística, não comprova gargalos nem severidade.', '',
        f'Arquivos considerados: **{len(files)}**; inventário parcial: **{data["inventory_may_be_partial"]}**.',
        '', '## Linguagens',
    ]
    md += [f'- {lang}: {count}' for lang, count in by_language.most_common()]
    md += ['', '## Exclusões', *[f'- {reason}: {count}' for reason, count in skipped.most_common()],
           '', '## Configurações identificadas', *[f'- `{p}`' for p in configs[:50]],
           '', f'## Candidatos para deep dive (top {top_n})',
           '| Score | Arquivo | Linguagem | Papel | Sinais |', '|---:|---|---|---|---|']
    for item in selected:
        safe_path = item['path'].replace('|', r'\|')
        safe_role = item['role'].replace('|', r'\|')
        md.append(f'| {item["priority_score"]} | `{safe_path}` | {item["language"]} | {safe_role} | '
                  f'{", ".join(item["content_signals"]) or "—"} |')
    (output_root / 'project_inventory.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description='Triagem heurística para project-scan.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--output-root', required=True)
    parser.add_argument('--max-files', type=int, default=5000)
    parser.add_argument('--top-n', type=int, default=30)
    args = parser.parse_args()
    try:
        data = inventory(Path(args.project_root).expanduser(), Path(args.output_root).expanduser(),
                         args.max_files, args.top_n)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f'FILES_CONSIDERED={data["total_files_considered"]}')
    print('INVENTORY_JSON=' + str(Path(args.output_root).expanduser().resolve() / 'project_inventory.json'))
    print('INVENTORY_MD=' + str(Path(args.output_root).expanduser().resolve() / 'project_inventory.md'))
    print('AVISO: Pontuações são indícios para triagem, não gargalos confirmados.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
