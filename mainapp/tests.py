from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Appointment, Caregiver, Job, JobApplication, Member, User
from .services import accept_application


class JobWorkflowTests(TestCase):
    def setUp(self):
        def profile(name):
            account = get_user_model().objects.create_user(username=name)
            return User.objects.create(account=account, given_name=name)

        self.member = Member.objects.create(user=profile("member"))
        self.other = Member.objects.create(user=profile("other"))
        self.caregiver = Caregiver.objects.create(
            user=profile("caregiver"), hourly_rate=Decimal("15.00"),
        )
        self.schedule = {"date": "2026-12-10", "time": "14:00", "hours": 2}

    def post_job(self):
        self.client.force_login(self.member.user.account)
        response = self.client.post(reverse("create_job"), {
            "required_caregiving_type": "Elderly care", "other_requirements": "Afternoons",
        })
        self.assertRedirects(response, reverse("index"))
        return Job.objects.get()

    def test_post_apply_twice_and_accept(self):
        job = self.post_job()
        self.client.force_login(self.caregiver.user.account)
        for _ in range(2):
            response = self.client.post(reverse("apply", args=[job.pk]))
            self.assertRedirects(response, reverse("index"))
        application = JobApplication.objects.get(job=job)
        self.client.force_login(self.member.user.account)
        url = reverse("accept", args=[application.pk])
        self.assertRedirects(self.client.post(url, self.schedule), reverse("index"))
        self.assertEqual(self.client.post(url, self.schedule).status_code, 404)
        job.refresh_from_db()
        self.assertFalse(job.is_open)
        self.assertEqual(Appointment.objects.get(application=application).work_hours, 2)
        self.assertContains(self.client.get(reverse("index")), "1 application")

    def test_another_member_cannot_accept(self):
        job = self.post_job()
        application = JobApplication.objects.create(
            job=job, caregiver=self.caregiver, date_applied=date.today(),
        )
        self.client.force_login(self.other.user.account)
        response = self.client.post(reverse("accept", args=[application.pk]), self.schedule)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Appointment.objects.exists())

    def test_failed_appointment_insert_rolls_back_job_closure(self):
        job = self.post_job()
        application = JobApplication.objects.create(
            job=job, caregiver=self.caregiver, date_applied=date.today(),
        )
        with self.assertRaises(IntegrityError):
            accept_application(application=application, date=date.today(), time=time(14), hours=0)
        job.refresh_from_db()
        self.assertTrue(job.is_open)
