#!/usr/bin/env python3
"""Atalho retrocompatível: exibe o guia sem criar artefatos."""
from pathlib import Path

if __name__ == '__main__':
    print((Path(__file__).resolve().parent.parent / 'references' / 'execution_guide.md').read_text(encoding='utf-8'))
