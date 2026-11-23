from datetime import date, time
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    given_name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))


class Caregiver(Base):
    __tablename__ = "caregiver"

    id: Mapped[int] = mapped_column(ForeignKey("profile.id"), primary_key=True)
    caregiving_type: Mapped[str] = mapped_column(String(255))
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(7, 2))
    profile: Mapped[Profile] = relationship()


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(ForeignKey("profile.id"), primary_key=True)
    house_rules: Mapped[str] = mapped_column(Text, default="")
    profile: Mapped[Profile] = relationship()


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    street: Mapped[str] = mapped_column(String(255))
    town: Mapped[str] = mapped_column(String(255))


class Job(Base):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    required_caregiving_type: Mapped[str] = mapped_column(String(255))
    other_requirements: Mapped[str] = mapped_column(Text, default="")
    date_posted: Mapped[date] = mapped_column(default=date.today)
    is_open: Mapped[bool] = mapped_column(default=True)
    member: Mapped[Member] = relationship()


class JobApplication(Base):
    __tablename__ = "job_application"

    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), primary_key=True)
    caregiver_id: Mapped[int] = mapped_column(ForeignKey("caregiver.id"), primary_key=True)
    date_applied: Mapped[date] = mapped_column(default=date.today)


class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = (CheckConstraint("work_hours > 0", name="appointment_positive_hours"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), unique=True)
    caregiver_id: Mapped[int] = mapped_column(ForeignKey("caregiver.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    appointment_date: Mapped[date]
    appointment_time: Mapped[time]
    work_hours: Mapped[int]
    status: Mapped[str] = mapped_column(String(50), default="accepted")
