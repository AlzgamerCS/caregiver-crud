import os
from datetime import date, time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import open_database
from .models import Base, Caregiver, Member, Profile
from .repository import accept_application, applicant_counts, post_job, submit_application


def main():
    engine = open_database(os.environ.get("LAB_DATABASE_URL", "sqlite://"))
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session, session.begin():
            if session.scalar(select(Profile.id).limit(1)) is not None:
                raise SystemExit("The lab needs an empty dedicated database.")
            member = Member(profile=Profile(
                given_name="Aida", city="Astana", email="member@example.invalid",
            ))
            caregiver = Caregiver(
                profile=Profile(given_name="Sam", city="Astana", email="caregiver@example.invalid"),
                caregiving_type="Elderly care", hourly_rate=Decimal("15.00"),
            )
            session.add_all([member, caregiver])
            session.flush()
            job = post_job(session, member_id=member.id, care_type="Elderly care",
                           requirements="Synthetic demo: afternoon companionship.")
            submit_application(session, job_id=job.id, caregiver_id=caregiver.id)
            appointment = accept_application(
                session, job_id=job.id, caregiver_id=caregiver.id, member_id=member.id,
                date=date.today(), time=time(14), hours=2,
            )
            report = [
                f"Job {job_id} ({care_type}): {count} applicant(s)"
                for job_id, care_type, count in applicant_counts(session, member_id=member.id)
            ]
            summary = f"Appointment {appointment.id}: {appointment.status}, {appointment.work_hours} hours"
        print(*report, summary, sep="\n")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
