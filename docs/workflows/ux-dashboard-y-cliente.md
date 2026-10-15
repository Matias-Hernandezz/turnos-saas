# UX — Landing del cliente y dashboard admin

Decisiones de producto acordadas (charla previa a más UI). Implementación visual: **HTML + CSS utilitario** hasta definir diseño final.

## Orden de la landing (cliente)

### Orden recomendado (default)

| # | Sección | Por qué |
|---|---------|--------|
| 1 | **Hero** | Quién es el negocio + CTA principal “Reservar”. |
| 2 | **Servicios** | Mayor intención de compra; cada ítem puede llevar a reserva con servicio preseleccionado. |
| 3 | **Profesionales** | Confianza y elección (cuando hay más de uno). |
| 4 | **Reseñas** | Prueba social; sube conversión después de ver precios/equipo. *(Pro+ si se limita por plan en la página pública.)* |
| 5 | **Nosotros** | Historia y diferenciación. |
| 6 | **Ubicación** | Dirección, mapa, horarios de atención del local (no confundir con slots de reserva). |
| 7 | **FAQ** | Opcional; útil para políticas de cancelación y seña. |
| 8 | **Footer** | Redes, WhatsApp, legal mínimo, CTAs secundarios “Reservar”. |

**Widget de reserva:** siempre disponible (sticky o barra fija) además de los CTAs en hero/servicios/footer.

### Ajustes por rubro (onboarding)

- **Peluquería / barbería:** mantener orden default; servicios muy arriba.
- **Tatuajes / estética visual:** subir **Galería** después de servicios (antes de reseñas).
- **Consultoría / pocos servicios:** hero más largo; servicios puede ser una sola tarjeta.

### Flujo de reserva (objetivo)

```text
CTA "Reservar" → elegir servicio (omitir si vino desde tarjeta de servicio)
  → elegir profesional (**si hay un solo profesional activo, se elige automáticamente** y se salta ese paso)
  → calendario / slots
  → datos cliente
  → pago seña (fase 5 MP; antes: hold 15 min + email)
```

Deep links útiles:

- `/t/{slug}` — landing
- `/t/{slug}/reservar` — paso servicio (o primer paso pendiente)
- `/t/{slug}/reservar?servicio={id}` — salto a profesional/slots
- `/t/{slug}/reserva/{public_code}` — ver / cancelar (ya existe)

## Dashboard admin

### Principio

**Misma estructura de panel en todos los planes** (navegación completa). Lo que cambia por plan es si un apartado está **habilitado**, **solo lectura** o **bloqueado con upgrade** — no un dashboard “recortado” distinto por plan.

### Módulos (visión)

| Módulo | Contenido | Gating típico |
|--------|-----------|----------------|
| **Agenda** | Vista **semana** por defecto; detalle turno; cancelar / estados | Todos los planes |
| **Servicios** | CRUD | Todos |
| **Profesionales** | CRUD; límite `max_professionals` en API | Basic: 1; Pro/Max: según plan |
| **Horarios** | Working hours + bloqueos (cuando existan) | Todos; bloqueos avanzados Pro+ |
| **Clientes** | Ficha, historial, notas | Basic: lista simple; Pro+: ficha completa |
| **Pagos / seña** | Config MP, estado cobros | Pro+ (`can_use_mp`) |
| **Recordatorios** | Plantillas email/WhatsApp | Pro email; Max WhatsApp |
| **Métricas** | Ingresos, ausentismo, etc. | Basic: bloqueado o resumen mínimo; Pro básico; Max completo + export |
| **Sitio web** | Tema, secciones, publicar | Basic: plantilla; Pro: secciones; Max: builder + dominio |
| **Equipo / usuarios** | Invitar staff, roles | Basic: solo owner; Pro+: staff según plan |
| **Plan y facturación** | Plan actual, upgrade | Todos |

UI bloqueada: ítem visible con candado + CTA “Mejorar plan”; API sigue siendo fuente de verdad (`require_feature`, límites en create).

### Usuarios por plan (piloto)

- **Basic:** un owner; un profesional en catálogo.
- **Pro:** varios profesionales; invitación staff (agenda acotada a su recurso cuando aplique).
- **Max:** roles finos, export, dominio, WhatsApp.

Detalle comercial en [planes-ejemplo.md](../planes-ejemplo.md) — actualizar tabla “Dashboard” para reflejar **shell completo + flags**, no “agenda simple” como producto distinto.

## Relación con el roadmap

| Fase | Trabajo UI cliente | Trabajo dashboard |
|------|--------------------|-------------------|
| **0** | — | — |
| **4** | Mantener landing mínima; profundizar flujo solo si hace falta para piloto | **Semana + CRUD turnos** (HTML/CSS) |
| **5** | Paso **pago** en flujo reserva | Pagos / config MP |
| **6a** | Tema + plantilla publicada | Sitio (tema) |
| **6b** | Builder secciones | Editor |
| **7b** | — | Métricas |

El front de reserva (fase 3) puede ir **algo adelantado** respecto a la landing rica; la landing “completa” encaja con **6a/6b**, pero el **orden de secciones y CTAs** de este doc aplica ya al registry y al JSON publicado.

## Referencias

- [dashboard.md](../dashboard.md)
- [pagina-publica-personalizable.md](../pagina-publica-personalizable.md)
- [roadmap-mvp.md](./roadmap-mvp.md)
