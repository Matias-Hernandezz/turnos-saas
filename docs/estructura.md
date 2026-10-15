turnos-saas/
├── docker-compose.yml          # postgres + backend + frontend
├── .env.example
├── README.md
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── availability/
│   │   ├── booking/
│   │   └── payments/
│   └── src/
│       ├── main.py                     # crea la app, monta routers, middlewares
│       │
│       ├── core/
│       │   ├── config.py               # Settings (pydantic-settings)
│       │   ├── database.py             # engine, session
│       │   ├── security.py             # hash de passwords, JWT
│       │   ├── crypto.py               # Fernet para tokens de MP
│       │   ├── unit_of_work.py         # UoW base
│       │   ├── base_repository.py      # repo base, SIEMPRE filtra por tenant_id
│       │   ├── exceptions.py
│       │   └── pagination.py
│       │
│       ├── tenancy/
│       │   ├── middleware.py           # resuelve tenant por slug / subdominio / dominio propio
│       │   ├── dependencies.py         # get_current_tenant, require_feature("online_payments")
│       │   └── plan_limits.py          # chequeo de límites por plan (feature flags)
│       │
│       ├── features/
│       │   ├── auth/
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── schemas.py
│       │   │   └── dependencies.py     # get_current_user, roles
│       │   │
│       │   ├── tenants/                # alta de negocio, onboarding, settings
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── schemas.py
│       │   │   └── presets.py          # RUBRO_PRESETS (lo que hoy está en seed.py)
│       │   │
│       │   ├── catalog/                # servicios + profesionales
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── availability/           # EL CORAZÓN
│       │   │   ├── router.py           # GET /slots?service=&professional=&date=
│       │   │   ├── service.py
│       │   │   ├── slot_calculator.py  # función pura, sin DB, 100% testeable
│       │   │   ├── repository.py       # working hours, time off
│       │   │   └── schemas.py
│       │   │
│       │   ├── booking/                # turnos
│       │   │   ├── router_public.py    # reservar, ver y cancelar con public_code
│       │   │   ├── router_admin.py     # CRUD del dashboard
│       │   │   ├── service.py          # crear con hold, confirmar, cancelar
│       │   │   ├── repository.py
│       │   │   ├── schemas.py
│       │   │   └── jobs.py             # expirar holds vencidos
│       │   │
│       │   ├── customers/
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── payments/               # Mercado Pago del negocio (seña)
│       │   │   ├── router.py           # crear preferencia, oauth callback
│       │   │   ├── webhook.py          # idempotente por mp_payment_id
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── mp_client.py        # wrapper de la API de MP
│       │   │   └── schemas.py
│       │   │
│       │   ├── subscriptions/          # lo que el negocio te paga a vos
│       │   │   ├── router.py
│       │   │   ├── webhook.py
│       │   │   ├── service.py
│       │   │   └── mp_client.py
│       │   │
│       │   ├── site_builder/           # personalización de la página
│       │   │   ├── router_admin.py     # GET/PUT draft, publish, templates
│       │   │   ├── router_public.py    # GET /public/{slug}/site (published)
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── schemas.py          # validación Pydantic del JSON (secciones y tema)
│       │   │   ├── templates.py        # plantillas base
│       │   │   └── media.py            # upload de imágenes
│       │   │
│       │   ├── analytics/              # métricas del dashboard
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   └── queries.py          # SQL de agregados
│       │   │
│       │   ├── notifications/          # recordatorios
│       │   │   ├── service.py
│       │   │   ├── email.py
│       │   │   ├── whatsapp.py
│       │   │   └── jobs.py
│       │   │
│       │   └── reviews/
│       │       ├── router.py
│       │       ├── service.py
│       │       └── repository.py
│       │
│       ├── models/                     # SQLModel (lo que ya tenés en models.py, un archivo por entidad)
│       │   ├── __init__.py             # importa todo para metadata/alembic
│       │   ├── plan.py
│       │   ├── tenant.py
│       │   ├── user.py
│       │   ├── catalog.py
│       │   ├── availability.py
│       │   ├── customer.py
│       │   ├── appointment.py
│       │   ├── payment.py
│       │   ├── page_config.py
│       │   └── review.py
│       │
│       └── workers/
│           ├── scheduler.py            # APScheduler o Celery beat
│           └── tasks.py                # expirar holds, enviar recordatorios
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── app/
        │   ├── router.tsx              # rutas: público / admin / super-admin
        │   ├── providers.tsx           # React Query, theme, auth
        │   └── layouts/
        │       ├── PublicLayout.tsx
        │       └── AdminLayout.tsx
        │
        ├── shared/
        │   ├── api/
        │   │   ├── client.ts           # axios/fetch + interceptors
        │   │   └── types.ts
        │   ├── ui/                     # Button, Modal, Input, Calendar...
        │   ├── hooks/
        │   └── lib/                    # formatters, fechas, dinero
        │
        ├── features/
        │   ├── auth/
        │   ├── onboarding/             # wizard: rubro → nombre y logo → plantilla → servicios
        │   ├── catalog/                # ABM de servicios y profesionales
        │   ├── availability/           # editor de horarios y bloqueos
        │   ├── bookings-admin/         # agenda (calendario drag & drop) + CRUD
        │   ├── customers/
        │   ├── payments-settings/      # conectar cuenta de Mercado Pago
        │   ├── analytics/              # dashboard con gráficos
        │   ├── billing/                # tu plan, upgrade, facturas
        │   │
        │   ├── site-builder/           # EL EDITOR
        │   │   ├── BuilderPage.tsx     # layout dividido: panel + preview
        │   │   ├── panels/
        │   │   │   ├── TemplatePicker.tsx
        │   │   │   ├── ThemePanel.tsx          # colores, fuentes, radius
        │   │   │   ├── SectionsPanel.tsx       # reordenar / activar (dnd-kit)
        │   │   │   └── SectionEditor.tsx       # form según el tipo de sección
        │   │   ├── preview/
        │   │   │   ├── PreviewFrame.tsx        # toggle móvil/desktop
        │   │   │   └── usePreviewSync.ts       # draft en vivo, sin guardar
        │   │   ├── store.ts                    # estado del draft (zustand)
        │   │   └── api.ts
        │   │
        │   └── public-site/            # LO QUE VE EL CLIENTE FINAL
        │       ├── PublicSitePage.tsx  # lee el JSON y renderiza
        │       ├── registry.ts         # { hero: Hero, services: Services, ... }
        │       ├── theme/
        │       │   └── applyTheme.ts   # JSON del tema → CSS variables
        │       ├── sections/
        │       │   ├── Hero.tsx
        │       │   ├── Services.tsx
        │       │   ├── Team.tsx
        │       │   ├── Gallery.tsx
        │       │   ├── Reviews.tsx
        │       │   ├── Location.tsx
        │       │   └── Faq.tsx
        │       └── booking/            # widget de reserva (siempre presente)
        │           ├── BookingWidget.tsx
        │           ├── steps/          # servicio → profesional → fecha/hora → datos → pago
        │           └── useBookingFlow.ts
        │
        └── types/                      # tipos generados desde el OpenAPI del backend