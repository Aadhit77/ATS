# Applicant Tracking System (ATS)

A full-stack web platform that digitizes and streamlines the recruitment process — built as a *21CSC205P — Database Management Systems* project at SRM IST Vadapalani.

## Problem

Traditional recruitment is manual and messy: applications get lost in email threads or spreadsheets, resume screening is disorganized, and applicants get little to no visibility into where their application stands. As applicant volume grows, this becomes unmanageable without a centralized system.

## What it does

ATS gives job seekers and employers a shared platform to manage the entire hiring lifecycle:

- **Job seekers** register, upload resumes (PDF), browse and filter job listings, apply, and track their application status in real time (*Pending → Under Review → Selected/Rejected*)
- **Recruiters** post and manage job listings, view applicants, download resumes, and update application status
- **Admins** oversee users and job posts, moderate spam/duplicate listings, and monitor system-wide activity

## Architecture

**Entities**: `User` (candidates & recruiters) · `Resume` · `Job` · `Application` (the bridge table connecting candidate → job → status)

Applications carry a status field driven by recruiter action, resumes are linked to the uploading user, and job posts are owned by the recruiter who created them — all enforced through foreign-key relationships in a normalized relational schema.

## System Modules

| Module | Key Features |
|---|---|
| **User (Job Seeker)** | Signup/login, resume upload, browse/filter jobs, apply, track application status |
| **Recruiter (Employer)** | Post/edit/delete jobs, view applicants, download resumes, update application status |
| **Admin** | User management, job post moderation, system-wide monitoring |

## Tech Stack

**Frontend**: HTML5 · CSS3 · JavaScript · Bootstrap
**Backend**: PHP (server-side logic, auth, session management) — alternatively adaptable to Node.js or Python/Flask
**Database**: MySQL
**Dev environment**: XAMPP (Apache + PHP + MySQL local stack)

## Non-Functional Requirements

- **Performance** — responds within 2–3 seconds to user actions, handles concurrent users
- **Security** — hashed passwords, input validation, SQL injection prevention, role-based access control
- **Scalability** — schema supports growth in users, job posts, and applications
- **Usability** — clean, responsive UI across desktop, tablet, and mobile
- **Data Integrity** — validation enforced at both frontend and backend

## Testing

Covered by unit, integration, and system testing phases:
- **Unit** — login/signup validation, resume upload handling, job post creation, duplicate-application prevention
- **Integration** — cross-module checks (e.g. resume correctly associated with the logged-in user's ID)
- **Tools** — manual click-through testing, browser dev tools, MySQL Workbench for backend verification, Postman for API routes

## Running it

```bash
# Start XAMPP (Apache + MySQL)
# Place project files in htdocs/
# Import the database schema via phpMyAdmin
# Visit http://localhost/ats in your browser
```

## Future Scope

- Resume parsing and automated candidate-job matching
- Analytics dashboard for recruiters
- Mobile app version
- Multi-language support (localization)

## Team

Aathitya A · T.P. Krishith · Pranav M — under the guidance of Dr. R. Dayana, Dept. of CSE (Emerging Technologies), SRM IST Vadapalani.
