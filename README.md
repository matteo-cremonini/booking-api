# booking-api

> 📌 **Portfolio project** — built as a demonstration for recruiters and technical reviewers.
> Live demo available, see [Live Demo](#live-demo) below.

Multi-tenant booking REST API built with Django REST Framework.
Providers create services and time slots. Clients browse and book appointments.

---

## Live Demo

**Base URL:** `https://[URL-RAILWAY]`

> ⚠️ The demo database may be reset periodically.

### Try it in the browser — Browsable API

1. Open [/api-auth/login/](https://[URL-RAILWAY]/api-auth/login/)
2. Log in with one of the demo credentials below
3. Navigate to any endpoint and interact directly from the browser

**Provider account**
| Field | Value |
|-------|-------|
| Username | `provider_demo` |
| Password | `demo1234` |

**Client account**
| Field | Value |
|-------|-------|
| Username | `client_demo` |
| Password | `demo1234` |

### Try it with Postman

**Environment setup**

| Variable | Value |
|----------|-------|
| `base_url` | `https://[URL-RAILWAY]` |
| `access_token` | *(fill after login)* |
| `refresh_token` | *(fill after login)* |

**Authentication**

Set `base_url`, then send `POST /api/auth/login/` with the demo credentials.
Copy the tokens from the response into `access_token` and `refresh_token`.
All requests use `Bearer {{access_token}}` via the collection Authorization tab.

> 💡 You can use a Postman post-response script to automate token saving.

---

## Tech Stack
- Python 3.12
- Django 6.0
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Role-based permissions — custom IsProvider, IsClient, IsSlotOwner
- django-filter — query parameter filtering
- PostgreSQL (production) / SQLite (development)
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

**Booking flow**
1. Client books an available slot → status `PENDING`, slot marked as booked
2. Provider confirms → status `CONFIRMED`
3. Either party cancels → status `CANCELLED`, slot released

---

## Models
- **Service** — a bookable offering (name, description, duration, active flag) owned by a provider
- **Slot** — a time window for a service (start/end time, price, booked flag)
- **Booking** — a client's reservation of a slot (status: pending / confirmed / cancelled)

---

## Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/client/ | Register as client |
| POST | /api/auth/register/provider/ | Register as provider |
| POST | /api/auth/login/ | Get JWT token pair |
| POST | /api/auth/token/refresh/ | Refresh access token |

---

## API Endpoints

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

---

## Query Filters
| Endpoint | Parameter | Example | Description |
|----------|-----------|---------|-------------|
| /api/services/ | is_active | ?is_active=false | Filter by active status |
| /api/slots/ | service | ?service=1 | Filter by service |
| /api/slots/ | start_date | ?start_date=2026-07-01 | Filter by date |
| /api/slots/ | is_booked | ?is_booked=true | Filter by availability |
| /api/bookings/ | status | ?status=pending | Filter by booking status |

---

## Security
- JWT authentication required for all endpoints
- Role-based access: providers and clients have distinct permissions on every endpoint
- Data isolation via queryset filtering — cross-user access returns 404, not 403
- Slot double-booking prevented at serializer validation level

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
python manage.py test
```
