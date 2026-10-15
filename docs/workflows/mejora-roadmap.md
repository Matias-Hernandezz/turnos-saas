Está muy bien, el orden es correcto: seguridad desde el día 0, motor de disponibilidad con tests antes que la UI, y el builder después de tener un MVP vendible. Le haría estos ajustes:

1. Falta el email de confirmación en el MVP (fase 3)
Un MVP sin confirmación al cliente no se puede vender. Meté email transaccional mínimo (confirmación + link de cancelación con public_code) en la fase 3. Los recordatorios y WhatsApp se quedan para después.

2. Salí a probar con un negocio real al terminar la fase 4
Con el peluquero amigo, antes de arrancar MP o el builder. Los problemas reales (horarios raros, cancelaciones, qué le falta al dashboard) los vas a descubrir ahí, no en el diseño. Mientras tanto la suscripción se cobra manual (transferencia), no hace falta automatizarla todavía.

3. Hacé un spike de Mercado Pago durante la fase 4
OAuth por tenant, webhooks y sandbox son lo que más tiempo suele comerse (permisos, credenciales, casos borde de pagos pendientes/rechazados). Hacé una prueba chica en paralelo con la agenda para que la fase 5 no te sorprenda. Y decidí temprano si vas con split/marketplace o cuenta propia.

4. Dejá el esqueleto de planes en la fase 1
Solo plan_id en el tenant y la dependency require_feature(...), aunque todavía no limite nada. Si lo dejás todo para la fase 8, tenés que volver a tocar cada endpoint. El cobro automático sí queda al final.

5. La anti doble-reserva va en la fase 2, no después
El EXCLUDE constraint y el test de concurrencia (dos requests al mismo slot) son parte del motor de disponibilidad. Es lo que más rompe la confianza si falla.

6. Faltan dos temas que no aparecen en el roadmap

Anti-abuso de la reserva pública: como no hay login, cualquiera puede bloquearte slots con reservas falsas. Rate limiting por IP/teléfono, hold corto y, si hace falta, verificación por código al teléfono. Va en la fase 3.
Ops mínimas: migraciones Alembic desde el inicio, backups de Postgres, Sentry/logs, subdominios (wildcard DNS) y deploy. Armalo antes de que entre el primer cliente real.

7. Partí la fase 6 y la fase 7

6a: plantilla + tema (colores, logo, textos). Es barato y ya da la sensación de “mi página”.
6b: secciones reordenables, draft/publicado, preview. Es lo caro.
Fase 7: los recordatorios valen más que las métricas porque bajan el ausentismo y se venden solos. Hacelos primero, y las métricas después.

Orden que te propongo:

0. Seguridad + tests cross-tenant
1. Multi-tenant, auth, CRUD, esqueleto de planes
2. Disponibilidad + anti doble-reserva + tests
3. Página fija + reserva + email de confirmación + anti-abuso
4. Agenda admin  →  piloto con el peluquero  (spike MP en paralelo)
5. Mercado Pago (seña)
6a. Plantilla + tema
7a. Recordatorios (email, luego WhatsApp)
6b. Builder con secciones
7b. Métricas
8. Cobro automático de suscripciones + enforcement completo

También agregaría una cosa de negocio: antes de la fase 8, ver el tema legal/fiscal (términos, política de privacidad por los datos de clientes, y cómo facturás tu suscripción). No es código, pero te frena el lanzamiento si lo dejás para el final.

---

**Estado:** incorporado en [roadmap-mvp.md](./roadmap-mvp.md) (fases 0–8, ops, piloto, spike MP, 6a/6b, 7a/7b).