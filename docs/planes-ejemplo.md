# Planes comerciales (ejemplo de referencia)

> **Importante:** esta tabla **no está cerrada al 100 %**. Sirve para alinear producto, desarrollo (feature flags) y pricing. Ajustar nombres, límites y checkmarks antes de lanzar comercialmente.

## Tabla orientativa

| Capacidad | Básico | Pro | Max |
|-----------|--------|-----|-----|
| Reservas online | Sí | Sí | Sí |
| Profesionales | 1 | Hasta 5 | Ilimitados |
| Mercado Pago / seña | No | Sí | Sí |
| Página pública | Plantilla fija + logo/colores | + Secciones reordenables | Builder completo + dominio propio |
| Dashboard | Mismo panel; métricas/clientes/export **bloqueados** | Módulos desbloqueados según fila | Completo + export |
| Recordatorios WhatsApp / email | No | Email | Email + WhatsApp |
| Soporte | Email | Email | Prioritario |

## Valor percibido (hipótesis)

Lo que más suele justificar el salto al plan superior:

1. **Seña con Mercado Pago** — reduce ausentismo y mejora flujo de caja.
2. **Recordatorios automáticos** — menos no-shows.
3. **Dominio propio** — marca y confianza (plan Max).

## Implementación técnica

- Campo `plan` (o equivalente) en el tenant.
- **Feature flags** por plan: límites (`max_professionals`), `can_use_mp`, `can_reorder_sections`, `custom_domain`, `whatsapp_reminders`, etc.
- Validar límites en API al crear recursos, no solo en UI.

## Documentos relacionados

- [mercado-pago.md](./mercado-pago.md) — Pro/Max y señas
- [pagina-publica-personalizable.md](./pagina-publica-personalizable.md) — qué puede editar cada nivel
- [dashboard.md](./dashboard.md) — profundidad del panel por plan
