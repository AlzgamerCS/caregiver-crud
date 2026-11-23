from django.db import transaction
from django.utils import timezone

from .models import Appointment, Job, JobApplication


class ClosedJob(ValueError):
    """Another acceptance has already closed this job."""


@transaction.atomic
def accept_application(*, application, date, time, hours):
    # A conditional write claims the job once, even when two requests race.
    claimed = Job.objects.filter(pk=application.job_id, is_open=True).update(is_open=False)
    if not claimed:
        raise ClosedJob("This job already has an accepted application.")
    return Appointment.objects.create(
        application=application,
        caregiver_id=application.caregiver_id,
        member_id=application.job.member_id,
        appointment_date=date,
        appointment_time=time,
        work_hours=hours,
        status="accepted",
    )


def submit_application(*, job, caregiver):
    if not job.is_open:
        raise ClosedJob("This job is closed.")
    return JobApplication.objects.get_or_create(
        job=job, caregiver=caregiver, defaults={"date_applied": timezone.localdate()},
    )
