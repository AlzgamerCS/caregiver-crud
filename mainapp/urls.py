from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("jobs/new/", views.create_job, name="create_job"),
    path("jobs/<int:job_id>/apply/", views.apply, name="apply"),
    path("applications/<int:application_id>/accept/", views.accept, name="accept"),
]
