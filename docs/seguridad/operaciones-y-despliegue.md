# Operaciones y despliegue

Controles que **no viven solo en el código** pero son necesarios para “seguridad de acero” con datos de clientes. Estado inicial: **needs_validation** hasta que exista infra real.

## Secretos y claves

| Secreto | Rotación | Notas |
|---------|----------|--------|
| `JWT_SECRET` o clave privada RS256 | Periódica + incidente | Distinto por entorno |
| `FERNET_KEY` (tokens MP) | Plan de re-cifrado | Perder clave = perder tokens MP |
| Webhook secrets MP (×2 flujos) | Al rotar en panel MP | D1 |
| `DATABASE_URL` | Solo en secret manager | Nunca en imagen Docker |

## Red y edge

- TLS 1.2+ terminado en proxy de confianza.
- Rate limiting y bot protection en rutas públicas (`/slots`, reserva, login).
- Headers: `Strict-Transport-Security`, CSP, `X-Content-Type-Options`, `Referrer-Policy`.
- Solo el proxy puede setear `X-Forwarded-For` / `Host` hacia la app.

## Base de datos

- Rol de aplicación con permisos mínimos (no `SUPERUSER`).
- Backups cifrados; prueba de restore trimestral.
- Acceso humano a prod con MFA y registro (quién consultó qué).

## Object storage (media builder)

- Bucket por entorno; prefijo `tenant_id/`; políticas IAM sin listado global.
- URLs: firmadas con TTL corto o servidas vía backend con auth.

## Logs y monitoreo

- Alertas: pico 401/403, webhooks fallidos, errores 5xx en `booking` y `payments`.
- Retención de logs acorde a ley; acceso restringido.
- Proceso de **incidente**: contener → rotar secretos → notificar tenants afectados si hay leak.

## Cumplimiento (orientativo — validar con asesoría)

- Argentina: Ley 25.326 — registro de bases, finalidad, derechos ARCO.
- Política de privacidad y términos antes de producción.
- Subprocesadores (email, WhatsApp, MP, hosting) listados.

## Definition of Ready para producción

- [ ] Checklist [checklist-antes-de-merge.md](./checklist-antes-de-merge.md) en CI verde.
- [ ] Tests A5 (cross-tenant) en verde.
- [ ] Auditoría skill **standard** sin hallazgos críticos/altos abiertos.
- [ ] Runbook de incidente con contacto y plazos.
- [ ] `.env.example` completo sin secretos.
