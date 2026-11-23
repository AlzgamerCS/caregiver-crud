from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from mainapp.models import Caregiver, Job, Member, User


class Command(BaseCommand):
    help = "Create synthetic local demo accounts and an example job."

    @transaction.atomic
    def handle(self, *args, **options):
        member = self.profile("demo-member", "Aida")
        caregiver = self.profile("demo-caregiver", "Sam")
        member, _ = Member.objects.get_or_create(user=member)
        Caregiver.objects.get_or_create(user=caregiver, defaults={
            "caregiving_type": "Elderly care", "hourly_rate": Decimal("15.00"),
        })
        Job.objects.get_or_create(
            member=member, required_caregiving_type="Elderly care",
            other_requirements="Synthetic demo: afternoon companionship.",
            defaults={"date_posted": timezone.localdate()},
        )
        self.stdout.write("Local-only accounts: demo-member and demo-caregiver / caregiver-demo-local")

    @staticmethod
    def profile(username, given_name):
        account, created = get_user_model().objects.get_or_create(username=username)
        email = f"{username}@example.invalid"
        if not created and account.email != email:
            raise CommandError(f"{username} already belongs to another account.")
        if created:
            account.email = email
            account.set_password("caregiver-demo-local")
            account.save()
        profile, _ = User.objects.get_or_create(account=account, defaults={
            "email": email, "given_name": given_name, "surname": "Demo", "city": "Astana",
        })
        return profile
