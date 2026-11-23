# Assignment 02 ? Caregiver database implementation

**Goal.** Build a relational database for caregivers, members, jobs, applications, and appointments. Populate it with sample data and use it to answer questions about hiring and appointment costs.

**Solution.** [ORM mappings](tables.py) represent the original seven entities. The [query runner](run_queries.py) creates the schema, seeds synthetic records, and runs the coursework exercises in order. The [MySQL DDL](schema.mysql.sql) is a schema-only export of these adapted mappings. [SQL report examples](reports.sql) show how to write three of the ORM reports directly in SQL.

| Exercise | Solution in the query runner |
| --- | --- |
| Insert sample records | Seed caregivers, members, addresses, jobs, applications, and appointments with a fixed random seed. |
| Update records | Change a matching user's city and update rates using different rules below and above a threshold. |
| Delete records | Remove jobs for a selected member and remove members associated with a given street. Follow cascading deletes in the mappings. |
| Filter and join | Find accepted appointments, jobs with matching text, hours for a caregiver type, and members with matching location and household rules. |
| Aggregate | Count applicants per job, including jobs with zero applicants. Compute total hours and average pay for accepted appointments. |
| Compare to an aggregate | Find caregivers with at least one accepted appointment paid above the average accepted appointment. |
| Report | Sum accepted appointment costs and list job applications with applicant details. |

From the repository root, use the same SQLAlchemy dependencies as the standalone lab.

~~~powershell
.venv/Scripts/python.exe -m pip install -r requirements-sqlalchemy.txt
.venv/Scripts/python.exe -m coursework.assignment_02_caregiver.run_queries
~~~

The runner creates an in-memory SQLite database with foreign keys enabled. It can be rerun without a pre-existing database or credentials. The MySQL DDL is available for reviewing the table definitions or trying them in an empty practice schema. The automated demo uses SQLite.

## Changes from the submission

The original exercise used MySQL and SQLAlchemy. This copy retains the exercise sequence and query patterns. It uses synthetic contact placeholders, omits password and phone fields, and runs inside a disposable database. The job table uses a single primary key so applications can reference a unique job on SQLite. The schema-only export omits the original dump's data, session directives, and table drops.

The [standalone SQLAlchemy lab](../../sqlalchemy_lab/) is the later implementation of the caregiver workflow. It focuses on repository functions and controls job acceptance through an explicit transaction. Compare it with the coursework to see how the same domain can evolve from a query exercise to an application.
