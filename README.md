# Smart City Incident Management System

## 1. Project Overview

This is a Django-based multi-role incident management platform for city services.

Main roles:
- `citizen` (Fuqaro)
- `operator` (Operator)
- `technician` (Texnik)
- `admin` (Admin)

Core purpose:
- citizens submit city incidents with photo evidence
- operators triage, prioritize, and assign technicians
- technicians resolve incidents with completion evidence and report
- citizens confirm or reject resolution
- operators close incidents or re-open workflow (reassign)
- system auto-closes unresolved-feedback incidents after 7 days

---

## 2. Backend Technologies and Patterns

- **Framework**: Django
- **Auth**: Custom user model (`users.CustomUser`)
- **DB**: SQLite by default (`smart_city.sqlite3`)
- **Views**: Class-Based Views (`ListView`, `CreateView`, `DetailView`, `UpdateView`, `DeleteView`, `TemplateView`, custom `View`)
- **Forms**: Django `ModelForm` + custom multi-file form fields
- **Access control**: Role-based mixins + approval gate for operator/technician
- **Messaging**: Django messages framework for user feedback
- **Pagination**: Django built-in pagination on list pages
- **Media handling**: Django `FileField` for incident photos
- **Background logic**: management command for overdue auto-close

---

## 3. Project Structure and Connections

### Apps

- `users/`
  - registration/login/logout
  - role redirects
  - role profile/edit profile
  - admin custom user management (list/add/delete/approve)

- `incidents/`
  - incident domain models and workflow methods
  - create/list/detail actions
  - operator assignment/priority/close/add-photos actions
  - technician resolve action
  - citizen feedback action

- `notifications/`
  - notification model and helper utilities
  - unread count context processor
  - notification list/read endpoints

- `reports/`
  - citizen stats dashboard
  - technician stats dashboard
  - admin filtered incident report page

- `templates/`
  - shared base layout and role-specific pages

- `static/`
  - CSS styles used by all pages

### URL Composition

Root router (`config/urls.py`) includes:
- `/users/`
- `/incidents/`
- `/notifications/`
- `/reports/`

### High-level Request Flow

1. User authenticates via `users` app.
2. Role redirect sends user to role landing page.
3. Role mixins enforce access and approval rules.
4. Incident actions in `incidents/views.py` call model-level workflow methods (`assign_technician`, `mark_resolved`, `mark_closed`, `close_if_overdue`).
5. Notification utilities create event-based notifications for affected users.
6. Templates read context (`page_obj`, filters, unread badge, stats) and render UI.

---

## 4. Core Domain Model (How Data Is Connected)

## `CustomUser` (`users.models.CustomUser`)
- Extends `AbstractUser`
- Additional fields:
  - `role`, `phone`, `address`, `department`, `specialization`, `current_workload`, `is_approved`
- Rules:
  - citizen requires address
  - operator requires department
  - technician requires specialization
  - citizens are auto-approved in `save()`
  - admins become `is_staff`

## `Incident` (`incidents.models.Incident`)
- Links:
  - `citizen` (owner)
  - optional `operator`
  - optional `technician`
