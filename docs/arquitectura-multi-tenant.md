# Arquitectura multi-tenant

## Principio

- **Un solo código**, **una sola base de datos**.
- Cada negocio es un **tenant**, identificado por `tenant_id`.
- Los datos **nunca** se cruzan: todo acceso a datos va filtrado por tenant.

## Identificación del tenant (routing)

| Modo | Ejemplo | Notas |
|------|---------|--------|
| Path / slug | `turnos.tuapp.com/lauti-barber` | Típico en plan básico |
| Subdominio | `lauti.tuapp.com` | Plan superior |
| Dominio propio | `www.lautibarber.com` | Plan máximo (DNS + SSL) |

El slug es el identificador humano del negocio; internamente se mapea a `tenant_id`.

## Modelo de datos

Todas las tablas relevantes incluyen `tenant_id`, por ejemplo:

- Servicios
- Profesionales
- Turnos / reservas
- Clientes
- Pagos
- Configuración de página pública (`draft_config`, `published_config`)

Índices compuestos `(tenant_id, ...)` según patrones de consulta (agenda por fecha, listado de servicios, etc.).

## Backend: resolución del tenant

En FastAPI (o equivalente):

1. Middleware o **dependency** lee host y/o path.
2. Resuelve el tenant (cache opcional por slug/host).
3. Inyecta el contexto de tenant en **repositories** o servicios de dominio.
4. Los repositories **siempre** aplican `WHERE tenant_id = :current` (nunca confiar solo en IDs de recurso sin validar tenant).

```text
Request → resolve_tenant() → TenantContext → Repository → DB
```

## Configuración por tenant

Además de datos operativos, cada tenant guarda:

- Plan / feature flags
- Branding y página (JSON)
- Integraciones (ej. tokens OAuth de Mercado Pago por negocio)

## Seguridad y operaciones

- Usuarios del panel vinculados a uno o más tenants (roles: owner, staff).
- Jobs asíncronos (recordatorios, webhooks MP) deben llevar `tenant_id` en el payload.
- Backups y exports siempre acotados por tenant en planes que lo permitan.

## Relación con el MVP

La capa multi-tenant y auth es el **primer bloque** del roadmap; sin esto no tiene sentido el resto del producto. Ver [roadmap-mvp.md](./roadmap-mvp.md).
