# Reglas inviolables

Si una feature no puede cumplir estas reglas, **no se mergea**. Excepciones solo con documento escrito en `docs/seguridad/` y mitigación explícita.

## A. Multi-tenant y acceso a datos

**A1.** Ningún query SQL (ORM o raw) sobre datos de negocio sin predicado de `tenant_id` acotado al contexto actual, salvo rutas **platform** con rol super-admin auditado.

**A2.** Prohibido usar `tenant_id` (o `slug`) del body o query como fuente de verdad; solo `TenancyContext` resuelto en servidor (middleware + membership del usuario).

**A3.** Todo `get_by_id(uuid)` debe ser `get_by_id(uuid, tenant_id)` en el repository base; el servicio no confía en que el ID “ya es del tenant”.

**A4.** Bulk, export, analytics y jobs usan el **mismo** predicado tenant que un GET unitario.

**A5.** Tests obligatorios: al menos dos tenants dummy; ningún test de integración pasa si un usuario de tenant A obtiene 200 con recurso de tenant B.

**A6.** Claves de cache, locks y colas incluyen `tenant_id` (y scope cuando aplique: `appointment_id`, etc.).

## B. Autenticación y autorización

**B1.** Admin API: autenticación en todas las rutas excepto health y assets públicos explícitos.

**B2.** Autenticado ≠ autorizado: cada mutación comprueba rol (owner/staff) **y** pertenencia al tenant del contexto.

**B3.** JWT: algoritmo fijado en código (`HS256` o `RS256`); verificar `exp`, `iss`, `aud`; prohibido `decode` sin verificar firma.

**B4.** Rotar sesión/refrescar tokens en login, cambio de password y revocación de usuario.

**B5.** `public_code` para reservas: generado con CSPRNG; longitud mínima documentada (ej. ≥ 128 bits de entropía efectiva); no usar solo UUID v4 si se expone en URL sin más binding.

**B6.** Rate limiting en login, forgot-password, reserva pública, webhooks y búsqueda de slots (anti-abuso y anti-enumeración).

## C. API pública y reservas (lógica de negocio)

**C1.** Crear turno: transacción atómica hold + slot; rechazar carreras (constraint DB o `SELECT FOR UPDATE`).

**C2.** No exponer en respuestas públicas: IDs internos secuenciales predecibles como único secreto; lista de turnos de un negocio; datos de otros clientes.

**C3.** Errores genéricos en rutas públicas cuando el detalle revelaría existencia de recurso ajeno (balancear UX vs oracle — documentar por endpoint).

**C4.** Idempotency-Key en creación de pago / confirmación cuando el cliente reintente (evitar doble cobro / doble confirmación).

## D. Mercado Pago y dinero

**D1.** Webhooks: verificar firma / secret de MP antes de mutar estado; rechazar si falla.

**D2.** Webhooks idempotentes por `mp_payment_id` (o id externo único); reprocesar no cambia estado dos veces.

**D3.** Tokens OAuth MP: cifrados en reposo; nunca en respuestas API ni front.

**D4.** Separar código y rutas de **pagos del negocio** vs **suscripción al SaaS** (dos webhooks, dos secretos).

**D5.** El monto y `tenant_id` del turno se leen de DB tras correlacionar con preferencia MP; no confiar solo en metadata del callback sin validar.

## E. Entrada, salida e inyección

**E1.** SQL solo parametrizado; prohibido f-string en queries.

**E2.** Pydantic (o equivalente) en **todos** los inputs HTTP; límites de tamaño en JSON de `site_builder`.

**E3.** HTML en JSON del builder: renderizar con escape por defecto; prohibido `dangerouslySetInnerHTML` con contenido de usuario sin sanitizar con allowlist.

**E4.** URLs en theme/links: validar esquema (`https:`); bloquear `javascript:`.

**E5.** Uploads: allowlist de tipos, tamaño máximo, almacenamiento fuera del webroot con URLs firmadas o proxy autenticado.

**E6.** SSRF: si el backend fetcha URLs (preview, import), allowlist de dominios o prohibir en MVP.

## F. Frontend y navegador

**F1.** Tokens admin en memoria o httpOnly cookies — **no** `localStorage` para access token si hay riesgo XSS.

**F2.** CSP en producción para sitio público y admin (al menos baseline); revisar al agregar scripts de terceros.

**F3.** CORS: orígenes explícitos; no reflejar `Origin` arbitrario con credenciales.

**F4.** Al cambiar de cuenta o tenant en el mismo browser, limpiar cache de React Query / estado cliente.

**F5.** Preview del builder no debe servir `draft` en URL pública sin auth.

## G. Secretos, logs y observabilidad

**G1.** Cero secretos en git; `.env.example` sin valores reales.

**G2.** Logs estructurados sin PII completa (teléfono/email truncados o hasheados); nunca JWT, `public_code` completo ni tokens MP.

**G3.** Errores 500 al cliente: mensaje genérico; detalle solo en log server-side.

**G4.** Dependabot o equivalente; `pip audit` / `npm audit` en CI con política de bloqueo para críticos.

## H. Workers y tareas async

**H1.** Payload del job incluye `tenant_id`; el worker revalida que el recurso pertenece a ese tenant antes de actuar.

**H2.** Tareas periódicas (expirar holds, recordatorios) con límites de batch y timeout para no agotar DB.

## I. Privacidad y ciclo de vida

**I1.** Definir retención de datos de clientes y borrado soft/hard; borrado de tenant cascada documentada.

**I2.** Export de datos del negocio solo para owner (o rol explícito) y acotado a su `tenant_id`.

**I3.** Derecho de acceso/borrado del cliente final: flujo documentado (aunque sea manual al inicio).

## J. Definición de “hecho” en seguridad

**J1.** Cada regla A–I relevante al PR tiene test automatizado o ticket `needs_validation` con plan en [operaciones-y-despliegue.md](./operaciones-y-despliegue.md).

**J2.** Nuevos endpoints aparecen en tabla de [patrones-por-modulo.md](./patrones-por-modulo.md) con actor y controles.

---

### Anti-patrones (rechazar en review)

- “Ya filtramos en el router, en el repo no hace falta.”
- “El front manda `tenant_id` y lo guardamos.”
- “Es solo internal/admin, después vemos permisos.”
- “El webhook viene de MP, no hace falta firma en dev” (sin flag explícita y nunca en prod).
- “UUID es secreto suficiente” para capacidades públicas sin rate limit.
