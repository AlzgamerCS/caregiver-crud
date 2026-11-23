from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import AppointmentForm, JobForm
from .models import Appointment, Caregiver, Job, JobApplication, Member
from .services import ClosedJob, accept_application, submit_application


def index(request):
    jobs = Job.objects.filter(is_open=True).order_by("-date_posted", "pk")
    context = {"jobs": jobs}
    if request.user.is_authenticated:
        member = Member.objects.filter(user__account=request.user).first()
        context["member"] = member
        context["caregiver"] = Caregiver.objects.filter(user__account=request.user).exists()
        if member:
            context["job_report"] = Job.objects.filter(member=member).annotate(
                applicants=Count("jobapplication"),
            ).order_by("pk")
            context["appointments"] = Appointment.objects.filter(
                member=member, status="accepted",
            ).select_related("caregiver__user").order_by("appointment_date", "appointment_time")
            context["applications"] = JobApplication.objects.filter(
                job__member=member, job__is_open=True,
            ).select_related("job", "caregiver__user").order_by("pk")
    return render(request, "mainapp/index.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def create_job(request):
    member = get_object_or_404(Member, user__account=request.user)
    form = JobForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        job = form.save(commit=False)
        job.member = member
        job.date_posted = timezone.localdate()
        job.save()
        return redirect("index")
    return render(request, "mainapp/form.html", {"title": "Post a job", "form": form})


@login_required
@require_POST
def apply(request, job_id):
    caregiver = get_object_or_404(Caregiver, user__account=request.user)
    job = get_object_or_404(Job, pk=job_id)
    try:
        _, created = submit_application(job=job, caregiver=caregiver)
    except ClosedJob as exc:
        messages.error(request, str(exc))
    else:
        messages.info(request, "Application submitted." if created else "You already applied.")
    return redirect("index")


@login_required
@require_http_methods(["GET", "POST"])
def accept(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related("job"),
        pk=application_id,
        job__member__user__account=request.user,
    )
    if not application.job.is_open:
        raise Http404("This job is closed.")
    form = AppointmentForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        try:
            accept_application(application=application, **form.cleaned_data)
        except ClosedJob as exc:
            form.add_error(None, str(exc))
        else:
            return redirect("index")
    return render(request, "mainapp/form.html", {"title": "Schedule an appointment", "form": form})
