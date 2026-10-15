# Mercado Pago

Conviene **definir el modelo temprano**; afecta legal, contable y arquitectura de webhooks.

## Dos flujos distintos

### 1. Señas / pagos del negocio (marketplace / split)

**Recomendado para SaaS de reservas.**

- Cada negocio **conecta su cuenta** de Mercado Pago (OAuth).
- La seña del turno va **directo al comercio**.
- La plataforma puede cobrar **comisión** vía split/marketplace.
- Evita que el operador del SaaS custodie dinero de terceros (menor carga legal/contable).

Implicaciones:

- Onboarding MP por tenant (estado de conexión, refresh de tokens).
- Webhooks con identificación de `tenant_id` y idempotencia.
- Planes Pro/Max según [planes-ejemplo.md](./planes-ejemplo.md).

### 2. Suscripción del negocio al SaaS

**Separado** del cobro de turnos al cliente final.

- Suscripciones MP (**preapproval**) u otro proveedor de billing.
- No mezclar con el checkout de seña del turno.

## Orden en el roadmap

Integración de seña **después** de:

- Multi-tenant + auth
- Motor de disponibilidad
- Flujo de reserva y confirmación de turno

Ver [roadmap-mvp.md](./roadmap-mvp.md).

## Checklist de diseño (borrador)

- [ ] Modelo de comisión (fija, %, solo plan pago)
- [ ] Qué pasa si el negocio desconecta MP (¿seña deshabilitada?)
- [ ] Reembolsos y cancelaciones de turno
- [ ] Moneda y país (Argentina primero, si aplica)
