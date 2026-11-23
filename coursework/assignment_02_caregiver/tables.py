"""Adapted mappings from the 2023 caregiver database assignment."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DECIMAL,
    ForeignKey,
    Date,
    Time,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "USER"

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255))
    given_name = Column(String(255))
    surname = Column(String(255))
    city = Column(String(255))
    profile_description = Column(Text)

    # Relationships
    caregiver = relationship("Caregiver", back_populates="user", uselist=False)
    member = relationship("Member", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, given_name='{self.given_name}', surname='{self.surname}')>"


class Caregiver(Base):
    __tablename__ = "CAREGIVER"

    caregiver_user_id = Column(Integer, ForeignKey("USER.user_id"), primary_key=True)
    photo = Column(String(255))
    gender = Column(String(50))
    caregiving_type = Column(String(255))
    hourly_rate = Column(DECIMAL(7, 2))

    # Relationships
    user = relationship("User", back_populates="caregiver")

    def __repr__(self):
        return f"<Caregiver({self.user}, caregiving_type='{self.caregiving_type}', hourly_rate={self.hourly_rate})>"


class Member(Base):
    __tablename__ = "MEMBER"

    member_user_id = Column(Integer, ForeignKey("USER.user_id"), primary_key=True)
    house_rules = Column(Text)

    # Relationships
    user = relationship("User", back_populates="member")

    def __repr__(self):
        return f"<Member({self.user}, house rules='{self.house_rules}')>"


class Address(Base):
    __tablename__ = "ADDRESS"

    member_user_id = Column(
        Integer,
        ForeignKey("MEMBER.member_user_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    house_number = Column(String(50))
    street = Column(String(255))
    town = Column(String(255))

    def __repr__(self):
        return f"<Address(member_user_id={self.member_user_id}, house_number={self.house_number}, street={self.street}, town={self.town})>"


class Job(Base):
    __tablename__ = "JOB"

    job_id = Column(Integer, primary_key=True)
    member_user_id = Column(
        Integer,
        ForeignKey("MEMBER.member_user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    required_caregiving_type = Column(String(255))
    other_requirements = Column(Text)
    date_posted = Column(Date)

    def __repr__(self):
        return f"<Job(job_id={self.job_id}, {self.member_user_id}, required_caregiving_type={self.required_caregiving_type}, other_requirements={self.other_requirements}, date_posted={self.date_posted})>"


class JobApplication(Base):
    __tablename__ = "JOB_APPLICATION"

    caregiver_user_id = Column(
        Integer,
        ForeignKey(
            "CAREGIVER.caregiver_user_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        primary_key=True,
    )
    job_id = Column(
        Integer,
        ForeignKey("JOB.job_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    date_applied = Column(Date)

    def __repr__(self):
        return f"<JobApplication(caregiver_user_id={self.caregiver_user_id}, job_id={self.job_id}, date_applied={self.date_applied})>"


class Appointment(Base):
    __tablename__ = "APPOINTMENT"

    appointment_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(
        Integer,
        ForeignKey(
            "CAREGIVER.caregiver_user_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )
    member_user_id = Column(
        Integer,
        ForeignKey("MEMBER.member_user_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Integer)
    status = Column(String(50))

    def __repr__(self):
        return f"<Appointment(appointment_id={self.appointment_id}, caregiver_user_id={self.caregiver_user_id}, member_user_id={self.member_user_id}, appointment_date={self.appointment_date})>"
