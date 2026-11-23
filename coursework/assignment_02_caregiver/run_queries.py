"""Run the adapted coursework queries on an isolated in-memory SQLite database."""

from datetime import datetime, time, timedelta
from decimal import Decimal
from random import choice, randint, random, seed

from sqlalchemy import create_engine, event, func
from sqlalchemy.orm import Session, aliased

from .tables import Address, Appointment, Base, Caregiver, Job, JobApplication, Member, User


cities = [
    "Almaty",
    "Taraz",
    "Astana",
    "Shymkent",
    "Semey",
    "Pavlodar",
    "Atyrau",
]

names = [
    "Askar",
    "Bolat",
    "Kerey",
    "Kuanysh",
    "Nursultan",
    "Almas",
    "Azamat",
    "Medet",
    "Islam",
    "Sanzhar",
    "Aziz",
    "Zhanibek",
    "Nurbek",
    "Marat",
    "Bekzat",
    "Miras",
    "Arsen",
    "Beksultan",
]


streets = [
    "Turan",
    "Kabanbay",
    "Tole bi",
    "Nazarbayev",
    "Abay",
    "Zhangeldin",
    "Bogenbay",
    "Respublica",
    "Seifullina",
    "Baitursunov",
    "Zhumabayev",
    "Momyshuly",
]

caregiving_types = ["Baby Sitter", "Elderly Care", "Playmate for Children"]


start_val = 100


curr_id = start_val


def generate_id(increment):
    global curr_id
    oldId = curr_id
    if increment:
        curr_id += 1
    return oldId


curr_address_id = start_val


def generate_address_id(increment):
    global curr_address_id
    oldId = curr_address_id
    if increment:
        curr_address_id += 1
    return oldId


curr_job_id = start_val


def generate_job_id(increment):
    global curr_job_id
    oldId = curr_job_id
    if increment:
        curr_job_id += 1
    return oldId


curr_appointment_id = start_val


def generate_appointment_id(increment):
    global curr_appointment_id
    oldId = curr_appointment_id
    if increment:
        curr_appointment_id += 1
    return oldId


def generate_number(n):
    return "".join([str(randint(0, 9)) for _ in range(n)])


def generate_email(name, surname):
    return name.lower() + "." + surname.lower() + "@example.invalid"


def generate_date():
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 10, 31)
    delta = end_date - start_date
    random_days = randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.date()


def generate_time():
    random_hour = randint(0, 23)  # Hour between 0 and 23
    random_minute = randint(0, 59)  # Minute between 0 and 59
    random_second = randint(0, 59)  # Second between 0 and 59
    return time(random_hour, random_minute, random_second)


def generate_caregiver():
    name = choice(names)
    surname = choice(names) + "ov"
    user_id = generate_id(True)
    email = generate_email(name, surname)
    city = choice(cities)
    photo = "image.jpg"
    gender = "Male"
    hourly_rate = Decimal(str(5 + random() * 10)).quantize(Decimal("0.01"))
    return (
        User(
            user_id=user_id,
            email=email,
            given_name=name,
            surname=surname,
            city=city,
            profile_description="A professional caregiver",
        ),
        Caregiver(
            caregiver_user_id=user_id,
            photo=photo,
            gender=gender,
            caregiving_type=choice(caregiving_types),
            hourly_rate=hourly_rate,
        ),
    )


def generate_member():
    name = choice(names)
    surname = choice(names) + "ov"
    user_id = generate_id(True)
    email = generate_email(name, surname)
    city = choice(cities)
    return (
        User(
            user_id=user_id,
            email=email,
            given_name=name,
            surname=surname,
            city=city,
            profile_description="Need caregivers' help!",
        ),
        Member(
            member_user_id=user_id,
            house_rules=choice(["No smoking", "no drinking", "hygiene", "No pets"]),
        ),
    )


def generate_address():
    return Address(
        member_user_id=generate_address_id(True),  # type: ignore
        house_number=generate_number(3),
        street=choice(streets),
        town=choice(cities),
    )


def generate_job(session):
    member_id = choice(session.query(Member).all()).member_user_id
    return Job(
        job_id=(generate_job_id(True)),
        member_user_id=member_id,  # type: ignore
        required_caregiving_type=choice(caregiving_types),
        other_requirements=choice(
            [
                "gentle",
                "good cook",
                "with medical education",
                "high communication skills",
            ]
        ),
        date_posted=generate_date(),
    )


def generate_job_application(session):
    while True:
        caregiver_id = choice(session.query(Caregiver).all()).caregiver_user_id
        job = choice(session.query(Job).all())
        if (
            session.query(JobApplication)
            .filter_by(caregiver_user_id=caregiver_id, job_id=job.job_id)
            .first()
            is not None
        ):
            continue
        return JobApplication(
            caregiver_user_id=caregiver_id,
            job_id=job.job_id,
            date_applied=job.date_posted + timedelta(days=randint(0, 60)),
        )


