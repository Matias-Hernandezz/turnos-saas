# Documentación — Turnos SaaS

Documentación de producto y arquitectura del proyecto. Los planes comerciales descritos en [planes-ejemplo.md](./planes-ejemplo.md) son **orientativos** y aún no están cerrados al 100 %.

## Índice

| Documento | Contenido |
|-----------|-----------|
| [proyecto.md](./proyecto.md) | Visión del producto: problema, objetivo, solución y resultado esperado |
| [arquitectura-multi-tenant.md](./arquitectura-multi-tenant.md) | Multi-tenant, slugs, subdominios y aislamiento de datos |
| [pagina-publica-personalizable.md](./pagina-publica-personalizable.md) | Plantillas, tema, secciones y JSON de configuración |
| [editor-ux.md](./editor-ux.md) | Editor con preview, onboarding, draft vs publicado |
| [planes-ejemplo.md](./planes-ejemplo.md) | Tabla de planes de referencia (no definitiva) |
| [mercado-pago.md](./mercado-pago.md) | Señas, marketplace OAuth y suscripciones |
| [dashboard.md](./dashboard.md) | Agenda, métricas y gestión (plan avanzado) |
| [workflows/roadmap-mvp.md](./workflows/roadmap-mvp.md) | Orden sugerido de construcción |
| [workflows/mejora-roadmap.md](./workflows/mejora-roadmap.md) | Notas de refinamiento del roadmap |
| [workflows/agent-loop.md](./workflows/agent-loop.md) | Ciclo autónomo agente (roadmap → test → push) |
| [estructura.md](./estructura.md) | Árbol de carpetas backend/frontend |
| [seguridad/README.md](./seguridad/README.md) | **Reglas de seguridad pre-código** (límites de confianza, MUST NOT, checklists) |

## Convenciones

- **MVP**: reservas + disponibilidad + página pública + admin antes del builder completo.
- **Base existente**: un proyecto previo de peluquería puede servir como núcleo; generalizar con `tenant_id` y quitar lógica específica de un solo negocio.
