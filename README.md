# 💈 BarberBook — Barbershop Reservation Platform

A full-stack Django reservation system for barbershops. Customers pick a service, choose a barber, and lock in a time slot from a live 15-minute availability grid. Owners run the shop from a dedicated admin console — managing services, barbers, working hours, days off and appointment statuses.

## ✨ Features

- **JWT authentication** with three roles: `customer`, `barber`, `admin`
- **Service catalog** — name, category (haircut/beard/shave/combo/kids/styling), price, duration
- **Barber roster** — each barber has working hours, days off, a specialty, a rating and a list of services they personally offer
- **Smart booking system** with server-side validation:
  - ❌ Two bookings of the same barber cannot overlap
  - ❌ Past dates are blocked (with 5-min clock-skew tolerance)
  - ❌ Cannot book a barber on their day off
  - ❌ Appointment cannot start before opening or end after closing
  - ❌ Cannot book a barber for a service they don't offer
  - ❌ Inactive barbers or services cannot be booked
  - ✅ `end_time` auto-derived from `service.duration_minutes`
  - ✅ `total_price` auto-set from the service price
- **Dynamic 15-min slot generator** — `/api/barbers/:id/slots?date=&service=` returns every possible slot for that day, each marked available/unavailable. The booking UI greys out blocked slots in real time.
- **Customer dashboard** — upcoming/past tabs, in-place cancel
- **Admin dashboard** — KPIs, appointment approval flow, fleet+barber CRUD, top-barber + top-service analytics
- **Classic barbershop UI** — charcoal + ivory + gold palette, Playfair Display headings, decorative barber-pole stripe

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0 |
| API | Django REST Framework |
| Auth | djangorestframework-simplejwt (JWT) |
| Database | SQLite (swap to PostgreSQL via `DATABASES`) |
| Frontend | Server-rendered HTML templates + vanilla JS (no build step) |
| Styling | Custom CSS design system |
| CORS | django-cors-headers |

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed           # creates demo data
python manage.py runserver
```

Visit **http://localhost:8000** and log in with:

- **Admin** → `admin` / `admin123` — runs the shop
- **Customer** → `demo` / `demo1234` — books appointments

## 📁 Project Structure

```
barberbook/
├── barberbook/             # Project settings + URL routing
├── accounts/               # Custom User model + JWT auth endpoints
│   └── models.py           # User(role=customer|barber|admin)
├── services/               # Service catalog + Barber roster
│   ├── models.py           # Service, Barber (with M2M services)
│   └── management/commands/seed.py
├── bookings/               # Appointment booking engine (the heart)
│   ├── models.py           # Appointment with full validation logic
│   ├── serializers.py
│   ├── permissions.py      # IsOwnerBarberOrAdmin
│   └── views.py            # ViewSet + admin + slot generator
├── templates/              # 9 server-rendered pages
├── static/
│   ├── css/styles.css      # Charcoal-gold-ivory design system
│   └── js/{api.js,app.js}
└── manage.py
```

## 🔌 API Reference

All endpoints prefixed with `/api`. Protected endpoints require `Authorization: Bearer <access>`.

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new customer |
| POST | `/auth/login` | Get JWT pair |
| POST | `/auth/logout` | Blacklist refresh token |
| GET/PATCH | `/auth/me` | Get / update profile |

### Services
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/services/` (filter: `?category=` `?active=true` `?search=`) | Public |
| GET | `/services/{id}/` | Public |
| POST / PUT / DELETE | `/services/[/{id}/]` | Admin |

### Barbers
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/barbers/` (filter: `?service=` `?active=true` `?search=`) | List | Public |
| GET | `/barbers/{id}/` | Detail with services & hours | Public |
| POST / PUT / DELETE | `/barbers/[/{id}/]` | CRUD | Admin |
| GET | `/barbers/{id}/busy?date=YYYY-MM-DD` | Existing pending+confirmed appts | Public |
| GET | `/barbers/{id}/slots?date=&service=` | **Slot generator** | Public |

### Appointments
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/appointments/` (filter: `?status=` `?date=` `?barber=` `?service=`) | User |
| POST | `/appointments/` | User |
| GET / PUT / DELETE | `/appointments/{id}/` | Owner/Barber/Admin |
| POST | `/appointments/{id}/cancel/` | Owner/Barber/Admin |

### Admin
| Method | Endpoint |
|--------|----------|
| GET | `/admin/appointments` |
| PATCH | `/admin/appointments/{id}/status` — body `{"status":"confirmed\|rejected\|completed\|no_show"}` |
| GET | `/admin/stats` — KPIs + top barbers + top services |

## 🧪 Validation Tested End-to-End

```json
// Overlap on the same barber
{ "start_time": ["This barber is already booked during that time slot."] }

// Past date
{ "appointment_date": ["Cannot book a slot in the past."] }

// Day off
{ "appointment_date": ["Marcus \"The Razor\" Hill is off on this day."] }

// Outside working hours
{ "start_time": ["This appointment would end after Marcus's closing time (19:00)."] }

// Service not offered by the barber
{ "service": ["Jamie Park does not offer this service."] }
```

## 🎨 Design Notes

The UI uses a hand-crafted classic-barbershop palette — charcoal `#14110f`, ivory `#fffaf0`, gold `#c9a24a`, crimson stripe accents — with **Playfair Display** for headings and **Inter** for body. The thin striped bar at the top of every page is a CSS-only homage to the spinning barber pole. The booking page is a true multi-step wizard: pick service → barber list re-filters → date → slot grid recomputes live as you change anything upstream.

## 🚧 Optional Enhancements (Roadmap)

- Online payment integration (Stripe/Square) — `Payment` model is the natural next step
- SMS / email confirmation on status change
- Loyalty: repeat-customer discount, "10th cut free" counter
- Barber portal — barbers see their own schedule (the permission class already supports this)
- Walk-in queue mode for in-shop iPad
- Reviews & star ratings per appointment
- Multi-shop / multi-location support

## 📄 License

MIT — built as a Django learning showcase.
