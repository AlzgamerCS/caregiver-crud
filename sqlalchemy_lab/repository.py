from sqlalchemy import func, select, update

from .models import Appointment, Job, JobApplication


def post_job(session, *, member_id, care_type, requirements):
    job = Job(
        member_id=member_id, required_caregiving_type=care_type,
        other_requirements=requirements,
    )
    session.add(job)
    session.flush()
    return job


def submit_application(session, *, job_id, caregiver_id):
    job = session.get(Job, job_id)
    if job is None or not job.is_open:
        raise ValueError("Apply to an open job.")
    existing = session.get(JobApplication, (job_id, caregiver_id))
    if existing is not None:
        return existing
    application = JobApplication(job_id=job_id, caregiver_id=caregiver_id)
    session.add(application)
    session.flush()
    return application


def accept_application(session, *, job_id, caregiver_id, member_id, date, time, hours):
    if hours < 1:
        raise ValueError("Appointment hours must be positive.")
    if session.get(JobApplication, (job_id, caregiver_id)) is None:
        raise ValueError("The caregiver has not applied to this job.")
    result = session.execute(
        update(Job).where(
            Job.id == job_id, Job.member_id == member_id, Job.is_open.is_(True),
        ).values(is_open=False)
    )
    if result.rowcount != 1:
        raise ValueError("Only the owner can accept an application to an open job.")
    appointment = Appointment(
        job_id=job_id, caregiver_id=caregiver_id, member_id=member_id,
        appointment_date=date, appointment_time=time, work_hours=hours,
    )
    session.add(appointment)
    session.flush()
    return appointment


def applicant_counts(session, *, member_id):
    query = (
        select(Job.id, Job.required_caregiving_type, func.count(JobApplication.caregiver_id))
        .outerjoin(JobApplication, Job.id == JobApplication.job_id)
        .where(Job.member_id == member_id)
        .group_by(Job.id, Job.required_caregiving_type)
        .order_by(Job.id)
    )
    return session.execute(query).all()
