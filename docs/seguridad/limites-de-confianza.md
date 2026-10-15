# Límites de confianza

Mapa de **quién confía en qué** antes de escribir código. Cada endpoint o job debe etiquetarse con el límite que cruza.

## Actores (principals)

| Actor | Confianza | Qué puede hacer |
|-------|-----------|-----------------|
| **Visitante anónimo** | Mínima | Ver sitio publicado, consultar slots, crear hold/reserva con datos propios, usar `public_code` acotado |
| **Cliente final autenticado** | Baja (si existe cuenta cliente) | Solo sus reservas / perfil — *si el producto lo incluye* |
| **Staff del negocio** | Media | CRUD dentro del **tenant** asignado, sin datos de otros negocios |
| **Owner del negocio** | Media-alta | Config, MP OAuth, publicar sitio, usuarios staff, export si plan lo permite |
| **Plataforma (super-admin)** | Alta | Operación cross-tenant **solo** con rol explícito, auditoría y mínimo privilegio |
| **Mercado Pago (webhooks)** | Externo no confiable | Solo entradas firmadas/verificadas; nunca confiar en `tenant_id` del body sin correlación criptográfica |
| **Workers / cron** | Servicio interno | Identidad de sistema; payload **debe** incluir `tenant_id` validado al encolar |

## Superficies de entrada

```text
                    ┌─────────────────────────────────────┐
                    │           Internet                   │
                    └─────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
  Host/Path            Admin API            Webhooks MP
  (tenant resolve)     (JWT + tenant)       (firma + idempotencia)
        │                    │                    │
        └──────────────┬─────┴────────────────────┘
                       ▼
              FastAPI + TenancyContext
                       │
                       ▼
              PostgreSQL (tenant-scoped)
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Redis/cache    Object storage   Email/WhatsApp
     (si hay)       (media builder)   (PII en tránsito)
```

### Resolución de tenant (alto riesgo)

- **Entrada:** `Host`, path slug, dominio custom, headers `X-Forwarded-*` (solo desde proxy de confianza).
- **Riesgo:** confiar en `Host` o `X-Forwarded-Host` enviado por el cliente → routing a tenant equivocado o open redirect.
- **Invariante:** el proxy de producción **elimina** headers de forwarding falsos; la app solo lee tenant desde lista allowlisted de proxies.

Rutas según [arquitectura-multi-tenant.md](../arquitectura-multi-tenant.md).

## Datos sensibles (clasificación)

| Clase | Ejemplos | Reglas |
|-------|----------|--------|
| **PII cliente** | Nombre, teléfono, email, notas de turno | Cifrado en tránsito (TLS); mínimo en logs; retención definida; export acotado por tenant |
| **PII negocio** | Email owner, datos fiscales si hay | Igual; separar de PII de clientes en modelos |
| **Autenticación** | Password hash, JWT refresh, sesión | Nunca en logs/URLs; rotación en cambio de password |
| **Secretos MP** | OAuth refresh, access tokens | Solo en DB cifrada (`crypto.py` / Fernet); nunca al front |
| **Capacidad** | `public_code` de reserva | Alto entropía; scope solo a un turno; no enumerar |
| **Config pública** | JSON `published_config` | Tratar como **contenido no confiable** al renderizar (XSS) |

## Flujos críticos (cada uno = tests de seguridad)

1. **Registro / onboarding** — crea tenant + owner; sin asignar usuario a tenant ajeno.
2. **Login admin** — JWT con `sub`, `tenant_id` o membership; rotación; logout invalida refresh si aplica.
3. **Reserva pública** — hold → confirmar; no double-book; no leer turno sin `public_code` o permiso admin.
4. **Cancelar / ver con `public_code`** — capability token, no ID secuencial.
5. **OAuth MP** — `state` ligado a sesión + tenant; callback valida tenant del token guardado.
6. **Webhook pago** — verificar firma MP; idempotencia; actualizar solo turno del tenant del pago.
7. **Publicar sitio** — solo staff autorizado; draft no visible públicamente.
8. **Upload media** — tipo MIME real, tamaño, path por tenant; URLs sin path traversal.
9. **Jobs recordatorios** — no enviar datos de tenant A con job encolado para B.
10. **Analytics / export** — agregados siempre con `WHERE tenant_id = ?`; export = mismo filtro.

## Copias derivadas (no olvidar)

La skill de aislamiento exige rastrear **copias** del dato, no solo la fila en Postgres:

| Copia | Riesgo |
|-------|--------|
| Cache HTTP / CDN | Página de un tenant servida a otro (clave sin tenant) |
| React Query / SW | Respuesta admin cacheada tras logout o cambio de tenant |
| Logs / traces | Teléfonos y emails en texto plano |
| Backups | Restaurar sin re-aplicar borrado |
| Search (futuro) | Índice sin filtro tenant |

Cada nueva copia necesita: **clave con tenant**, **TTL**, **invalidación** al borrar o cambiar ACL.

## Fuera del repo (validar en despliegue)

Marcar como **owner-observed** en producción (no asumir en código):

- TLS y HSTS en edge
- WAF / rate limit en ingress
- Política de backups y quién puede restaurar
- Rotación de `FERNET_KEY` / JWT signing keys
- DPA / Ley 25.326 (Argentina) según asesoría legal

Detalle en [operaciones-y-despliegue.md](./operaciones-y-despliegue.md).