- Main fields:
  - title, description, category, priority, region, address
  - status (`NEW`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`)
  - workflow timestamps and round
- Workflow methods:
  - `assign_technician()`
  - `mark_resolved()`
  - `mark_closed()`
  - `close_if_overdue()`

## `IncidentPhoto`
- Linked to incident and uploader
- Kinds:
  - `initial` (citizen, exactly 3, round 0)
  - `technician_completion` (technician, exactly 3 per round)
  - `operator_completion` (operator, max 2 per round, on RESOLVED)

## `ResolutionReport`
- One report per incident per workflow round
- Submitted by assigned technician during resolution

## `CitizenFeedback`
- One-to-one with incident
- Submitted once by incident owner when status is `RESOLVED`
- Stores resolved/not-resolved, reason, optional rating

## `IncidentUpdate`
- Timeline log of status transitions and notes

## `Notification`
- Linked to target user and optionally incident
- Stores message, type, read state, timestamp

---

## 5. Detailed Business Logic

## 5.1 Authentication, Roles, and Approval

- Login success redirect:
  - citizen -> `incidents:citizen_incident_list`
  - operator -> `incidents:operator_incident_list`
  - technician -> `incidents:technician_incident_list`
  - admin -> `reports:admin_system_reports`

- Role protection:
  - each role uses dedicated mixin
  - operator and technician must be `is_approved=True`
  - otherwise redirected to `users:pending_approval`

## 5.2 Citizen Workflow

1. Citizen registers (auto-approved).
2. Creates incident with required fields + **exactly 3 initial photos**.
3. Incident starts in `NEW`.
4. System notifies all approved operators.
5. Citizen tracks status in list/detail.
6. When incident becomes `RESOLVED`, citizen can submit feedback once:
   - `is_resolved=True` optionally with rating
   - `is_resolved=False` reason required
7. If not resolved feedback:
   - operators notified
   - incident can be re-assigned (new workflow round)
8. If no feedback within 7 days of `RESOLVED`:
   - system auto-closes incident
   - citizen and operators notified

## 5.3 Operator Workflow

1. Operator views incident dashboard list (paginated).
2. Uses filters:
   - priority
   - assigned yes/no
   - status
3. Sees available technicians (`current_workload=0`).
4. Can update incident priority from detail page.
5. Assignment logic:
   - assignment allowed on `NEW`
   - re-assignment allowed for unresolved feedback after `RESOLVED`
   - technician list filtered by category-compatible specialization (+ multi-skilled)
   - only approved technicians are assignable
6. On assignment:
   - incident -> `IN_PROGRESS`
   - operator set, technician set
   - technician workload increments
   - notification sent to technician and citizen
7. On `RESOLVED`:
   - operator may add up to 2 additional photos
8. Close rules:
   - can close if citizen confirmed resolved (`feedback.is_resolved=True`) **or** workflow round > 1
   - on close, citizen receives notification

## 5.4 Technician Workflow

1. Technician sees own incidents:
   - active (`IN_PROGRESS`)
   - resolved
   - closed
2. To resolve:
   - must be assigned technician
   - incident must be `IN_PROGRESS`
   - must submit report + **exactly 3 completion photos**
3. On successful resolve:
   - incident -> `RESOLVED`
   - technician workload decrements
   - citizen notified
   - operators notified

## 5.5 Admin Workflow

Custom user management is implemented in `users` app (not dependent on Django admin for business operations):

- list citizens/operators/technicians (paginated)
- add user by role
- delete user
- approve/unapprove operators and technicians
- view profile-level overall stats

Admin reports page:
- full incident list with filters (priority/assigned/status)
- paginated
- quick access to incident details

## 5.6 Notifications Logic

Notification events are triggered from incident actions:
- citizen incident creation -> operators
- assignment -> technician + citizen
- technician resolution -> citizen + operators
- citizen unresolved feedback -> operators
- operator/manual close -> citizen
- auto-close after timeout -> citizen + operators

Unread badge:
- `notifications.context_processors.unread_notifications`
- exposed globally as `unread_notification_count`

---

## 6. Backend Utilities and Important Functions

## Incident model workflow functions
- `assign_technician()`: validates role/specialization, updates status and workload, writes update log
- `mark_resolved()`: validates assigned technician, updates status/workload, writes update log
- `mark_closed()`: validates status, closes and logs update
- `close_if_overdue()`: auto-close resolved incidents with no feedback after 7 days

## Notification utilities
- `notify(user=..., incident=..., message=..., notification_type=...)`
- `notify_many(users=..., ...)`

## Forms with validation
- `IncidentCreationForm`: enforces OTHER category note
- `ResolutionForm`: completion report payload
- `FeedbackForm`: reason required when unresolved
- multi-file field for photo uploads

---

## 7. Templates and UI Data Contracts

Common context patterns used by templates:
- `page_obj`, `is_paginated` for pagination controls
- filter state dicts like `current_filters`
- `unread_notification_count` from context processor
- role-specific stats variables in profile/report pages

Base navbar behavior:
- role-aware navigation links
- global notifications link with unread badge
- role-aware profile link

---

## 8. Setup and Run

## Prerequisites
- Python 3.11+ (project currently configured with Python 3.14 environment on Windows)
- pip

## Install and migrate
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install django
python manage.py migrate
```

## Run server
```powershell
python manage.py runserver
```

## Optional: seed sample data
```powershell
python manage.py seed_sample_data --count 150
```

## Optional: auto-close overdue resolved incidents
```powershell
python manage.py auto_close_incidents
```

---

## 9. Key Operational Notes

- Citizens are auto-approved by model logic.
- Operators/technicians cannot work until admin approval.
- File upload constraints are enforced at both form layer and model layer.
- Workflow and status transition constraints are enforced in model methods.
- Incident lifecycle is audit-friendly via `IncidentUpdate`.
- Notification read/unread state is tracked per user.

---

## 10. Current Route Summary (Practical)

- `/users/` -> auth, profiles, admin user management
- `/incidents/` -> citizen/operator/technician incident operations
- `/notifications/` -> personal notification center
- `/reports/citizen/` -> citizen stats
- `/reports/technician/` -> technician stats
- `/reports/admin/` -> admin filtered incident reporting

