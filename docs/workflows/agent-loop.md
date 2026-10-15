# Agent loop — desarrollo autónomo

Workflow para agentes (Cursor u otros) trabajando en **Turnos SaaS**.

## Pasos

```text
roadmap-mvp.md → tarea pendiente → código + tests → pytest → actualizar roadmap → git commit → git push → repetir
```

## Comandos de verificación

```bash
cd backend
export JWT_SECRET=test-jwt-secret-key-32chars-min   # Windows: $env:JWT_SECRET=...
export DATABASE_URL=sqlite://
export APP_ENV=test
pytest -q
```

## Git

- Rama: `main` (salvo que el usuario indique feature branches).
- Push: `git push origin main` tras commit local exitoso.
- No incluir marcas de herramientas en mensajes de commit ni en `Co-authored-by`.

## Reglas Cursor

El archivo `.cursor/rules/autonomous-workflow.mdc` aplica este loop en cada sesión (`alwaysApply: true`).

## Estado actual

Ver checklists en [roadmap-mvp.md](./roadmap-mvp.md). La primera línea sin `[x]` es la siguiente tarea.
