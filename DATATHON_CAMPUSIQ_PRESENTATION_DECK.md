# DATATHON 2026 — ROUND 1 IDEA PRESENTATION
## CampusIQ: Smart Campus Space Intelligence
**Track:** Education — *The Campus Has Space. Students Don't.*  
**Theme:** AHLR Venture UI & Decision Intelligence Framework

---

### Slide 1: Problem Statement
* **Target Users:** University students, student club leads (ACM, Robotics, Debate, Cultural), academic project teams, and facility scheduling administrators.
* **The Paradox:** Universities report severe classroom and laboratory shortages, resulting in 31.2% of student and club space requests being waitlisted or rejected.
* **Underlying Friction:** Rigid weekly timetables and fragmented event booking logs prevent campus managers from matching actual student demand to underutilized spaces and available equipment.

---

### Slide 2: Proposed Solution
* **CampusIQ** is an explainable decision intelligence prototype that synchronizes room inventory, recurring academic timetables, date-specific events, and student space requests.
* **Interval-Union Utilization:** Evaluates true scheduled load without artificially inflating utilization when overlapping sessions exist.
* **Constraint-Aware Matching:** Evaluates hard constraints (capacity, projectors, computers, accessibility, and zero timetable clash) to provide instant candidate recommendations and alternative time slots.

---

### Slide 3: Dataset & Genuine Empirical Findings
*All findings calculated directly from the official DATATHON datasets:*
* **120 Rooms (`rooms.csv`):** 5 campus zones (East, South, West, North, Central) totaling 11,316 seats (range: 15 to 179 seats).
* **5,000 Recurring Classes (`class_schedule.csv`):** Afternoon bottleneck between 12:00 PM and 5:00 PM accounts for over 50% of weekly timetable volume.
* **5,000 Space Requests (`room_requests.csv`):** 1,559 requests (31.2%) were unfulfilled (waitlisted or rejected) in the baseline records.
* **1,800 Recorded Events (`events.csv`):** 233 events showed severe turnout drops ($\ge 70\%$ drop from expected attendance), creating **20,439 wasted seat-hours**.
* **Timetable Conflicts:** Identified **6,791 conflict instances** (3,426 class overlaps, 19 event overlaps, 1,337 class-event clashes, and 2,009 capacity overflows).

---

### Slide 4: MVP Features
1. **Executive Overview Dashboard:** Data-derived KPIs with explicit mathematical definitions.
2. **Room Utilization Analytics:** Non-duplicative interval union calculation, department scheduling profiles, and turnout discrepancy analysis.
3. **Conflict Detection Engine:** Half-open interval $[start, end)$ clashing detection across classes, events, and capacity thresholds.
4. **Smart Room Finder:** Multi-objective transparent scoring, explainability rationale, and automated alternative time slot suggestions.
5. **Admin Recommendation Center:** Actionable policy interventions prioritized by measurable capacity gain.

---

### Slide 5: Unique Selling Proposition (USP) & Technical Approach

> **USP:**  
> *"CampusIQ turns fragmented campus schedules into actionable room-matching and allocation recommendations by combining recurring timetables, event commitments, room facilities, and student demand."*

* **Technical Stack:** Python 3.13, Streamlit, Pandas, NumPy, Plotly.
* **Interval Logic:** Half-open intervals $[start, end)$ prevent false positives on adjacent sessions ($[10, 12)$ and $[12, 14)$).
* **Transparent Scoring Formula:**
  $$\text{Score} = 0.45 \cdot S_{\text{capacity}} + 0.35 \cdot S_{\text{utilization}} + 0.20 \cdot S_{\text{amenities}}$$
* **AHLR Venture Styling:** Deep Navy (`#0B1424`), Accent Gold (`#D9A02B`), and Jost typography.

---

### Slide 6: Expected Impact & Future Roadmap
* **Immediate Operational Impact:**
  * Mitigates 6,791 detected timetable clashes and capacity overflows.
  * Reclaims 20,439 seat-hours from ghost-booked events via automated check-in grace policies.
  * Demonstrates a 99.0% feasible request match rate across the entire campus room inventory.
* **Round 2 Engineering Scope:**
  * Real-time IoT PIR sensor and WiFi access point telemetry integration.
  * Dynamic push notifications when nearby ghost rooms are released.
  * Single Sign-On (SSO) and Canvas/Blackboard LMS calendar sync.
