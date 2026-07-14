# Community Food Rescue Platform

A full-stack application for publishing surplus food, reserving quantities and completing pickups before the food expires.

The project has three roles:

- Donor: creates and manages food listings and handles reservation requests.
- Receiver: finds available food and requests a required quantity.
- Admin: manages users, listing visibility and platform statistics.

## Main features

- Registration and login with Flask-Security
- Token-based API authentication
- Donor, receiver and admin authorization
- Complete food-listing CRUD
- Search, filter and pagination
- Quantity and expiry validation
- Reservation approval, rejection, cancellation and collection workflow
- Quantity restoration after approved reservation cancellation
- Review after successful collection
- Role-based dashboards
- Admin moderation and statistics
- Celery and Redis task for expiring old listings
- Pytest API tests

## Technology used

- Flask
- Flask-SQLAlchemy
- Flask-Security-Too
- SQLite
- VueJS 2
- Vue Router
- Axios
- Bootstrap 5
- Celery and Redis

The Vue application is loaded through CDN scripts and served by Flask, so Node.js and npm are not required.

## Project structure

```text
community-food-rescue-platform/
├── backend/
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── listings.py
│   │   └── reservations.py
│   ├── tests/
│   │   └── test_api.py
│   ├── app.py
│   ├── celery_worker.py
│   ├── config.py
│   ├── create_db.py
│   ├── extensions.py
│   ├── models.py
│   ├── requirements.txt
│   ├── security_setup.py
│   └── tasks.py
├── frontend/
│   ├── css/style.css
│   ├── js/components/
│   ├── js/api.js
│   ├── js/app.js
│   └── index.html
├── docs/screenshots/
├── .gitignore
├── GITHUB_4_DAY_PLAN.md
└── README.md
```

## Installation on Windows

Open the project folder in VS Code and open a terminal.

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
cd backend
python create_db.py
python app.py
```

Open `http://127.0.0.1:5000`.

For Git Bash, activate the environment with:

```bash
source .venv/Scripts/activate
```

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@foodrescue.com | admin123 |
| Donor | donor@foodrescue.com | donor123 |
| Receiver | receiver@foodrescue.com | receiver123 |

Running `python create_db.py` creates these accounts and sample listings. Running it again does not duplicate the seed records.

## Authentication

Login returns an access token. Protected requests send it in this header:

```text
Authentication-Token: <token>
```

Example login:

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"donor@foodrescue.com","password":"donor123"}'
```

## API documentation

### Authentication

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register as donor or receiver |
| POST | `/api/auth/login` | Public | Login and receive token |
| GET | `/api/auth/me` | Authenticated | Current user details |
| PUT | `/api/auth/profile` | Authenticated | Update profile |
| POST | `/api/auth/logout` | Authenticated | Invalidate current token |

### Listings

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/listings` | Public | Search active listings |
| GET | `/api/listings/mine` | Donor | List own listings |
| GET | `/api/listings/<id>` | Public | Listing details |
| POST | `/api/listings` | Donor | Create listing |
| PUT | `/api/listings/<id>` | Owner/Admin | Update listing |
| DELETE | `/api/listings/<id>` | Owner/Admin | Delete listing without history |
| PATCH | `/api/listings/<id>/status` | Owner/Admin | Publish, close, hide or expire |

Supported list query parameters include `keyword`, `food_type`, `dietary_tag`, `location`, `page` and `per_page`.

### Reservations and reviews

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/listings/<id>/reservations` | Receiver | Request quantity |
| GET | `/api/reservations/mine` | Authenticated | Current user's reservations |
| GET | `/api/reservations/<id>` | Participant/Admin | Reservation details |
| PATCH | `/api/reservations/<id>/approve` | Listing owner | Approve and deduct quantity |
| PATCH | `/api/reservations/<id>/reject` | Listing owner | Reject request |
| PATCH | `/api/reservations/<id>/cancel` | Participant/Admin | Cancel permitted request |
| PATCH | `/api/reservations/<id>/collect` | Listing owner/Admin | Mark pickup collected |
| POST | `/api/reservations/<id>/reviews` | Participant | Review after collection |

### Dashboard and administration

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/dashboard` | Authenticated | Role-specific dashboard |
| GET | `/api/admin/users` | Admin | List users |
| PATCH | `/api/admin/users/<id>/active` | Admin | Block or reactivate user |
| GET | `/api/admin/listings` | Admin | List all listings |
| PATCH | `/api/admin/listings/<id>/visibility` | Admin | Hide or restore listing |
| GET | `/api/admin/statistics` | Admin | Platform statistics |

## Important workflow rules

- A published listing must have a future expiry time.
- A receiver cannot reserve their own listing.
- Requested quantity must be positive and within current availability.
- Stock is reduced only when the donor approves a request.
- Cancelling an approved request restores its quantity.
- A listing with reservation history is closed or hidden instead of deleted.
- Reviews are accepted only after collection.

## Running tests

```powershell
cd backend
pytest -q
```

## Optional Celery and Redis setup

Start Redis with Docker:

```powershell
docker run -d --name food-rescue-redis -p 6379:6379 redis:7
```

Open two terminals in the `backend` folder.

Worker:

```powershell
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

Scheduler:

```powershell
celery -A celery_worker.celery beat --loglevel=info
```

The scheduled task changes active listings to `EXPIRED` after their expiry time.

## Screenshots

Add final screenshots inside `docs/screenshots` before submission:

- Home and browse page
- Donor dashboard
- Receiver reservations
- Admin dashboard

## Submission checklist

- Replace development secret values with environment variables for deployment.
- Test all three demo roles.
- Add screenshots.
- Confirm the repository is public.
- Confirm the database, virtual environment and cache files are not committed.
- Follow `GITHUB_4_DAY_PLAN.md` for genuine staged commits.
