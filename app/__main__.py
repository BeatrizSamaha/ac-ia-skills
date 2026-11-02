"""Sobe o sistema: `python -m app` (cria o banco e os dados de demonstração na primeira vez)."""
import os
import secrets
from pathlib import Path

import uvicorn

from app.main import create_app
from app.seed import SENHA_DEMO, popular


def _segredo() -> str:
    if os.environ.get("JWT_SECRET"):
        return os.environ["JWT_SECRET"]
    arquivo = Path(".jwt_secret")
    if not arquivo.exists():
        arquivo.write_text(secrets.token_urlsafe(48))
    return arquivo.read_text().strip()


def main() -> None:
    app = create_app(database_url=os.environ.get("DATABASE_URL", "sqlite:///medicamentos.db"),
                     jwt_secret=_segredo())
    if popular(app.state.SessionLocal, app.state.agora().date()):
        print(f"Dados de demonstração criados. Senha de todos os usuários demo: {SENHA_DEMO}")
    port = int(os.environ.get("PORT", "8000"))
    print(f"Abra http://localhost:{port}  (API: http://localhost:{port}/docs)")
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
