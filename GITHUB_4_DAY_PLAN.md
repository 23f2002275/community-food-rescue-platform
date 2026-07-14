# Four-Day GitHub Commit Plan

Use this as a genuine four-day development plan. Make each commit on the day the work is completed. Do not change system dates, backdate commits or manufacture contribution history.

Before Day 1, create an empty public repository named `community-food-rescue-platform` on GitHub. Do not add a GitHub README or `.gitignore` while creating it.

Open this extracted folder in VS Code and run:

```bash
git init
git branch -M main
git remote add origin https://github.com/23f2002275/community-food-rescue-platform.git
git config user.name "Pratham Bhardwaj"
git config user.email "23f2002275@ds.study.iitm.ac.in"
```

## Day 1: Project setup, database and authentication

Files:

```text
.gitignore
backend/app.py
backend/config.py
backend/extensions.py
backend/models.py
backend/security_setup.py
backend/create_db.py
backend/requirements.txt
backend/routes/__init__.py
backend/routes/auth.py
frontend/index.html
frontend/css/style.css
frontend/js/api.js
frontend/js/components/Home.js
frontend/js/components/Login.js
frontend/js/components/Register.js
```

Commands:

```bash
git add .gitignore backend/app.py backend/config.py backend/extensions.py backend/models.py backend/security_setup.py backend/create_db.py backend/requirements.txt backend/routes/__init__.py backend/routes/auth.py frontend/index.html frontend/css/style.css frontend/js/api.js frontend/js/components/Home.js frontend/js/components/Login.js frontend/js/components/Register.js
git commit -m "set up project and user authentication"
git push -u origin main
```

Verify registration, login, logout and `/api/auth/me` before committing.

## Day 2: Food listing CRUD and browse interface

Files:

```text
backend/routes/listings.py
frontend/js/components/Listings.js
frontend/js/components/ListingDetails.js
frontend/js/components/ManageListing.js
frontend/js/components/MyListings.js
frontend/js/app.js
```

Commands:

```bash
git add backend/routes/listings.py frontend/js/components/Listings.js frontend/js/components/ListingDetails.js frontend/js/components/ManageListing.js frontend/js/components/MyListings.js frontend/js/app.js
git commit -m "add food listing crud and search"
git push
```

Verify create, edit, delete, filter, pagination and listing status actions.

## Day 3: Reservation workflow, dashboards and admin pages

Files:

```text
backend/routes/reservations.py
backend/routes/dashboard.py
backend/routes/admin.py
frontend/js/components/Reservations.js
frontend/js/components/Dashboard.js
frontend/js/components/AdminDashboard.js
```

Commands:

```bash
git add backend/routes/reservations.py backend/routes/dashboard.py backend/routes/admin.py frontend/js/components/Reservations.js frontend/js/components/Dashboard.js frontend/js/components/AdminDashboard.js
git commit -m "complete reservation and moderation workflow"
git push
```

Verify approval reduces quantity, approved cancellation restores quantity, collection works and reviews require collection.

## Day 4: Background task, tests and documentation

Files:

```text
backend/celery_worker.py
backend/tasks.py
backend/tests/test_api.py
docs/screenshots/.gitkeep
README.md
GITHUB_4_DAY_PLAN.md
```

Commands:

```bash
git add backend/celery_worker.py backend/tasks.py backend/tests/test_api.py docs/screenshots/.gitkeep README.md GITHUB_4_DAY_PLAN.md
git commit -m "add expiry job tests and documentation"
git push
```

Run `pytest -q`, add your own screenshots and make one final small commit when the screenshots are ready:

```bash
git add docs/screenshots
git commit -m "add project screenshots"
git push
```

## Daily working pattern

Use this small cycle each day:

```bash
git status
git diff
python -m compileall backend
cd backend && pytest -q && cd ..
git add <files completed today>
git commit -m "clear description of today's work"
git push
```
