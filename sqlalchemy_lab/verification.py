from datetime import date, time
from decimal import Decimal
import unittest

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import open_database
from .models import Appointment, Base, Caregiver, Job, JobApplication, Member, Profile
from .repository import accept_application, applicant_counts, post_job, submit_application


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = open_database()
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as session, session.begin():
            member = Member(profile=Profile(email="m@example.invalid", given_name="M", city="Astana"))
            caregiver = Caregiver(
                profile=Profile(email="c@example.invalid", given_name="C", city="Astana"),
                caregiving_type="Elderly care", hourly_rate=Decimal("15.00"),
            )
            session.add_all([member, caregiver])
            session.flush()
            self.member_id, self.caregiver_id = member.id, caregiver.id
            self.job_id = post_job(session, member_id=member.id, care_type="Care", requirements="").id

    def apply(self, session):
        return submit_application(session, job_id=self.job_id, caregiver_id=self.caregiver_id)

    def accept(self, session, member_id):
        return accept_application(
            session, job_id=self.job_id, caregiver_id=self.caregiver_id, member_id=member_id,
            date=date.today(), time=time(14), hours=2,
        )

    def test_report_duplicate_application_and_acceptance(self):
        with Session(self.engine) as session, session.begin():
            self.assertEqual(applicant_counts(session, member_id=self.member_id)[0][2], 0)
            self.apply(session)
            self.apply(session)
            self.assertEqual(session.scalar(select(func.count()).select_from(JobApplication)), 1)
            self.assertEqual(applicant_counts(session, member_id=self.member_id)[0][2], 1)
            with self.assertRaises(ValueError):
                self.accept(session, member_id=-1)
            self.accept(session, self.member_id)
            with self.assertRaises(ValueError):
                self.accept(session, self.member_id)
        with Session(self.engine) as session:
            self.assertFalse(session.get(Job, self.job_id).is_open)
            self.assertEqual(session.scalar(select(func.count()).select_from(Appointment)), 1)

    def test_caller_controls_rollback(self):
        with Session(self.engine) as session, session.begin():
            self.apply(session)
        with self.assertRaisesRegex(RuntimeError, "abort"):
            with Session(self.engine) as session, session.begin():
                self.accept(session, self.member_id)
                raise RuntimeError("abort")
        with Session(self.engine) as session:
            self.assertTrue(session.get(Job, self.job_id).is_open)
            self.assertEqual(session.scalar(select(func.count()).select_from(Appointment)), 0)