def generate_appointment(session):
    return Appointment(
        appointment_id=(generate_appointment_id(True)),
        caregiver_user_id=choice(session.query(Caregiver).all()).caregiver_user_id,
        member_user_id=choice(session.query(Member).all()).member_user_id,
        appointment_date=generate_date(),
        appointment_time=generate_time(),
        work_hours=randint(1, 12),
        status=choice(["Accepted", "Not accepted"]),
    )


def seed_random_rows(session):
    global curr_address_id
    n = 30
    m = 40
    for _ in range(n):
        user, caregiver = generate_caregiver()
        session.add(user)
        session.flush()
        session.add(caregiver)
        session.flush()
    for _ in range(n):
        user, member = generate_member()
        session.add(user)
        session.flush()
        session.add(member)
        session.flush()

    last_member_id = generate_id(False)
    curr_address_id = last_member_id - n

    for _ in range(n):
        address = generate_address()
        session.add(address)
        session.flush()
    for _ in range(m):
        job = generate_job(session)
        session.add(job)
        session.flush()
    for _ in range(m):
        job_application = generate_job_application(session)
        session.add(job_application)
        session.flush()
    for _ in range(m):
        appointment = generate_appointment(session)
        session.add(appointment)
        session.flush()


def run_course_queries(session):
    # Insertions
    askar = User(
        user_id=1,
        email="askar.askarov@example.invalid",
        given_name="Askar",
        surname="Askarov",
        city="Almaty",
        profile_description="Very professional caregiver for elderly people. I love my job!",
    )
    askarCaregiver = Caregiver(
        caregiver_user_id=1,
        photo="path_to_photo.jpg",
        gender="M",
        caregiving_type="Elder Care",
        hourly_rate=Decimal("15.50"),
    )
    session.add(askar)
    session.add(askarCaregiver)
    session.flush()

    bolat = User(
        user_id=2,
        email="bolat.bolatov@example.invalid",
        given_name="Bolat",
        surname="Bolatov",
        city="Astana",
        profile_description="Elderly blind man needs a caregiver.",
    )
    bolatMember = Member(member_user_id=2, house_rules="Hygiene, no smoking, no drinking")
    session.add(bolat)
    session.add(bolatMember)
    session.flush()

    p1 = User(
        user_id=10000,
        email="nurbek.nurbekov@example.invalid",
        given_name="Nurbek",
        surname="Nurbekov",
        city="Astana",
        profile_description="Little kid needs a babysitter.",
    )
    session.add(p1)
    session.flush()

    p1Member = Member(member_user_id=10000, house_rules="No pets")
    session.add(p1Member)
    session.flush()

    newjob = Job(
        job_id=100000,
        member_user_id=10000,
        required_caregiving_type="Elderly Care",
        other_requirements="gentle",
        date_posted=generate_date(),
    )
    session.add(newjob)
    session.flush()

    # Random insertions
    seed_random_rows(session)

    # Queries

    # 3.1
    askars = session.query(User).filter_by(given_name="Askar", surname="Askarov")
    print("3.1 Change the city of the matching user:")
    print("Before:")
    for askar in askars:
        print(askar)

    for askar in askars:
        askar.city = "Astana"
    session.flush()

    askars = session.query(User).filter_by(given_name="Askar", surname="Askarov")
    print("After:")
    for askar in askars:
        print(askar)

    # 3.2
    caregivers = session.query(Caregiver)
    print("3.2 Caregivers:")
    print("Before:")
    for caregiver in caregivers:
        print(caregiver)

    for caregiver in caregivers:
        if caregiver.hourly_rate < Decimal("9"):
            caregiver.hourly_rate += Decimal("0.5")
        else:
            caregiver.hourly_rate = (caregiver.hourly_rate * Decimal("1.1")).quantize(Decimal("0.01"))
        session.flush()

    print("After:")
    for caregiver in caregivers:
        print(caregiver)
    # 4.1
    bolats = session.query(User).filter_by(given_name="Bolat", surname="Bolatov")
    bolats_ids = [bolat.user_id for bolat in bolats]
    session.query(Job).filter(Job.member_user_id.in_(bolats_ids)).delete()
    session.flush()

    # 4.2
    member_ids_on_turan = session.query(Address.member_user_id).filter_by(street="Turan")
    member_ids_on_turan = [id[0] for id in member_ids_on_turan]
    session.query(Member).filter(Member.member_user_id.in_(member_ids_on_turan)).delete()
    session.flush()

    # 5.1
    CaregiverUser = aliased(User)
    MemberUser = aliased(User)

    accepted_appointments = (
        session.query(
            CaregiverUser.given_name.label("caregiver_name"),
            MemberUser.given_name.label("member_name"),
        )
        .join(Caregiver, CaregiverUser.user_id == Caregiver.caregiver_user_id)
        .join(Appointment, Caregiver.caregiver_user_id == Appointment.caregiver_user_id)
        .join(Member, Member.member_user_id == Appointment.member_user_id)
        .join(MemberUser, Member.member_user_id == MemberUser.user_id)
        .filter(Appointment.status == "Accepted")
        .all()
    )

    print("5.1 Accepted appointments:")
    print(accepted_appointments, "\n")

    # 5.2
    jobs_with_gentle = (
        session.query(Job.job_id).filter(Job.other_requirements.like("%gentle%")).all()
    )

    print("5.2 Job IDs with 'gentle':")
    print([job.job_id for job in jobs_with_gentle], "\n")

    # 5.3
    baby_sitters = [
        id[0]
        for id in session.query(Caregiver.caregiver_user_id).filter(
            Caregiver.caregiving_type == "Baby Sitter"
        )
    ]

    print("5.3 Work hours of Baby Sitters:")
    print(
        [
            x[0]
            for x in session.query(Appointment.work_hours).filter(
                Appointment.caregiver_user_id.in_(baby_sitters)
            )
        ],
        "\n",
    )


    # 5.4

    members = (
        session.query(Member)
        .join(User, Member.member_user_id == User.user_id)
        .join(Job, Member.member_user_id == Job.member_user_id)
        .filter(Job.required_caregiving_type == "Elderly Care")
        .filter(User.city == "Astana")
        .filter(Member.house_rules.like("%No pets%"))
        .all()
    )

    print("5.4 Members who are looking for Elderly Care in Astana and have 'No pets' rule:")
    print(members, "\n")

    # 6.1
    job_applicant_counts = (
        session.query(
            Job.job_id, func.count(JobApplication.job_id).label("applicant_count")
        )
        .join(Member, Member.member_user_id == Job.member_user_id)
        .outerjoin(JobApplication, Job.job_id == JobApplication.job_id)
        .group_by(Job.job_id)
        .all()
    )

    print(
        "6.1 Count the number of applicants for each job posted by a member (multiple joins with aggregation):"
    )
    print(job_applicant_counts, "\n")

    # 6.2

    total_hours = (
        session.query(func.sum(Appointment.work_hours).label("total_hours"))
        .join(Caregiver, Caregiver.caregiver_user_id == Appointment.caregiver_user_id)
        .filter(Appointment.status == "Accepted")
        .scalar()
    )

    print(
        "6.2 Total hours spent by care givers for all accepted appointments (multiple joins with aggregation):"
    )
    print(f"Total Hours Spent by Caregivers: {total_hours}", "\n")


    # 6.3


    average_pay = (
        session.query(
            func.avg(Appointment.work_hours * Caregiver.hourly_rate).label("average_pay")
        )
        .join(Caregiver, Caregiver.caregiver_user_id == Appointment.caregiver_user_id)
        .filter(Appointment.status == "Accepted")
        .scalar()
    )

    print(
        "6.3 Average pay of caregivers based on accepted appointments (join with aggregation):"
    )
    print(f"Average Pay of Caregivers: {average_pay}", "\n")


    # 6.4

    caregivers_above_average = (
        session.query(Caregiver)
        .join(Appointment, Caregiver.caregiver_user_id == Appointment.caregiver_user_id)
        .filter(Appointment.status == "Accepted")
        .filter((Appointment.work_hours * Caregiver.hourly_rate) > average_pay)
        .group_by(Caregiver.caregiver_user_id)
        .all()
    )

    print(
        "6.4 Caregivers with an accepted appointment above the average appointment cost:"
    )
    for caregiver in caregivers_above_average:
        print(caregiver)
    print("\n")


    # 7
    total_cost = (
        session.query(
            func.sum(Appointment.work_hours * Caregiver.hourly_rate).label("total_cost")
        )
        .join(Caregiver, Caregiver.caregiver_user_id == Appointment.caregiver_user_id)
        .filter(Appointment.status == "Accepted")
        .scalar()
    )

    print(
        "7 Calculate the total cost to pay for a caregiver for all accepted appointments:"
    )
    print(f"Total Cost for All Accepted Appointments: {total_cost}", "\n")


    # 8

    applications_with_applicants = (
        session.query(JobApplication, User)
        .join(User, User.user_id == JobApplication.caregiver_user_id)
        .all()
    )
    print("8 View all job applications and the applicants:")
    for application, user in applications_with_applicants:
        print(f"Application: {application}, Applicant: {user}")


def main():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys = ON")

    try:
        Base.metadata.create_all(engine)
        seed(0)
        with Session(engine) as session, session.begin():
            run_course_queries(session)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
