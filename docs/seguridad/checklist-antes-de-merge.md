# Checklist antes de merge

Copiar en descripción de PR o usar como plantilla `.github/pull_request_template.md` cuando exista el repo.

## Datos y tenant

- [ ] ¿Hay query nueva sin `tenant_id`? Si sí → rechazar o marcar `platform` auditado.
- [ ] ¿El cliente puede enviar `tenant_id` / `slug` que el servidor acepta sin validar membership?
- [ ] ¿Test cross-tenant (tenant A vs B) agregado o actualizado?

## AuthZ

- [ ] ¿Ruta nueva tiene auth + rol + tenant?
- [ ] ¿Operación bulk/export/analytics respeta permiso por ítem?

## Público y PII

- [ ] ¿Respuesta pública filtra PII de terceros?
- [ ] ¿`public_code` / tokens con entropía adecuada y rate limit?

## Pagos (si toca MP)

- [ ] Webhook verifica firma.
- [ ] Idempotencia documentada.
- [ ] Sin secretos en diff.

## Front (si toca UI pública o admin)

- [ ] Sin `dangerouslySetInnerHTML` sin sanitizar.
- [ ] URLs de usuario validadas.
- [ ] Cache/query invalidado en logout o cambio tenant.

## Observabilidad

- [ ] Sin PII ni tokens en logs añadidos.
- [ ] Errores al usuario no filtran stack ni SQL.

## Dependencias

- [ ] Lockfile actualizado; sin CVE crítico sin mitigación.

## Documentación

- [ ] Si cambia límite de confianza → actualizar [limites-de-confianza.md](./limites-de-confianza.md) o [patrones-por-modulo.md](./patrones-por-modulo.md).

---

## CI deseable (definir al bootstrap)

| Job | Objetivo |
|-----|----------|
| `pytest` + coverage mínima en `availability`, `booking`, `tenancy` | Regresión aislamiento |
| `ruff` / `mypy` | Calidad y tipos en repos |
| `bandit` o equivalente | Patrones inseguros Python |
| `npm audit` / `pnpm audit` | Front |
| Secret scan (gitleaks, trufflehog) | G1 |
| OpenAPI diff | Rutas nuevas visibles para review |

## Cuándo correr auditoría completa (skill 6 fases)

- Antes del **primer** deploy con datos reales de clientes.
- Después de cambios grandes en `tenancy/`, `booking/router_public`, `payments/webhook`.
- Perfil sugerido: **`standard`** en repo completo; **`deep`** antes de escalar comercialmente.

Comando para el agente (con código en el tree):

```text
Security audit full de E:\mati\programacion\PROYECTOS\TURNOS-SAAS, perfil standard, foco DATA-ISOLATION y WEB-PROTOCOL-AND-AUTH
```
