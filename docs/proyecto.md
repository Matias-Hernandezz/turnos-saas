# Proyecto — Turnos SaaS

Plataforma multi-negocio para que rubros de servicios (peluquerías, barberías, tatuajes, etc.) publiquen una página de reservas, gestionen agenda y profesionales, y opcionalmente cobren seña y envíen recordatorios.

---

## Problema

Los negocios de servicios con turnos suelen depender de WhatsApp, agenda en papel o herramientas genéricas que no encajan con su rubro. Eso implica:

- Pérdida de tiempo coordinando horarios manualmente.
- Ausentismo y cancelaciones sin recordatorios automáticos.
- Poca presencia online profesional (página genérica o inexistente).
- Dificultad para cobrar seña y reducir no-shows sin integrar pagos.
- Para quien ofrece el software: mantener un código o una base de datos por cliente no escala.

---

## Objetivo

Ofrecer **un solo producto SaaS** donde cada negocio tenga:

- Reservas online con disponibilidad real según servicios, duración y profesionales.
- Una **página pública** configurable (desde plantilla simple hasta builder por secciones).
- Panel de administración (agenda, servicios, equipo, horarios).
- Funciones de mayor valor en planes superiores: pagos (Mercado Pago), recordatorios, métricas, dominio propio.

El operador del SaaS debe poder sumar miles de negocios con **un código y una base de datos**, sin mezclar datos entre clientes.

---

## Solución

### Enfoque de producto

1. **Multi-tenant**: todas las entidades llevan `tenant_id`; el tenant se resuelve por slug en path o por host (subdominio / dominio custom).
2. **Página como configuración**: la landing no se redeploya por cliente; se guarda JSON (`template`, `theme`, `sections`) y el front renderiza con un registry de componentes.
3. **Planes por capacidades** (ver [planes-ejemplo.md](./planes-ejemplo.md)): límites de profesionales, profundidad del editor, pagos, recordatorios y dominio — implementados con feature flags según plan del tenant.
4. **Pagos alineados a SaaS**: señas vía marketplace/split (cada negocio conecta su MP); suscripción del SaaS por otro canal (ej. preapproval MP).

### Enfoque técnico (resumen)

| Capa | Idea |
|------|------|
| Backend (ej. FastAPI) | Dependency que resuelve tenant y lo inyecta en repositories |
| Datos | Servicios, profesionales, turnos, clientes, pagos — siempre filtrados por `tenant_id` |
| Front público | `sections.map` + registry `{ hero, services, gallery, ... }` |
| Editor | Panel + preview en vivo; `draft_config` vs `published_config` |

Detalle en los documentos enlazados desde [README.md](./README.md).

---

## Resultado

### Para el negocio (tenant)

- Página lista en poco tiempo (plantilla + onboarding), con reserva embebida.
- Menos fricción para el cliente final (reserva desde móvil).
- Agenda centralizada; en planes altos: seña, recordatorios, métricas y ficha de cliente.

### Para el operador del SaaS

- Un despliegue, una DB, coste marginal bajo por nuevo tenant.
- Upsell claro: MP + recordatorios + dominio propio en plan superior.
- Menos soporte de diseño si el editor limita opciones que “rompen” el layout.

### Para el desarrollo

- MVP acotado: multi-tenant + auth + CRUD + **motor de disponibilidad** (con tests) + página fija + reserva + admin; después MP, builder y métricas.
- Reutilización del prototipo de peluquería como núcleo al agregar `tenant_id` y quitar acoplamiento a un solo negocio.

### Indicadores de éxito (orientativos)

- Tiempo de onboarding hasta primera reserva pública.
- Tasa de ausentismo antes/después de recordatorios y seña.
- Conversión de plan básico a planes con pagos y dominio.
- Cero incidentes de fuga de datos entre tenants (aislamiento estricto en queries).
