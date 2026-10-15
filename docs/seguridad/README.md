# Seguridad — Turnos SaaS

Documentación **previa al código**: límites de confianza, reglas inviolables y checklists. Está alineada con la metodología de la skill [security-audit](https://github.com/cloudflare/security-audit-skill) de Cloudflare (enfoque en **violaciones de límites de confianza**, no en checklists cosméticos).

> **Estado:** diseño / pre-MVP. Cuando exista código, conviene una auditoría completa (6 fases) sobre el repo; hasta entonces esto es el **contrato** que el equipo no puede romper.

## Principio rector

> Un campo `tenant_id` en la base **no es aislamiento**. El aislamiento existe solo si **cada lectura y escritura** pasa por un control que ata recurso + principal + tenant de forma verificable en código y en tests.

## Índice

| Documento | Para qué |
|-----------|----------|
| [limites-de-confianza.md](./limites-de-confianza.md) | Actores, superficies, datos sensibles, flujos |
| [reglas-inviolables.md](./reglas-inviolables.md) | MUST / MUST NOT — ley del proyecto |
| [patrones-por-modulo.md](./patrones-por-modulo.md) | Cómo aplica cada feature de [estructura.md](../estructura.md) |
| [checklist-antes-de-merge.md](./checklist-antes-de-merge.md) | PR, tests de seguridad obligatorios, CI |
| [operaciones-y-despliegue.md](./operaciones-y-despliegue.md) | Secretos, backups, logs, incidentes (owner-observed) |

## Relación con el resto de `docs/`

- [arquitectura-multi-tenant.md](../arquitectura-multi-tenant.md) — modelo de negocio
- [estructura.md](../estructura.md) — carpetas donde viven los controles
- [mercado-pago.md](../mercado-pago.md) — pagos (límite de confianza financiero)

## Severidad (calibración para este producto)

Si algo falla, pensar impacto en datos de **clientes finales** y **negocios**:

| Nivel | Ejemplo en Turnos SaaS |
|-------|-------------------------|
| **Crítico** | Leak o escritura cross-tenant; ejecución remota; takeover de cuenta owner |
| **Alto** | Bypass de auth admin; `public_code` adivinable; webhook MP sin verificación; IDOR en turnos de otro negocio |
| **Medio** | Enumeración de reservas; rate limit ausente en endpoint caro; XSS almacenado en página pública |
| **Bajo / info** | Headers faltantes sin vector real; hardening sin boundary violado |
