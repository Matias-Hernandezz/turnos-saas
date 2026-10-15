# Spike Mercado Pago — decisión (MVP)

## Modelo elegido

**Marketplace / OAuth por tenant** (cada negocio conecta su cuenta MP). La seña del turno se cobra con **Checkout Pro (preferencia)** sobre el access token del comercio.

- Suscripción del SaaS al operador: **flujo separado** (`subscriptions/webhook`), fase 8.
- Comisión marketplace / split: **pendiente** (siguiente iteración; hoy 100 % al comercio).

## Flujo implementado

1. Owner (plan Pro+): `GET /api/admin/payments/mp/authorize` → redirect OAuth → `GET /api/admin/payments/mp/callback`.
2. Tokens guardados cifrados (`FERNET_KEY`, regla D3).
3. Cliente con turno en `held`: `POST /api/public/{slug}/bookings/{public_code}/checkout` → `init_point`.
4. Webhook `POST /api/webhooks/mercadopago/tenant-payments` con firma `x-signature` + idempotencia (`mp_webhook_event`).
5. Pago `approved` → turno `confirmed`, registro `payment` `approved`.

## Configuración sandbox

- Crear app en [Mercado Pago Developers](https://www.mercadopago.com.ar/developers).
- `MP_CLIENT_ID`, `MP_CLIENT_SECRET`, `MP_REDIRECT_URI` (callback admin).
- Webhook URL: `{API_PUBLIC_BASE_URL}/webhooks/mercadopago/tenant-payments` + secret en panel MP.

## Comisión plataforma

- `MP_PLATFORM_FEE_PERCENT` (0 = desactivado) → `marketplace_fee` en la preferencia MP.
- Monto persistido en `payment.platform_fee_cents`.

## Cancelación y reembolso

- Cancelar turno (`held`, `pending_payment`, `confirmed`) dispara `refund_on_cancellation`.
- Pago `approved` → reembolso total vía API MP (simulado en test).
- Pago `pending` → `cancelled` sin llamada a MP.

## Pendiente

- Refresh token automático.
- Reembolso parcial / políticas por negocio.
- UI admin “Conectar MP” y manejo de desconexión.

Ver [../mercado-pago.md](../mercado-pago.md).
