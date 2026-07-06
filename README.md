# booking-api

> 📌 **Portfolio project** — built as a demonstration for recruiters and technical reviewers.
> Live demo available, see [Web Interface — Live Demo](#web-interface--live-demo) below.

Multi-tenant booking platform built with Django REST Framework and an htmx web frontend.
Providers create services and time slots. Clients browse and book appointments.
Both a full REST API and a server-rendered web interface run on the same Django project.

---

## Web Interface — Live Demo

**[booking-api-production-51cd.up.railway.app](https://booking-api-production-51cd.up.railway.app)**

> ⚠️ The demo database may be reset periodically.

| Role       | Username        | Password       |
|------------|-----------------|----------------|
| Provider   | `testprovider`  | `testpassword` |
| Provider 2 | `testprovider2` | `testpassword` |
| Client     | `testclient`    | `testpassword` |

- **testclient** — browse services, book slots, view and cancel own bookings
- **testprovider** / **testprovider2** — view incoming bookings, confirm or cancel them

The database is pre-seeded with 3 services and bookable slots over the next 2 days.
The two providers demonstrate multi-tenant isolation — each sees only their own services and bookings.

> ⚠️ Service and Slot creation is only available via API in this version.

### Browsable API

Log in at [/api/auth/login/](https://booking-api-production-51cd.up.railway.app/api/auth/login/)
with the demo credentials above, then navigate to any endpoint below.

**Auth**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/client/ | Register as client |
| POST | /api/auth/register/provider/ | Register as provider |
| POST | /api/auth/login/ | Get JWT token pair |
| POST | /api/auth/token/refresh/ | Refresh access token |

**Services** *(providers: own only / clients: all active)*
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/services/ | List services |
| POST | /api/services/ | Create service *(provider only)* |
| GET | /api/services/{id}/ | Service detail |
| PATCH | /api/services/{id}/ | Update service *(owner only)* |
| DELETE | /api/services/{id}/ | Delete service *(owner only, blocked if bookings exist)* |

**Slots** *(providers: own only / clients: available only)*
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/slots/ | List slots |
| POST | /api/slots/ | Create slot *(provider only)* |
| GET | /api/slots/{id}/ | Slot detail |
| PATCH | /api/slots/{id}/ | Update slot *(owner only, blocked if booked)* |
| DELETE | /api/slots/{id}/ | Delete slot *(owner only, blocked if booked)* |

**Bookings** *(providers: on own slots / clients: own only)*
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/bookings/ | List bookings |
| POST | /api/bookings/ | Create booking *(client only)* |
| GET | /api/bookings/{id}/ | Booking detail |
| POST | /api/bookings/{id}/confirm/ | Confirm booking *(provider only)* |
| POST | /api/bookings/{id}/cancel/ | Cancel booking *(provider or client)* |

**Query Filters**
| Endpoint | Parameter | Example | Description |
|----------|-----------|---------|-------------|
| /api/services/ | is_active | ?is_active=false | Filter by active status |
| /api/slots/ | service | ?service=1 | Filter by service |
| /api/slots/ | start_date | ?start_date=2026-07-01 | Filter by date |
| /api/slots/ | is_booked | ?is_booked=true | Filter by availability |
| /api/bookings/ | status | ?status=pending | Filter by booking status |

### Postman

Use JWT — send `POST /api/auth/login/` to get tokens, then authorize all requests with `Bearer {{access_token}}`.

| Variable | Value |
|----------|-------|
| `base_url` | `https://booking-api-production-51cd.up.railway.app` |
| `access_token` | *(fill after login)* |
| `refresh_token` | *(fill after login)* |

Copy the tokens from the login response into `access_token` and `refresh_token`.
All requests use `Bearer {{access_token}}` via the collection Authorization tab.

> 💡 You can use a Postman post-response script to automate token saving.

---

## Tech Stack

**Backend / API**
- Python 3.12, Django 6.0, Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Role-based permissions — custom IsProvider, IsClient, IsSlotOwner
- django-filter — query parameter filtering
- PostgreSQL (production) / SQLite (development)

**Web frontend**
- htmx — server-driven partial updates, no JavaScript written by hand
- Pico CSS — minimal classless CSS framework
- Django session authentication (independent of the JWT API)

**Infrastructure**
- Docker + Nginx (local development)
- Deployed on Railway

---

## Architecture

Multi-tenant: single database, multiple independent providers.
Each provider manages their own services and slots. Data isolation is enforced
via queryset filtering — cross-provider access returns 404, not 403.

**Roles**
- **Provider** — creates services and slots, views and manages own bookings
- **Client** — browses active services and available slots, creates bookings

**Data model**
- **Service** — something a provider offers, e.g. a haircut (name, description, duration, active flag)
- **Slot** — a specific time window when a service can be booked (start/end time, price, availability)
- **Booking** — a client's reservation of a slot (status: pending / confirmed / cancelled)

**Booking flow**
1. Client books an available slot → status `PENDING`, slot marked as booked
2. Provider confirms → status `CONFIRMED`
3. Either party cancels → status `CANCELLED`, slot released

---

## Security & Concurrency
- JWT authentication required for all API endpoints; session auth for the web interface
- Role-based access: providers and clients have distinct permissions on every endpoint
- Data isolation via queryset filtering — cross-user access returns 404, not 403
- Slot double-booking prevented with `select_for_update()` row-level locking inside
  `transaction.atomic()` — API and web share the same service layer, lock applied on every write path

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Models — CustomUser, Service, Slot, Booking | ✅ |
| 2 | JWT Authentication with role-based registration | ✅ |
| 3 | Role-based permissions — IsProvider, IsClient, IsSlotOwner | ✅ |
| 4 | Services and Slots — ViewSets, serializers, business logic | ✅ |
| 5 | Bookings — ViewSet, confirm/cancel actions, slot state management | ✅ |
| 6 | 31 automated tests — auth, services, slots, bookings | ✅ |
| 7 | django-filter — query parameter filtering | ✅ |
| 8 | Docker local environment — Django + PostgreSQL + Nginx | ✅ |
| 9 | Deploy on Railway with PostgreSQL | ✅ |
| 10 | Web frontend — htmx + Pico CSS, client and provider flows | ✅ |
| 11 | Concurrency — service layer with select_for_update, race condition eliminated | ✅ |

---

## Future Improvements

Documented as the production roadmap — intentionally out of scope for this version.

- **Email notifications** — async booking confirm/cancel emails (Celery + Redis worker, SMTP backend).
- **Full user registration** — email verification and password reset.

---

## Local Setup

**Standard**
```bash
git clone https://github.com/matteo-cremonini/booking-api
cd booking-api
cp .env.example .env   # fill in your values
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

**Docker**
```bash
cp .env.example .env   # fill in your values
docker compose up --build
```

Runs Django + PostgreSQL + Nginx. API available at `http://localhost`.

---

## Running Tests
```bash
docker compose exec web python manage.py test
```

---

## Seed Demo Data

Populates the database with the demo accounts and data shown in
[Web Interface — Live Demo](#web-interface--live-demo). Idempotent — safe to re-run.

**Local (Docker)**
```bash
docker compose exec web python manage.py seed_demo
```

**Railway (production)**

`railway run` can't reach the internal database host, so load the public URL inside a shell:
```bash
railway shell --service Postgres
export DATABASE_URL="$DATABASE_PUBLIC_URL"
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py seed_demo
```
