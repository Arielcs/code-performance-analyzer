#!/usr/bin/env python3
"""Cria uma pasta única de relatório (opt-in), sem sobrescrever arquivos existentes."""
from __future__ import annotations

import argparse
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from uuid import uuid4

VALID_MODES = {'code-scan', 'project-scan'}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    cleaned = re.sub(r'[^a-zA-Z0-9_-]+', '_', Path(normalized).stem)
    return re.sub('_+', '_', cleaned).strip('_').lower()[:50] or 'codigo'


def create_report_structure(output_root: Path, filename: str, mode: str) -> dict[str, str]:
    if mode not in VALID_MODES:
        raise ValueError(f'Modo inválido: {mode}')
    output_root = output_root.expanduser().resolve()
    reports_root = output_root / 'performance-analysis-reports'
    reports_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = slugify(filename)
    # Random suffix prevents collisions, including concurrent invocations at same second.
    folder = None
    for _ in range(10):
        candidate = reports_root / f'performance-report_{mode}_{slug}_{timestamp}_{uuid4().hex[:10]}'
        try:
            candidate.mkdir(exist_ok=False)
            folder = candidate
            break
        except FileExistsError:
            pass
    if folder is None:
        raise RuntimeError('Não foi possível reservar pasta exclusiva para o relatório')
    report = folder / 'relatorio_performance.md'
    title = 'Projeto Inteiro' if mode == 'project-scan' else 'Código/Módulo'
    report.write_text(
        f'# Relatório de Análise de Performance — {title}\n\n'
        f'> **Análise:** `{filename}`  \n> **Modo:** `{mode}`  \n'
        f'> **Data/Hora:** `{datetime.now().isoformat(timespec="seconds")}`  \n'
        '> **Status:** Modelo inicial; diagnósticos ainda não preenchidos.\n\n'
        '---\n\n\n', encoding='utf-8'
    )
    return {'reports_root': str(reports_root), 'folder_path': str(folder),
            'report_path': str(report), 'timestamp': timestamp, 'mode': mode}


def main() -> int:
    parser = argparse.ArgumentParser(description='Cria relatório de performance somente sob demanda.')
    parser.add_argument('--execution-guide', action='store_true', help='Exibe o guia, sem criar arquivos.')
    parser.add_argument('--filename')
    parser.add_argument('--mode', choices=sorted(VALID_MODES), default='code-scan')
    parser.add_argument('--output-root', default='.')
    args = parser.parse_args()
    if args.execution_guide:
        print((Path(__file__).resolve().parent.parent / 'references' / 'execution_guide.md').read_text(encoding='utf-8'))
        return 0
    if not args.filename:
        parser.error('--filename é obrigatório fora de --execution-guide')
    try:
        result = create_report_structure(Path(args.output_root), args.filename, args.mode)
    except (ValueError, OSError, RuntimeError) as error:
        parser.error(str(error))
    for key, value in result.items():
        print(f'{key.upper()}={value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
