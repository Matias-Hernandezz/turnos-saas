# Dashboard (administración)

El panel del negocio crece con el plan; la visión **completa** apunta al tier superior (ver [planes-ejemplo.md](./planes-ejemplo.md)).

## Agenda

- Vista **hoy / semana** (calendario).
- **Drag & drop** para mover turnos (con validación de disponibilidad).
- CRUD de reservas, bloqueos (vacaciones, feriados), horarios por profesional.

## Métricas (plan avanzado)

Indicadores sugeridos:

- Ingresos (período)
- Turnos por servicio y por profesional
- Horarios pico
- Tasa de cancelación y ausentismo
- Clientes nuevos vs recurrentes

## Ficha de cliente

- Historial de turnos
- Gasto acumulado
- Notas internas del negocio

## CRUD operativo

- Servicios (duración, precio)
- Profesionales y sus horarios
- Excepciones y bloqueos

## MVP vs completo

| Fase | Alcance |
|------|---------|
| MVP | Agenda simple, CRUD esencial, confirmar/cancelar turnos |
| Post-MVP | Métricas, fichas de cliente, exportaciones |
| Con planes | Feature flags limitan profundidad según plan |

Orden de implementación: [roadmap-mvp.md](./roadmap-mvp.md).
