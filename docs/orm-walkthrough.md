# Side-by-side ORM walkthrough

Both implementations use the caregiver assignment as a starting point. The Django app uses its built-in auth model for sessions and password hashing. Its original `User` table now represents the domain profile and can link to an auth account. The SQLAlchemy lab uses `Profile` as domain data and passes actor IDs directly from its CLI demo.

~~~mermaid
erDiagram
    PROFILE ||--o| MEMBER : has
    PROFILE ||--o| CAREGIVER : has
    MEMBER ||--o{ ADDRESS : has
    MEMBER ||--o{ JOB : posts
    JOB ||--o{ JOB_APPLICATION : receives
    CAREGIVER ||--o{ JOB_APPLICATION : submits
    JOB ||--o| APPOINTMENT : results_in
~~~

The diagram represents the supported workflow. Appointment records also store the member and caregiver IDs. Django links an appointment to its chosen application. SQLAlchemy links it directly to the job, with a unique constraint on the job ID. Addresses are part of the schema and are outside the demo workflow.

| Topic | Django | SQLAlchemy |
| --- | --- | --- |
| Where mapping lives | [models.py](../mainapp/models.py) | [models.py](../sqlalchemy_lab/models.py) |
| Where workflow logic lives | [services.py](../mainapp/services.py) and [views.py](../mainapp/views.py) | [repository.py](../sqlalchemy_lab/repository.py) |
| Duplicate application | Surrogate ID plus a unique constraint on (job, caregiver) | Composite primary key (job, caregiver) |
| Zero applicants | `annotate(applicants=Count("jobapplication"))` | `outerjoin()` plus `group_by()` and `count()` |
| Transaction boundary | `transaction.atomic` on the acceptance service | Caller owns `Session.begin()`. Repository uses `flush()` to send writes and obtain generated IDs |
| Schema evolution | Follow [migrations](../mainapp/migrations/) | `create_all()` bootstraps a fresh schema. Schema changes in a persistent application would require migrations |

## Trace an acceptance

1. The Django view verifies that the signed-in member owns the job. The SQLAlchemy repository includes the member ID in the job update predicate.
2. A conditional update changes the job from open to closed. Once a transaction claims the job, a second acceptance cannot also change it from open to closed.
3. The same transaction writes an appointment. If the insert fails, the transaction rolls back the job closure. A database check constraint requires positive hours in each implementation.

The models and transactions cover one appointment per accepted job through the supported workflow. Calendar conflicts, rescheduling, account registration, and coordination between the two databases are outside this demo. The SQLAlchemy duplicate check makes repeat CLI submissions straightforward. For concurrent callers, the composite primary key protects the table and callers must handle and roll back an integrity error if two inserts race.

## Exercises

1. Post a second job with no applications. Explain why a left join includes it and why counting the application's caregiver ID yields zero.
2. Compare `session.flush()` with a commit. Run the rollback tests and trace which rows are visible afterward.
3. Add an aggregate for scheduled hours by caregiver. Write it as a Django queryset and a SQLAlchemy select statement and compare the generated SQL.
4. Add an index for a filtered job listing and compare its query plan before and after. Use a larger synthetic dataset so that the planner has a reason to choose between scan strategies.

## Working with older copies

Use a fresh demo database. The Django app defaults to `django.sqlite3` and creates it through migrations. If you intentionally point `DJANGO_DB_PATH` at a historical database, back it up and inspect legacy data first. Migration 0002 removes the old profile password field, adds the optional link to Django auth, and adds uniqueness and positive-hours constraints. Legacy profiles need to be linked to auth accounts before they can sign in. Existing duplicates and nonpositive appointment hours must be resolved before migration. The [coursework section](../coursework/) contains the original design and the adapted query exercises.
