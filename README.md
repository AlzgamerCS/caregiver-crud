# Caregiver job board and ORM lab

This project started as coursework for CSCI 341 Database Systems at Nazarbayev University. A member posts a job, a caregiver applies, and the member accepts the application and schedules an appointment. An applicant-count report demonstrates a join and aggregation.

Each implementation has its own models, database connection, dependencies, and entry point. Run either one independently.

| | Django app | SQLAlchemy lab |
| --- | --- | --- |
| Interface | Browser job board and Django Admin | Command-line walkthrough |
| ORM | Models, managers, and querysets | Typed mappings, repositories, and sessions |
| Default database | Local file, `django.sqlite3` | In-memory SQLite, rebuilt each run |
| Schema setup | Versioned migrations | Metadata creates a fresh lab schema |
| Focus | Authenticated workflows | Explicit transactions and query composition |

## Django app

From the repository root with Python 3.12 or newer, run the commands below. On macOS or Linux, use `.venv/bin/python` in place of `.venv/Scripts/python.exe`.

~~~powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-django.txt
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py seed_demo
.venv/Scripts/python.exe manage.py runserver
~~~

1. Open [the local job board](http://127.0.0.1:8000/) and sign in as `demo-member`. Post a job or use the sample job.
2. Sign out, sign in as `demo-caregiver`, and apply. Both accounts use `caregiver-demo-local` on the local development server.
3. Return to the member account and schedule an appointment. The job leaves the public list. The member dashboard still shows its applicant count and the accepted appointment.

Use `manage.py createsuperuser` to inspect and manage records in [Django Admin](http://127.0.0.1:8000/admin/). Use the job board to exercise the workflow rules. Demo accounts and default settings are for local development. Use deployment-specific settings and credentials if you host the app.

~~~powershell
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py test
~~~

## SQLAlchemy lab

A separate virtual environment is optional. This lab needs only SQLAlchemy for the default walkthrough.

~~~powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-sqlalchemy.txt
.venv/Scripts/python.exe -m sqlalchemy_lab
.venv/Scripts/python.exe -m unittest sqlalchemy_lab.verification
~~~

Expected output with in-memory SQLite:

~~~text
Job 1 (Elderly care): 1 applicant(s)
Appointment 1: accepted, 2 hours
~~~

The original coursework used MySQL. To try the lab on MySQL 8.0.16 or later, create an empty, dedicated schema and a user with access to it. Install `requirements-mysql.txt` and set `LAB_DATABASE_URL` to a `mysql+pymysql` connection URL for that schema before running the lab. Keep the URL outside Git and URL-encode special characters in the password. Use a fresh schema for a persisted demo run. The verified walkthrough and tests use SQLite.

## Compare the implementations

The [ORM walkthrough](docs/orm-walkthrough.md) explains the relationships, query patterns, transactions, and suggested exercises.
