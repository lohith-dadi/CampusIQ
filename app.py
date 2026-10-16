"""
app.py
CampusIQ — Full User-Facing Campus Space Management Application
Datathon 2026 — Track: Education Space Allocation
Theme: AHLR Venture Design Language (Deep Navy #0B1424, Gold #D9A02B, Jost Typography, Crisp Surfaces)

Supports:
- 3 Roles: Student, Faculty, Administrator with Server-Side Authorization
- Room Search & Conflict-Aware Booking Engine
- Personal Request Tracking & Administrative Approval Queue
- Master Timetable & Campus Events with RSVP Registration
- Visual Request Lifecycle Workflow Page
- Notification Center & Profile Management
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CampusIQ | Campus Space Management",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# AHLR VENTURE THEME STYLING (NAVY #0B1424, GOLD #D9A02B, JOST FONT)
# ==============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* Global Typography & Palette */
    html, body, [class*="css"], .stApp {
        font-family: 'Jost', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #0B1424;
        background-color: #F5F7FA;
    }
    
    /* Top Brand Header */
    .campusiq-topbar {
        background: linear-gradient(135deg, #0B1424 0%, #13223D 100%);
        border-bottom: 3px solid #D9A02B;
        border-radius: 12px;
        padding: 20px 28px;
        color: #FFFFFF;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -3px rgba(11, 20, 36, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 14px;
    }
    .campusiq-topbar-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .campusiq-topbar-sub {
        color: #D9A02B;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 4px;
    }
    
    /* Pills & Status Badges */
    .pill-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .pill-gold { background: #FBF6EC; color: #0B1424; border: 1px solid #D9A02B; }
    .pill-navy { background: #1E345D; color: #FFFFFF; border: 1px solid #334E7B; }
    .pill-green { background: #E6F4EA; color: #137333; border: 1px solid #34A853; }
    .pill-red { background: #FCE8E6; color: #C5221F; border: 1px solid #EA4335; }
    .pill-amber { background: #FEF3C7; color: #92400E; border: 1px solid #F59E0B; }
    
    /* Metric & Action Cards */
    .iq-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(11, 20, 36, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .iq-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px -2px rgba(11, 20, 36, 0.09);
        border-color: #D9A02B;
    }
    .iq-card-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #718096;
        margin-bottom: 6px;
    }
    .iq-card-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0B1424;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .iq-card-sub {
        font-size: 0.78rem;
        color: #4A5568;
        line-height: 1.4;
    }
    
    /* User Profile Card in Sidebar */
    .user-profile-box {
        background: #13223D;
        border: 1px solid #1E345D;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 16px;
        color: white;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #D9A02B !important;
        color: #0B1424 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 9px 20px !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.02em !important;
    }
    .stButton > button:hover {
        background-color: #C38D22 !important;
        box-shadow: 0 4px 12px rgba(217, 160, 43, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# Core Imports
from core.database import initialize_database, get_db_connection
from core.auth import (
    authenticate, get_all_demo_users, get_current_user, set_current_user,
    is_admin, is_faculty, is_student, check_permission
)
from core.booking_service import BookingService
from core.event_service import EventService
from core.notification_service import NotificationService
from core.matcher import SmartRoomMatcher
from core.conflict_detector import ConflictDetector
from core.analytics import CampusAnalytics
from core.recommendations import RecommendationEngine
from core.workflow_view import render_workflow_page

# Ensure DB initialized
initialize_database()

# Load Cached Relational Datasets
@st.cache_data
def get_cached_static_tables():
    conn = get_db_connection()
    rooms = pd.read_sql_query("SELECT * FROM rooms;", conn)
    schedule = pd.read_sql_query("SELECT * FROM class_schedule;", conn)
    events = pd.read_sql_query("SELECT * FROM events;", conn)
    reqs = pd.read_sql_query("SELECT * FROM booking_requests ORDER BY created_at DESC;", conn)
    conn.close()
    return rooms, schedule, events, reqs

@st.cache_data
def get_cached_analytics_and_conflicts(op_start: float, op_end: float):
    rooms, schedule, events, reqs = get_cached_static_tables()
    analytics = CampusAnalytics(rooms, schedule, events, reqs)
    kpi_dict = analytics.get_overall_kpis(op_start, op_end, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    util_df = kpi_dict["utilization_df"]
    detector = ConflictDetector(rooms, schedule, events)
    conflicts_dict = detector.detect_all_conflicts()
    rec_engine = RecommendationEngine(rooms, schedule, events, reqs, util_df, conflicts_dict)
    admin_recs = rec_engine.generate_recommendations()
    return kpi_dict, util_df, conflicts_dict, admin_recs

@st.cache_resource
def get_cached_matcher():
    rooms, schedule, events, _ = get_cached_static_tables()
    _, util_df, _, _ = get_cached_analytics_and_conflicts(8.0, 20.0)
    return SmartRoomMatcher(rooms, schedule, events, util_df)

rooms_df, schedule_df, events_df, requests_df = get_cached_static_tables()
kpi_dict, util_df, conflicts_dict, admin_recs = get_cached_analytics_and_conflicts(8.0, 20.0)
matcher = get_cached_matcher()
db_tables = {"rooms": rooms_df, "schedule": schedule_df, "events": events_df, "requests": requests_df}

# Session State Setup
all_demo_users = get_all_demo_users()
if "current_user" not in st.session_state:
    st.session_state["current_user"] = all_demo_users[0] # Default to Admin

current_user = get_current_user()
unread_notifs = NotificationService.get_unread_count(current_user["id"]) if current_user else 0

# ==============================================================================
# SIDEBAR NAVIGATION & PERSONA SWITCHER
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="background:#0B1424; padding:16px; border-radius:8px; border-left:4px solid #D9A02B; color:white; margin-bottom:14px;">
        <div style="font-size:1.35rem; font-weight:800; color:#FFFFFF;">🏛️ CampusIQ</div>
        <div style="font-size:0.8rem; color:#D9A02B; font-weight:600;">Campus Space Intelligence & Management</div>
    </div>
    """, unsafe_allow_html=True)
    
    # User Profile Box
    role_color = "pill-gold" if current_user["role"] == "admin" else ("pill-navy" if current_user["role"] == "faculty" else "pill-green")
    st.markdown(f"""
    <div class="user-profile-box">
        <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; color:#94A3B8; font-weight:700;">Active Persona</div>
        <div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:2px;">{current_user['full_name']}</div>
        <div style="font-size:0.78rem; color:#E2E8F0; margin-bottom:8px;">{current_user['department']}</div>
        <span class="pill-badge {role_color}">Role: {current_user['role'].upper()}</span>
        <span class="pill-badge pill-navy">🔔 {unread_notifs} New</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 1-Click Persona Switcher for Hackathon Evaluation
    user_names = [f"{u['full_name']} ({u['role'].capitalize()})" for u in all_demo_users]
    current_idx = next((i for i, u in enumerate(all_demo_users) if u["id"] == current_user["id"]), 0)
    selected_user_str = st.selectbox("Switch Persona / Role", user_names, index=current_idx)
    selected_user = all_demo_users[user_names.index(selected_user_str)]
    if selected_user["id"] != current_user["id"]:
        set_current_user(selected_user)
        st.rerun()

    st.markdown("### 🧭 Main Navigation")
    
    # Navigation list customized by role
    nav_options = [
        "🏠 Home & Overview",
        "🔍 Room Search & Booking",
        "📑 Bookings & Requests",
        "🗓️ Master Timetable",
        "🎉 Campus Events",
        "🔄 Request Lifecycle Workflow",
        f"🔔 Notifications ({unread_notifs})",
        "⚙️ Profile & Settings"
    ]
    
    selected_page = st.radio("Navigation Menu", nav_options, label_visibility="collapsed")
    
    st.divider()
    st.markdown("### ⚙️ Operating Assumptions")
    st.caption("Configurable operating window for scheduled utilization calculation.")
    op_start = st.number_input("Opening Hour", 6.0, 10.0, 8.0, 0.5, format="%.1f")
    op_end = st.number_input("Closing Hour", 17.0, 23.0, 20.0, 0.5, format="%.1f")

# Top Header Bar
st.markdown(f"""
<div class="campusiq-topbar">
    <div>
        <div class="campusiq-topbar-title">🏛️ CampusIQ Space Management</div>
        <div class="campusiq-topbar-sub">Smart Room Matching, Timetable Synchronization & Allocation Management</div>
    </div>
    <div>
        <span class="pill-badge pill-gold">User: {current_user['full_name']}</span>
        <span class="pill-badge {role_color}">{current_user['role'].upper()} ACCESS</span>
        <span class="pill-badge pill-navy">DB: SQLite Transactional (ACID)</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: 🏠 HOME & OVERVIEW
# ==============================================================================
if selected_page == "🏠 Home & Overview":
    st.markdown(f"### 👋 Welcome back, {current_user['full_name']}!")
    st.caption(f"Logged in as **{current_user['role'].capitalize()}** in **{current_user['department']}**.")
    
    # Role-Specific Welcome Cards
    if is_student():
        st.info("🎓 **Student Hub:** Search for available study rooms, submit club space requests, track your booking approvals, and explore campus workshops.")
        sc1, sc2, sc3 = st.columns(3)
        my_reqs = BookingService.get_requests_for_user(current_user["id"])
        with sc1:
            st.markdown(f"""
            <div class="iq-card">
                <div class="iq-card-title">My Total Requests</div>
                <div class="iq-card-value">{len(my_reqs)}</div>
                <div class="iq-card-sub">Submitted space requests across capstone, clubs, and study groups.</div>
            </div>
            """, unsafe_allow_html=True)
        with sc2:
            appr = sum(1 for r in my_reqs if r["status"] == "Approved")
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #1E8E3E;">
                <div class="iq-card-title">Approved Bookings</div>
                <div class="iq-card-value" style="color:#1E8E3E;">{appr}</div>
                <div class="iq-card-sub">Confirmed space reservations with room allocations.</div>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            user_evs = len(EventService.get_user_registered_event_ids(current_user["id"]))
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #D9A02B;">
                <div class="iq-card-title">My Event RSVPs</div>
                <div class="iq-card-value" style="color:#D9A02B;">{user_evs}</div>
                <div class="iq-card-sub">Campus workshops and club meetings you've registered for.</div>
            </div>
            """, unsafe_allow_html=True)

    elif is_faculty():
        st.info("👨‍🏫 **Faculty Portal:** Schedule department review sessions, request lecture auditoriums, view the department timetable, and announce academic seminars.")
        fc1, fc2, fc3 = st.columns(3)
        my_reqs = BookingService.get_requests_for_user(current_user["id"])
        with fc1:
            st.markdown(f"""
            <div class="iq-card">
                <div class="iq-card-title">My Academic Requests</div>
                <div class="iq-card-value">{len(my_reqs)}</div>
                <div class="iq-card-sub">Special lectures, exam reviews, and lab sessions.</div>
            </div>
            """, unsafe_allow_html=True)
        with fc2:
            dept_classes = len(schedule_df[schedule_df["department"] == "CSE"])
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #3B82F6;">
                <div class="iq-card-title">Department Classes</div>
                <div class="iq-card-value">{dept_classes:,}</div>
                <div class="iq-card-sub">Weekly scheduled classes in Computer Science & Engineering.</div>
            </div>
            """, unsafe_allow_html=True)
        with fc3:
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #D9A02B;">
                <div class="iq-card-title">Campus Utilization</div>
                <div class="iq-card-value" style="color:#D9A02B;">{kpi_dict['campus_scheduled_utilization_pct']}%</div>
                <div class="iq-card-sub">Scheduled classroom and lab utilization across campus.</div>
            </div>
            """, unsafe_allow_html=True)

    else: # Administrator
        st.info("🏛️ **Administrator Command Center:** Review pending space requests, resolve timetable conflicts, monitor scheduled utilization, and oversee campus facility policy.")
        pending_cnt = len(BookingService.get_all_requests(status_filter="Pending", limit=500))
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #D9A02B;">
                <div class="iq-card-title">Pending Approvals</div>
                <div class="iq-card-value" style="color:#D9A02B;">{pending_cnt}</div>
                <div class="iq-card-sub">Requests awaiting room assignment in the Approval Queue.</div>
            </div>
            """, unsafe_allow_html=True)
        with ac2:
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #D93025;">
                <div class="iq-card-title">Schedule Conflicts</div>
                <div class="iq-card-value" style="color:#D93025;">{conflicts_dict['total_conflicts']}</div>
                <div class="iq-card-sub">Timetable overlaps and capacity overflows in raw schedules.</div>
            </div>
            """, unsafe_allow_html=True)
        with ac3:
            st.markdown(f"""
            <div class="iq-card">
                <div class="iq-card-title">Scheduled Utilization</div>
                <div class="iq-card-value">{kpi_dict['campus_scheduled_utilization_pct']}%</div>
                <div class="iq-card-sub">{kpi_dict['total_occupied_union_hours']:,} union hours / {kpi_dict['total_available_hours']:,} total available.</div>
            </div>
            """, unsafe_allow_html=True)
        with ac4:
            st.markdown(f"""
            <div class="iq-card" style="border-left:4px solid #1E8E3E;">
                <div class="iq-card-title">Room Inventory</div>
                <div class="iq-card-value" style="color:#1E8E3E;">{len(rooms_df)}</div>
                <div class="iq-card-sub">11,316 total seats across East, South, West, North, Central.</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # Campus Space Visual Breakdown
    col_chart1, col_chart2 = st.columns([1.2, 1])
    with col_chart1:
        st.markdown("#### 🏢 Campus Building Capacity & Utilization")
        bldg_agg = rooms_df.groupby("building").agg(
            total_seats=("capacity", "sum"),
            rooms_count=("room_id", "count")
        ).reset_index()
        fig_bldg = px.bar(
            bldg_agg, x="building", y="total_seats", color="rooms_count",
            color_continuous_scale=[[0, "#13223D"], [1, "#D9A02B"]],
            labels={"building": "Building", "total_seats": "Total Seating Capacity", "rooms_count": "Room Count"},
            title="Seating Capacity by Campus Zone"
        )
        fig_bldg.update_layout(template="plotly_white", margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_bldg, use_container_width=True)

    with col_chart2:
        st.markdown("#### 💡 Urgent Recommendations for Space Managers")
        for rec in admin_recs[:3]:
            st.markdown(f"""
            <div class="rec-item">
                <div style="font-weight:700; color:#0B1424;">{rec['title']}</div>
                <div style="font-size:0.78rem; color:#4A5568; margin-top:4px;">{rec['evidence']}</div>
                <div style="font-size:0.75rem; color:#D9A02B; font-weight:700; margin-top:4px;">Impact: {rec['impact_metric']}</div>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: 🔍 ROOM SEARCH & BOOKING
# ==============================================================================
elif selected_page == "🔍 Room Search & Booking":
    st.markdown("### 🔍 Search Available Rooms & Submit Booking Request")
    st.caption("Filters campus room inventory using strict interval-based clash checks [start, end) against recurring timetables, events, and confirmed bookings.")
    
    col_search_form, col_search_results = st.columns([1, 1.4])
    
    with col_search_form:
        st.markdown("#### 📝 Booking Requirements")
        with st.container(border=True):
            b_purpose = st.text_input("Booking Purpose / Event Title", value="Project Collaboration Meeting")
            b_pax = st.slider("Number of Attendees", 2, 160, 35)
            
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                b_date = st.date_input("Date", value=datetime(2025, 9, 15))
                b_date_str = b_date.strftime("%Y-%m-%d")
                b_weekday = b_date.strftime("%a")
            with c_d2:
                st.markdown(f"**Day:** `{b_weekday}`")
                
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                b_start = st.slider("Start Hour", 8.0, 21.0, 14.0, 0.5, format="%.1f")
            with c_t2:
                b_dur = st.slider("Duration (Hours)", 0.5, 4.0, 2.0, 0.5)
                
            st.markdown("##### 🔌 Facilities Required")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                b_proj = st.checkbox("High-Lumen Projector", value=True)
                b_comp = st.checkbox("Computer Workstations", value=False)
            with c_f2:
                b_access = st.checkbox("Wheelchair Accessible", value=True)
                b_outlets = st.number_input("Min Power Outlets", 0, 30, 4)
                
            c_pref1, c_pref2 = st.columns(2)
            with c_pref1:
                b_bldg = st.selectbox("Preferred Building", ["Any", "Central", "East", "West", "North", "South"])
            with c_pref2:
                b_rtype = st.selectbox("Preferred Room Type", ["Any", "Classroom", "Lab", "Seminar", "Study room", "Auditorium"])
                
            search_trigger = st.button("🔎 Search Feasible Rooms", type="primary", use_container_width=True)

    with col_search_results:
        st.markdown("#### 🏆 Feasible Candidate Rooms (Ranked by Multi-Objective Score)")
        
        candidates_result = matcher.find_candidates(
            required_capacity=b_pax,
            weekday=b_weekday,
            start_hour=b_start,
            duration_hours=b_dur,
            event_date=b_date_str,
            projector_required=b_proj,
            computers_required=b_comp,
            accessible_required=b_access,
            min_power_outlets=b_outlets,
            preferred_building=b_bldg,
            preferred_room_type=b_rtype
        )
        
        feasible_list = candidates_result["feasible_candidates"]
        
        if feasible_list:
            st.success(f"✓ Found **{len(feasible_list)} feasible candidate rooms** with zero scheduling conflict.")
            best_room = candidates_result["best_candidate"]
            
            # Featured Best Match
            st.markdown(f"""
            <div style="background:#0B1424; color:white; border-radius:10px; padding:18px; border:2px solid #D9A02B; margin-bottom:16px;">
                <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#D9A02B; font-weight:700;">★ Best Recommended Candidate</div>
                <div style="font-size:1.6rem; font-weight:800; color:#FFFFFF;">Room {best_room['room_id']} — {best_room['building']} Building</div>
                <div style="font-size:0.9rem; color:#E2E8F0; margin-top:4px;">
                    <b>{best_room['room_type']}</b> • Capacity: <b>{best_room['capacity']} seats</b> • Floor {best_room['floor']} • Score: <b style="color:#D9A02B;">{best_room['score']}/100</b>
                </div>
                <div style="font-size:0.85rem; color:#94A3B8; margin-top:8px;">💡 {best_room['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Request Submission Card
            with st.container(border=True):
                st.markdown(f"##### 🚀 Submit Request for Room {best_room['room_id']}")
                st.caption(f"Submit request for **{b_purpose}** ({b_pax} attendees) on **{b_date_str}** from **{b_start:04.1f} to {b_start+b_dur:04.1f}**.")
                if st.button("📤 Submit Request for Administrative Review", key="submit_req_btn"):
                    try:
                        res = BookingService.create_request(
                            user_id=current_user["id"],
                            requester_name=current_user["full_name"],
                            requester_role=current_user["role"],
                            purpose=b_purpose,
                            required_capacity=b_pax,
                            request_date=b_date_str,
                            weekday=b_weekday,
                            start_hour=b_start,
                            duration_hours=b_dur,
                            projector_required=b_proj,
                            computers_required=b_comp,
                            accessible_required=b_access,
                            min_power_outlets=b_outlets,
                            preferred_building=b_bldg,
                            preferred_room_type=b_rtype
                        )
                        st.success(f"🎉 **Request Submitted!** Request ID: `{res['request_id']}`. Track status in 'Bookings & Requests'.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error submitting request: {e}")
                        
            st.markdown("##### Other Feasible Alternatives")
            for alt in feasible_list[1:5]:
                with st.container(border=True):
                    a_c1, a_c2 = st.columns([3, 1])
                    with a_c1:
                        st.markdown(f"**Room {alt['room_id']}** ({alt['building']} • {alt['room_type']} • {alt['capacity']} seats)")
                        st.caption(f"Score: **{alt['score']}** | Scheduled Load: **{alt['scheduled_utilization_pct']}%** | Outlets: **{alt['power_outlets']}**")
                        st.caption(f"Reason: {alt['explanation']}")
                    with a_c2:
                        if st.button(f"Request {alt['room_id']}", key=f"req_alt_{alt['room_id']}"):
                            res = BookingService.create_request(
                                user_id=current_user["id"],
                                requester_name=current_user["full_name"],
                                requester_role=current_user["role"],
                                purpose=b_purpose,
                                required_capacity=b_pax,
                                request_date=b_date_str,
                                weekday=b_weekday,
                                start_hour=b_start,
                                duration_hours=b_dur,
                                preferred_building=alt["building"],
                                preferred_room_type=alt["room_type"]
                            )
                            st.success(f"Submitted request `{res['request_id']}` for Room {alt['room_id']}!")
        else:
            st.error("⚠️ No candidate room satisfies all hard constraints for this requested time.")
            rej = candidates_result["rejection_summary"]
            st.markdown(f"""
            **Rejection Analysis:**
            - Insufficient Capacity: **{rej['capacity']} rooms**
            - Missing Equipment: **{rej['equipment']} rooms**
            - Class Timetable Clash: **{rej['class_conflict']} rooms**
            - Recorded Event Clash: **{rej['event_conflict']} rooms**
            """)
            if candidates_result["alternative_slots"]:
                st.markdown("##### 💡 Feasible Alternative Time Slots")
                for alt_s in candidates_result["alternative_slots"]:
                    st.info(f"🕒 **Slot {alt_s['suggested_start_hour']} - {alt_s['suggested_end_hour']}**: Candidate **Room {alt_s['example_room_id']}** ({alt_s['room_type']}, {alt_s['room_capacity']} seats) in {alt_s['building']} is available.")


# ==============================================================================
# PAGE 3: 📑 BOOKINGS & REQUESTS (USER TRACKING + ADMIN APPROVAL QUEUE)
# ==============================================================================
elif selected_page == "📑 Bookings & Requests":
    st.markdown("### 📑 Space Bookings & Request Management")
    st.caption("Track request lifecycle states, view assigned spaces, and process administrative approvals.")
    
    # Dual View: Personal User Requests vs. Admin Approval Queue
    if is_admin():
        admin_tab1, admin_tab2 = st.tabs(["🏛️ Administrative Approval Queue", "👤 My Personal Requests"])
        
        with admin_tab1:
            st.markdown("#### 🏛️ Master Booking Request Approval Queue")
            st.caption("Review incoming space requests, verify availability, assign rooms, or provide rejection reasons.")
            
            queue_filter = st.selectbox("Queue Filter by Status", ["Pending", "Approved", "Rejected", "Cancelled", "All"], index=0)
            all_reqs = BookingService.get_all_requests(status_filter=queue_filter, limit=100)
            
            if not all_reqs:
                st.info(f"No requests currently matching status '{queue_filter}'.")
            else:
                for req in all_reqs[:15]:
                    with st.container(border=True):
                        rq1, rq2, rq3 = st.columns([2.5, 2, 1.5])
                        with rq1:
                            st.markdown(f"**Request ID:** `{req['request_id']}`")
                            st.markdown(f"**Requester:** {req['requester_name']} (*{req['requester_role'].capitalize()}*)")
                            st.markdown(f"**Purpose:** {req['purpose']}")
                            st.caption(f"Attendees: **{req['required_capacity']}** • Date: **{req['request_date']} ({req['weekday']})** • Time: **{req['start_hour']:04.1f} - {req['end_hour']:04.1f}**")
                        with rq2:
                            status_badge = "pill-amber" if req["status"] == "Pending" else ("pill-green" if req["status"] == "Approved" else "pill-red")
                            st.markdown(f"<span class='pill-badge {status_badge}'>{req['status'].upper()}</span>", unsafe_allow_html=True)
                            if req["assigned_room_id"]:
                                st.markdown(f"**Assigned Room:** `{req['assigned_room_id']}`")
                            if req["rejection_reason"]:
                                st.caption(f"Reason: *{req['rejection_reason']}*")
                            st.caption(f"Submitted: {req['created_at']}")
                        with rq3:
                            if req["status"] == "Pending":
                                # Find candidate rooms for quick assignment
                                candidates = matcher.find_candidates(
                                    required_capacity=req["required_capacity"],
                                    weekday=req["weekday"],
                                    start_hour=req["start_hour"],
                                    duration_hours=req["duration_hours"],
                                    event_date=req["request_date"],
                                    projector_required=bool(req["projector_required"]),
                                    computers_required=bool(req["computers_required"])
                                )["feasible_candidates"]
                                
                                candidate_room_ids = [c["room_id"] for c in candidates[:8]]
                                if not candidate_room_ids:
                                    candidate_room_ids = rooms_df[rooms_df["capacity"] >= req["required_capacity"]]["room_id"].head(5).tolist()
                                    
                                chosen_room = st.selectbox("Assign Room", candidate_room_ids, key=f"assign_{req['request_id']}")
                                
                                if st.button("✓ Approve", key=f"appr_btn_{req['request_id']}", type="primary"):
                                    try:
                                        res = BookingService.approve_request(req["request_id"], chosen_room, current_user["id"])
                                        st.success(res["message"])
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Approval failed: {e}")
                                        
                                rej_reason = st.text_input("Rejection Reason", value="Schedule saturation", key=f"rej_txt_{req['request_id']}")
                                if st.button("✕ Reject", key=f"rej_btn_{req['request_id']}"):
                                    try:
                                        res = BookingService.reject_request(req["request_id"], rej_reason, current_user["id"])
                                        st.warning(res["message"])
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Rejection failed: {e}")
                                        
        with admin_tab2:
            st.markdown("#### 👤 Requests Submitted by You")
            my_reqs = BookingService.get_requests_for_user(current_user["id"])
            if my_reqs:
                st.dataframe(pd.DataFrame(my_reqs)[["request_id", "purpose", "request_date", "weekday", "start_hour", "end_hour", "status", "assigned_room_id", "created_at"]], use_container_width=True, hide_index=True)
            else:
                st.info("You have not submitted any personal space requests yet.")

    else: # Student & Faculty Personal View
        st.markdown(f"#### 👤 My Space Requests ({current_user['full_name']})")
        my_reqs = BookingService.get_requests_for_user(current_user["id"])
        
        if not my_reqs:
            st.info("You have not submitted any booking requests yet. Use 'Room Search & Booking' to request spaces!")
        else:
            for req in my_reqs:
                with st.container(border=True):
                    r_c1, r_c2, r_c3 = st.columns([3, 2, 1.2])
                    with r_c1:
                        st.markdown(f"**Request ID:** `{req['request_id']}` — **{req['purpose']}**")
                        st.caption(f"Attendees: **{req['required_capacity']}** • Date: **{req['request_date']} ({req['weekday']})** • Time: **{req['start_hour']:04.1f} - {req['end_hour']:04.1f}**")
                        if req["assigned_room_id"]:
                            st.success(f"🎉 **Allocated Space:** Room `{req['assigned_room_id']}` is confirmed for your session!")
                        if req["rejection_reason"]:
                            st.error(f"Rejection Reason: *{req['rejection_reason']}*")
                    with r_c2:
                        s_pill = "pill-green" if req["status"] == "Approved" else ("pill-amber" if req["status"] == "Pending" else "pill-red")
                        st.markdown(f"<span class='pill-badge {s_pill}'>Status: {req['status'].upper()}</span>", unsafe_allow_html=True)
                        st.caption(f"Created: {req['created_at']}")
                    with r_c3:
                        if req["status"] in ["Pending", "Approved"]:
                            if st.button("Cancel Request", key=f"cancel_{req['request_id']}"):
                                try:
                                    res = BookingService.cancel_request(req["request_id"], current_user["id"])
                                    st.info(res["message"])
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error cancelling request: {e}")


# ==============================================================================
# PAGE 4: 🗓️ MASTER TIMETABLE
# ==============================================================================
elif selected_page == "🗓️ Master Timetable":
    st.markdown("### 🗓️ Master Campus Timetable & Schedule Explorer")
    st.caption("Synchronized view of recurring academic classes and confirmed room allocations.")
    
    col_t_filt1, col_t_filt2, col_t_filt3 = st.columns(3)
    with col_t_filt1:
        tt_day = st.selectbox("Filter Weekday", ["All", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    with col_t_filt2:
        tt_dept = st.selectbox("Filter Department", ["All"] + sorted(list(schedule_df["department"].unique())))
    with col_t_filt3:
        tt_room = st.selectbox("Filter Room", ["All"] + sorted(list(rooms_df["room_id"].unique())))
        
    filtered_sched = schedule_df.copy()
    if tt_day != "All":
        filtered_sched = filtered_sched[filtered_sched["weekday"] == tt_day]
    if tt_dept != "All":
        filtered_sched = filtered_sched[filtered_sched["department"] == tt_dept]
    if tt_room != "All":
        filtered_sched = filtered_sched[filtered_sched["room_id"] == tt_room]
        
    st.markdown(f"**Showing {len(filtered_sched):,} scheduled classes matching filters:**")
    st.dataframe(
        filtered_sched[["schedule_id", "course_code", "department", "room_id", "weekday", "start_hour", "end_hour", "duration_hours", "expected_attendance"]].head(100),
        use_container_width=True, hide_index=True
    )


# ==============================================================================
# PAGE 5: 🎉 CAMPUS EVENTS
# ==============================================================================
elif selected_page == "🎉 Campus Events":
    st.markdown("### 🎉 Campus Events, Seminars & Workshops")
    st.caption("Explore upcoming campus gatherings, RSVP for attendance, and inspect venue turnout telemetry.")
    
    ev_types = ["All"] + sorted(list(events_df["event_type"].unique()))
    chosen_type = st.selectbox("Filter by Event Type", ev_types)
    
    event_list = EventService.get_all_events(event_type_filter=chosen_type, limit=50)
    user_registered_ids = EventService.get_user_registered_event_ids(current_user["id"])
    
    st.write("")
    for ev in event_list[:15]:
        is_registered = ev["event_id"] in user_registered_ids
        with st.container(border=True):
            e_c1, e_c2, e_c3 = st.columns([3, 1.8, 1.2])
            with e_c1:
                st.markdown(f"#### {ev['title'] or ev['event_type']}")
                st.markdown(f"**Venue:** Room `{ev['room_id']}` ({ev['building']} Building • {ev['room_type']})")
                st.caption(f"Organizer: **{ev['organizer']}** • Expected: **{ev['expected_attendance']} attendees**")
            with e_c2:
                st.markdown(f"📅 **Date:** `{ev['event_date']} ({ev['weekday']})`")
                st.markdown(f"🕒 **Time:** `{ev['start_hour']:04.1f} - {ev['end_hour']:04.1f} ({ev['duration_hours']:.0f} hrs)`")
                if ev["is_ghost_booking"]:
                    st.markdown("<span class='pill-badge pill-red'>⚡ Ghost Event Flagged (Low Turnout)</span>", unsafe_allow_html=True)
            with e_c3:
                if is_registered:
                    st.success("✓ Registered")
                    if st.button("Cancel RSVP", key=f"unreg_{ev['event_id']}"):
                        EventService.cancel_registration(ev["event_id"], current_user["id"])
                        st.info("RSVP cancelled.")
                        st.rerun()
                else:
                    if st.button("Register / RSVP", key=f"reg_{ev['event_id']}", type="primary"):
                        res = EventService.register_for_event(ev["event_id"], current_user["id"])
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()


# ==============================================================================
# PAGE 6: 🔄 REQUEST LIFECYCLE WORKFLOW
# ==============================================================================
elif selected_page == "🔄 Request Lifecycle Workflow":
    render_workflow_page(db_tables, matcher, {"kpi_dict": kpi_dict, "recommendations": admin_recs})


# ==============================================================================
# PAGE 7: 🔔 NOTIFICATIONS
# ==============================================================================
elif selected_page.startswith("🔔 Notifications"):
    st.markdown(f"### 🔔 Notification Center ({current_user['full_name']})")
    st.caption("Real-time alerts for booking approvals, rejections, cancellations, and event RSVPs.")
    
    col_notif_act1, col_notif_act2 = st.columns([3, 1])
    with col_notif_act2:
        if st.button("Mark All as Read"):
            NotificationService.mark_all_as_read(current_user["id"])
            st.rerun()
            
    user_notifs = NotificationService.get_notifications_for_user(current_user["id"])
    if not user_notifs:
        st.info("No notifications yet! When you submit requests or register for events, alerts will appear here.")
    else:
        for n in user_notifs:
            n_color = "pill-green" if n["category"] == "success" else ("pill-red" if n["category"] == "warning" else "pill-navy")
            with st.container(border=True):
                st.markdown(f"<span class='pill-badge {n_color}'>{n['category'].upper()}</span> **{n['title']}**", unsafe_allow_html=True)
                st.write(n["message"])
                st.caption(f"Timestamp: {n['created_at']}")
                if not n["is_read"]:
                    if st.button("Mark Read", key=f"read_{n['id']}"):
                        NotificationService.mark_as_read(n["id"], current_user["id"])
                        st.rerun()


# ==============================================================================
# PAGE 8: ⚙️ PROFILE & SETTINGS
# ==============================================================================
elif selected_page == "⚙️ Profile & Settings":
    st.markdown("### ⚙️ User Profile & System Information")
    st.caption("Active user credentials, role permissions, and database diagnostics.")
    
    col_p1, col_p2 = st.columns([1, 1.2])
    with col_p1:
        with st.container(border=True):
            st.markdown("#### 👤 Account Details")
            st.markdown(f"**Full Name:** `{current_user['full_name']}`")
            st.markdown(f"**Username:** `{current_user['username']}`")
            st.markdown(f"**Email:** `{current_user['email']}`")
            st.markdown(f"**Assigned Role:** `{current_user['role'].upper()}`")
            st.markdown(f"**Department:** `{current_user['department']}`")
            
            st.markdown("##### 🛡️ Role Privileges")
            if is_admin():
                st.write("✓ Full administrative queue access\n✓ Approve and reject space requests\n✓ Manage campus schedules & events\n✓ View conflict analytics")
            elif is_faculty():
                st.write("✓ Request academic lecture/lab rooms\n✓ Schedule department seminars & guest lectures\n✓ View department timetables\n✓ RSVP to campus events")
            else:
                st.write("✓ Search available campus spaces\n✓ Submit club and project space requests\n✓ Cancel personal requests\n✓ RSVP to campus events")

    with col_p2:
        with st.container(border=True):
            st.markdown("#### 🗄️ Database & Storage Diagnostics")
            st.markdown(f"**Database Engine:** SQLite (Transactional ACID)")
            st.markdown(f"**Location:** `campus_iq.db`")
            st.markdown(f"**Rooms Loaded:** `{len(rooms_df)} rooms`")
            st.markdown(f"**Classes Synchronized:** `{len(schedule_df):,} records`")
            st.markdown(f"**Events Loaded:** `{len(events_df):,} records`")
            st.markdown(f"**Total Requests Tracked:** `{len(requests_df):,} requests`")
            st.success("✓ Server-side validation and persistence active.")

st.divider()
st.markdown("""
<div style="text-align:center; color:#718096; font-size:0.8rem; padding:12px 0;">
    <b>CampusIQ — Smart Campus Space Intelligence</b> • DATATHON 2026 Education Space Allocation Prototype • Powered by Python & Streamlit
</div>
""", unsafe_allow_html=True)
