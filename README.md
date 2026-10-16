# 🏛️ CampusIQ — Full User-Facing Campus Space Management Application

> **Datathon 2026 Prototype — Track: Education Space Allocation**  
> *A full-featured campus space management application for Students, Faculty, and Campus Administrators.*

---

## 🎨 Visual Identity & UI Design

CampusIQ implements the clean, modern **AHLR Venture design language**:
* **Primary Deep Navy:** `#0B1424` (Headers, branding, active navigation tabs)
* **Accent Gold:** `#D9A02B` (Action buttons, score badges, status pills, highlights)
* **Surface Navy:** `#13223D` / **Border Navy:** `#1E345D`
* **Page Surface:** `#F5F7FA` / **Card Surfaces:** `#FFFFFF` with soft shadows
* **Typography:** Geometric Sans-Serif **Jost** (Google Fonts)

---

## 👥 Roles & Server-Side Permissions

CampusIQ implements server-side role authentication and authorization with 3 distinct personas:

| Role | Demo Account | Permissions & Workflows |
| :--- | :--- | :--- |
| **Student** | `student_alex` (Robotics Club Lead)<br>`student_priya` (ACM Chapter) | Search available rooms, submit space requests for study and clubs, track personal request history, cancel own requests, browse campus events, and RSVP. |
| **Faculty** | `prof_sharma` (CSE)<br>`prof_patel` (EEE) | Request spaces for academic lectures and lab exams, view departmental timetables, schedule guest lectures/seminars with conflict checking. |
| **Administrator** | `admin` (Facilities & Space Planning) | Master approval queue: approve requests with room assignment (with automated clash prevention), reject requests with mandatory reasons, manage schedules, resolve conflicts, and view analytics. |

*Quick Persona Switcher:* In the left sidebar, users and judges can switch between Student, Faculty, and Admin in **1 click** to evaluate each persona's unique view!

---

## 🏗️ Technical Architecture & Features

```
campus_sync_hackathon/
│
├── core/
│   ├── database.py             # SQLite transactional ACID database (users, rooms, schedule, events, requests, notifs)
│   ├── auth.py                 # Server-side authentication and role-based access control
│   ├── booking_service.py      # Request lifecycle (Submit -> Conflict Check -> Approve/Reject -> Cancel)
│   ├── event_service.py        # Campus event scheduling, turnout tracking, and RSVP management
│   ├── notification_service.py # In-app notification center for status updates and alerts
│   ├── matcher.py              # Multi-objective constraint-based smart room matcher
│   ├── conflict_detector.py    # Pairwise half-open [start, end) interval conflict detection
│   ├── analytics.py            # Non-duplicative interval-union scheduled utilization calculations
│   ├── recommendations.py      # Prioritized administrative recommendations
│   └── workflow_view.py        # Visual request lifecycle flowchart with dual branching
│
├── data/                       # Official DATATHON CSV datasets (rooms, schedule, events, requests)
├── tests/
│   ├── test_logic.py           # 12 unit tests for interval arithmetic and room constraints
│   └── test_application.py     # 10 unit tests for roles, booking approvals, and notifications
│
├── app.py                      # Full Streamlit Web Application (AHLR Venture Navy & Gold design)
├── campus_iq.db                # SQLite database persisting state across restarts
├── requirements.txt            # Minimal dependencies (streamlit, pandas, numpy, plotly, openpyxl)
├── RUN_CAMPUSIQ.bat            # Windows 1-click batch launcher
└── README.md                   # Documentation & user guide
```

---

## 🚀 How to Launch on Windows

### Method 1: One-Click Launcher (Recommended)
Double-click `RUN_CAMPUSIQ.bat` in the project root folder.

### Method 2: Manual Command
Open PowerShell or Command Prompt in the project folder and run:
```powershell
cd C:\Users\dadil\.gemini\antigravity\scratch\campus_sync_hackathon
py -3.13 -m streamlit run app.py
```
Then navigate to: **`http://localhost:8501`**

---

## 🧪 Automated Test Suite (22/22 Passing)

Run all unit and integration tests with:
```powershell
py -3.13 -m unittest discover -s tests -p "test_*.py"
```

```text
Ran 22 tests in 0.436s
OK
```

* **12 Interval & Constraint Tests (`tests/test_logic.py`):**
  - Half-open interval $[start, end)$ overlap validation.
  - Adjacent sessions ($[10, 12)$ and $[12, 14)$) do not trigger false conflicts.
  - Undersized rooms and missing equipment are rejected.
  - Non-duplicative interval union calculation prevents utilization from exceeding 100%.
* **10 Application & Workflow Tests (`tests/test_application.py`):**
  - Authentication and role enforcement across Student, Faculty, and Admin.
  - Student request submission and notification delivery.
  - Admin approval with room assignment commits allocation to database.
  - Duplicate simultaneous requests on the same room and time are blocked as conflicts.
  - Student cannot approve requests (server-side security guard).
  - Admin rejection requires an explanatory reason and notifies requester.
  - Student cancellation immediately frees the allocated room.
  - Event RSVP registration and cancellation.
  - Faculty event scheduling with room conflict verification.
  - Persistent state across database reconnects.

---

## 🧭 Dashboard Page Guide

1. **🏠 Home & Overview:** Role-tailored home page with summary metrics, building capacity breakdown, and quick action shortcuts.
2. **🔍 Room Search & Booking:** Interactive room search with capacity, equipment, date, and time filters; presents best candidate and 1-click request submission.
3. **📑 Bookings & Requests:**
   - *Student/Faculty View:* Personal request history with live status badges (`Pending`, `Approved`, `Rejected`, `Cancelled`) and cancellation button.
   - *Administrator View:* Approval queue to review requests, inspect candidate rooms, approve with room assignment, or reject with a reason.
4. **🗓️ Master Timetable:** Filterable weekly schedule by Weekday, Department, or Room.
5. **🎉 Campus Events:** Campus event listings, venue details, and student RSVP registration.
6. **🔄 Request Lifecycle Workflow:** Visual Mermaid decision flowchart, dual branching (Available vs Conflict), and historical request tracer.
7. **🔔 Notifications:** User inbox with unread badges, approval alerts, rejection reasons, and mark-as-read.
8. **⚙️ Profile & Settings:** Active user credentials, permissions breakdown, and database storage diagnostics.
