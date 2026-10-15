# Turnos SaaS

Plataforma multi-tenant de reservas online. Documentación de producto y seguridad en [`docs/`](./docs/).

## Requisitos

- Docker y Docker Compose (recomendado), o Python 3.12+ y Node 20+
- PostgreSQL 16 si corrés el backend sin Docker

## Inicio rápido

```bash
cp .env.example .env
# Editar JWT_SECRET y opcionalmente FERNET_KEY

docker compose up --build
```

- API: http://localhost:8000/api/health  
- OpenAPI: http://localhost:8000/docs  
- Frontend: http://localhost:5173  

## Backend local (sin Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
# DATABASE_URL apuntando a Postgres
alembic upgrade head
uvicorn main:app --reload --app-dir src
pytest
```

## Frontend local

```bash
cd frontend
npm install
npm run dev
```

## Seguridad

Antes de implementar features, leer [`docs/seguridad/reglas-inviolables.md`](./docs/seguridad/reglas-inviolables.md). Los tests en `backend/tests/tenancy/` validan aislamiento por tenant.

## Estructura

Ver [`docs/estructura.md`](./docs/estructura.md).
