# Patrones de seguridad por módulo

Traduce [estructura.md](../estructura.md) a controles concretos. Al agregar un archivo en estas carpetas, actualizar la fila correspondiente.

## Backend (`backend/src`)

| Módulo | Actor principal | Límite cruzado | Controles obligatorios |
|--------|-----------------|----------------|-------------------------|
| `tenancy/middleware` | Todos | Internet → tenant context | Host allowlist; no trust client `X-Forwarded-*` sin proxy; cache de slug con TTL |
| `tenancy/dependencies` | Admin | Auth → tenant | `get_current_tenant` + membership; `require_feature` antes de MP/builder |
| `core/base_repository` | — | DB | A1–A3; tests de fuga |
| `auth` | Owner/staff | Credenciales | B1–B4; rate limit; bcrypt/argon2 |
| `tenants` | Owner / anónimo registro | Creación tenant | Un usuario no queda owner de tenant existente; invitaciones con token one-time |
| `catalog` | Staff | Tenant data | CRUD solo tenant; IDs opacos en API pública si se listan servicios |
| `availability` | Público + staff | Lectura horarios | Slots sin revelar datos de otros clientes; rate limit GET slots |
| `booking/router_public` | Anónimo | Reserva | C1–C3; `public_code`; holds + job expiración |
| `booking/router_admin` | Staff | Turnos tenant | Autorización por rol; drag-drop = misma validación que PATCH |
| `customers` | Staff | PII | Mínimo necesario; no endpoint público de listado |
| `payments` | Owner + MP | Dinero | D1–D5; OAuth state; cifrado tokens |
| `subscriptions` | Owner + MP | Billing SaaS | Separado de payments; no mezclar webhooks |
| `site_builder` | Staff / público | XSS + leak draft | JSON schema estricto; publish gate; media E5 |
| `analytics/queries` | Staff | Agregados | SQL solo con tenant; cuidado joins que multipliquen filas cross-tenant |
| `notifications/jobs` | Sistema | PII saliente | H1; plantillas sin loguear cuerpo completo |
| `reviews` | Público/staff | UGC | Moderación; sanitizar texto; rate limit creación |
| `workers/tasks` | Sistema | Async | H1–H2; dead-letter con tenant_id |

## Frontend (`frontend/src`)

| Módulo | Riesgo principal | Controles |
|--------|------------------|-----------|
| `shared/api/client` | Token leak | Interceptors; no loguear bodies; refresh seguro |
| `public-site` + `registry` | Stored XSS | F1, E3; theme URLs E4 |
| `public-site/booking` | Abuse / bots | Captcha/Turnstile (futuro); no confiar en validación solo client |
| `site-builder/preview` | Draft leak | F5; preview con token admin |
| `payments-settings` | OAuth confusion | Solo redirect server-side; nunca pegar secret en front |
| `bookings-admin` | IDOR vía API | No construir URLs con IDs de otra sesión; confiar en API 403 |

## Tests mínimos por módulo (desde el día 1)

| Área | Archivo sugerido | Qué prueba |
|------|------------------|------------|
| Tenant | `tests/tenancy/test_isolation.py` | A5 cross-tenant en cada repository |
| Availability | `tests/availability/` | Lógica pura + sin leak PII en slots |
| Booking | `tests/booking/` | Race hold; public_code scope |
| Payments | `tests/payments/` | Webhook firma inválida → 401; idempotencia |

## Matriz rápida: clases de ataque (skill Cloudflare)

| Dominio skill | Aplica a Turnos SaaS |
|---------------|----------------------|
| DATA-ISOLATION-AND-LIFECYCLE | **Prioridad máxima** — todo el producto |
| WEB-PROTOCOL-AND-AUTH | JWT, OAuth MP, cookies admin |
| CLIENT-SIDE | Builder + public-site |
| PROTOCOLS-RPC (webhooks) | MP webhooks |
| RESOURCE-EXHAUSTION | slots, reserva pública, uploads |
| SUPPLY-CHAIN | CI, dependencias |
| CLOUD-AND-DEPLOYMENT | Cuando exista IaC — [operaciones-y-despliegue.md](./operaciones-y-despliegue.md) |
