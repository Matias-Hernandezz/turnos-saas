# UX del editor de página

Objetivo: que un dueño de negocio sin conocimientos técnicos pueda dejar su página presentable y publicarla sin miedo.

## Layout del editor

- **Izquierda**: panel de edición (plantilla, tema, secciones, textos, imágenes).
- **Derecha**: **preview en vivo** (iframe o el mismo árbol de componentes en modo `preview`).
- **Toggle móvil / desktop**: la mayoría de las reservas llegan desde el celular; el preview debe reflejarlo.

## Onboarding guiado (wizard)

Al registrarse, flujo sugerido en ~4 pasos:

1. **Rubro** (peluquería, barbería, tatuajes, etc.)
2. **Nombre y logo**
3. **Elegir plantilla**
4. **Cargar servicios** (con sugerencias según rubro)

El rubro alimenta:

- Servicios de ejemplo precargados
- Secciones activas por defecto y orden sugerido
- Copy e imágenes placeholder coherentes

## Publicación

- Edición sobre `draft_config`.
- Botón **Publicar** copia o promociona a `published_config`.
- Opcional: vista previa con URL de borrador solo para el admin.

## Principios UX

| Principio | Implementación |
|-----------|----------------|
| Nunca vacío | Defaults por rubro y plantilla |
| No romper diseño | Controles acotados (tokens + secciones fijas) |
| Confianza | Preview instantáneo y modo móvil |
| Menos soporte | Menos opciones “libres” que un page builder genérico |

## Relación con el roadmap

El **builder completo** (plantillas → tema → secciones) viene **después** del MVP de reservas y página fija. Ver [roadmap-mvp.md](./roadmap-mvp.md).
