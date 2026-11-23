-- Schema-only MySQL DDL derived from the adapted course ORM mappings.
-- Run in an empty, dedicated practice schema.

CREATE TABLE `USER` (
	user_id INTEGER NOT NULL AUTO_INCREMENT,
	email VARCHAR(255),
	given_name VARCHAR(255),
	surname VARCHAR(255),
	city VARCHAR(255),
	profile_description TEXT,
	PRIMARY KEY (user_id)
);

CREATE TABLE `CAREGIVER` (
	caregiver_user_id INTEGER NOT NULL,
	photo VARCHAR(255),
	gender VARCHAR(50),
	caregiving_type VARCHAR(255),
	hourly_rate DECIMAL(7, 2),
	PRIMARY KEY (caregiver_user_id),
	FOREIGN KEY(caregiver_user_id) REFERENCES `USER` (user_id)
);

CREATE TABLE `MEMBER` (
	member_user_id INTEGER NOT NULL,
	house_rules TEXT,
	PRIMARY KEY (member_user_id),
	FOREIGN KEY(member_user_id) REFERENCES `USER` (user_id)
);

CREATE TABLE `ADDRESS` (
	member_user_id INTEGER NOT NULL,
	house_number VARCHAR(50),
	street VARCHAR(255),
	town VARCHAR(255),
	PRIMARY KEY (member_user_id),
	FOREIGN KEY(member_user_id) REFERENCES `MEMBER` (member_user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `APPOINTMENT` (
	appointment_id INTEGER NOT NULL AUTO_INCREMENT,
	caregiver_user_id INTEGER,
	member_user_id INTEGER,
	appointment_date DATE,
	appointment_time TIME,
	work_hours INTEGER,
	status VARCHAR(50),
	PRIMARY KEY (appointment_id),
	FOREIGN KEY(caregiver_user_id) REFERENCES `CAREGIVER` (caregiver_user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(member_user_id) REFERENCES `MEMBER` (member_user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `JOB` (
	job_id INTEGER NOT NULL AUTO_INCREMENT,
	member_user_id INTEGER NOT NULL,
	required_caregiving_type VARCHAR(255),
	other_requirements TEXT,
	date_posted DATE,
	PRIMARY KEY (job_id),
	FOREIGN KEY(member_user_id) REFERENCES `MEMBER` (member_user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `JOB_APPLICATION` (
	caregiver_user_id INTEGER NOT NULL,
	job_id INTEGER NOT NULL,
	date_applied DATE,
	PRIMARY KEY (caregiver_user_id, job_id),
	FOREIGN KEY(caregiver_user_id) REFERENCES `CAREGIVER` (caregiver_user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(job_id) REFERENCES `JOB` (job_id) ON DELETE CASCADE ON UPDATE CASCADE
);
