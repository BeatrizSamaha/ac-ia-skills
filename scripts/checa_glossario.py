"""Guardrail sugerido pela /retro: falha se o código usar termos que o GLOSSARY.md manda evitar.

Lê as linhas `_Avoid_: a, b, c` do glossário e procura esses termos como palavras inteiras
em identificadores e textos de app/ e tests/ (sem acento e sem diferenciar maiúsculas).
"""
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Termos genéricos demais para checar mecanicamente (aparecem em sentido técnico legítimo).
IGNORADOS = {"item", "log", "edicao", "operacao", "transacao", "tipo", "role", "pacote", "produto"}


def sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()


def termos_evitados() -> set[str]:
    termos = set()
    for linha in (RAIZ / "GLOSSARY.md").read_text(encoding="utf-8").splitlines():
        if linha.startswith("_Avoid_:"):
            for t in linha.removeprefix("_Avoid_:").split(","):
                t = sem_acento(t.strip())
                if t and " " not in t and t not in IGNORADOS:
                    termos.add(t)
    return termos


def main() -> int:
    termos = termos_evitados()
    achados = []
    for arq in [*RAIZ.glob("app/**/*.py"), *RAIZ.glob("app/web/*.*"), *RAIZ.glob("tests/*.py")]:
        for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            normal = sem_acento(linha)
            for t in termos:
                if re.search(rf"(?<![a-z]){t}(?![a-z])", normal.replace("_", " ")):
                    achados.append(f"{arq.relative_to(RAIZ)}:{n}: termo evitado '{t}'")
    print("\n".join(achados) or f"OK: nenhum dos {len(termos)} termos evitados encontrado.")
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
