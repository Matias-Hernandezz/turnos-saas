# Página pública personalizable

La página que ve el cliente final **no es código por negocio**: es **configuración en JSON** que el front interpreta y renderiza.

## Tres capas (de menor a mayor flexibilidad)

### 1. Plantilla base

Conjunto inicial pequeño (ej. 3–6): **Minimal**, **Elegante**, **Bold**, etc.

- El negocio elige una plantilla → página usable en un clic.
- Define layout base y estilos por defecto.

### 2. Tema (design tokens)

Se aplican vía **CSS variables** (pocos inputs, gran impacto visual):

- Colores (primario, fondo, etc.)
- Tipografía
- Radio de bordes
- Estilo de botones
- Logo e imagen de portada

### 3. Secciones reordenables

Bloques predefinidos: activar/desactivar y **ordenar** (drag & drop en el editor).

| Sección | Descripción |
|---------|-------------|
| `hero` | Portada + CTA “Reservar” |
| `services` | Servicios con precio y duración |
| `team` | Profesionales |
| `gallery` | Trabajos / portfolio |
| `reviews` | Reseñas |
| `location` | Ubicación, horarios, mapa |
| `faq` | Preguntas frecuentes |
| `social` | Redes / WhatsApp |
| Widget de reserva | Siempre presente; **no eliminable** |

Según el **rubro** en onboarding se pueden precargar secciones y contenidos de ejemplo (ej. tatuajes → galería prominente; peluquería → servicios y precios).

## Esquema JSON (ejemplo)

```json
{
  "template": "elegante",
  "theme": {
    "primary": "#C9A24B",
    "background": "#0F0F0F",
    "font": "Playfair Display",
    "radius": "lg",
    "logo_url": "..."
  },
  "sections": [
    {
      "type": "hero",
      "enabled": true,
      "props": {
        "title": "Lauti Barber",
        "cta": "Reservá tu turno",
        "image": "..."
      }
    },
    { "type": "services", "enabled": true },
    {
      "type": "gallery",
      "enabled": true,
      "props": { "images": [] }
    },
    { "type": "location", "enabled": false }
  ]
}
```

## Implementación en React

**Registry de componentes**:

```text
{ hero: Hero, services: Services, gallery: Gallery, ... }
```

Render:

```text
sections
  .filter(s => s.enabled)
  .map(s => <Registry[s.type] key={...} {...s.props} />)
```

Agregar una sección nueva = **nuevo componente + entrada en el registry**; no hace falta tocar el resto del sistema.

## Borrador vs publicado

- `draft_config`: lo que edita el negocio en el panel.
- `published_config`: lo que ve el público tras pulsar **Publicar**.

Evita romper la página en producción mientras se experimenta.

## Filosofía de diseño

**Límites a propósito**: menos libertad que un CMS genérico → menos soporte, páginas más consistentes y profesionales.

Textos e imágenes **placeholder** por defecto para que nunca se vea una página vacía en el primer acceso.

## Planes y alcance del builder

La profundidad del editor (solo logo/colores vs secciones vs dominio) se alinea con planes de referencia en [planes-ejemplo.md](./planes-ejemplo.md) — sujetos a cambio.
