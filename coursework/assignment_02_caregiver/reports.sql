-- Applicant counts, including jobs without applications.
SELECT j.job_id, COUNT(a.caregiver_user_id) AS applicant_count
FROM JOB AS j
LEFT JOIN JOB_APPLICATION AS a ON a.job_id = j.job_id
GROUP BY j.job_id
ORDER BY j.job_id;

-- Hours and estimated pay for accepted appointments by caregiver.
SELECT c.caregiver_user_id,
       SUM(a.work_hours) AS accepted_hours,
       SUM(a.work_hours * c.hourly_rate) AS estimated_pay
FROM APPOINTMENT AS a
JOIN CAREGIVER AS c ON a.caregiver_user_id = c.caregiver_user_id
WHERE a.status = 'Accepted'
GROUP BY c.caregiver_user_id
ORDER BY c.caregiver_user_id;

-- Total cost and average cost per accepted appointment.
SELECT SUM(a.work_hours * c.hourly_rate) AS total_cost,
       AVG(a.work_hours * c.hourly_rate) AS average_appointment_cost
FROM APPOINTMENT AS a
JOIN CAREGIVER AS c ON a.caregiver_user_id = c.caregiver_user_id
WHERE a.status = 'Accepted';
