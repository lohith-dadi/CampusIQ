"""
data_generator.py
Synthetic data generator for CampusSync AI.
Generates realistic data for rooms, facilities, bookings, IoT sensor feeds, and demand patterns.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

BUILDINGS = [
    {"name": "Alan Turing Science & Tech Hub", "code": "AT", "lat": 12.9716, "lon": 77.5946, "zones": ["Lab Wing", "East Lecture Hall", "Research Floor"]},
    {"name": "Aryabhata Academic Complex", "code": "AR", "lat": 12.9725, "lon": 77.5955, "zones": ["North Classrooms", "Seminar Center", "Annex"]},
    {"name": "Ramanujan Innovation & Club Center", "code": "RC", "lat": 12.9708, "lon": 77.5938, "zones": ["Student Union", "Maker Space", "Auditorium Wing"]},
    {"name": "Central Learning & Library Commons", "code": "LC", "lat": 12.9730, "lon": 77.5962, "zones": ["Quiet Study Core", "Group Collab Pods", "Mezzanine"]}
]

ROOM_TYPES = ["Classroom", "Laboratory", "Seminar Room", "Study Space"]

AMENITIES_POOL = [
    "High-Lumen Projector",
    "Dual 4K Displays",
    "High-Performance GPU Workstations",
    "Audio PA & Mic System",
    "Smart Whiteboard",
    "Video Conferencing Rig",
    "Lab Fume Hoods & Benches",
    "Acoustic Soundproofing",
    "Ergonomic Modular Desks",
    "High-Speed Gigabit LAN"
]

def generate_rooms(num_rooms=45):
    rooms = []
    room_id = 101
    
    for i in range(num_rooms):
        bldg = np.random.choice(BUILDINGS)
        rtype = np.random.choice(ROOM_TYPES, p=[0.35, 0.20, 0.25, 0.20])
        
        # Realistic capacity based on type
        if rtype == "Classroom":
            cap = int(np.random.choice([40, 60, 80, 120]))
            amenities = list(np.random.choice(["High-Lumen Projector", "Smart Whiteboard", "Audio PA & Mic System", "Ergonomic Modular Desks"], size=np.random.randint(2, 4), replace=False))
            noise_tolerance = "Moderate"
            base_hourly_energy_kwh = cap * 0.05
        elif rtype == "Laboratory":
            cap = int(np.random.choice([25, 35, 50]))
            amenities = list(np.random.choice(["High-Performance GPU Workstations", "Lab Fume Hoods & Benches", "High-Speed Gigabit LAN", "Smart Whiteboard"], size=np.random.randint(2, 4), replace=False))
            noise_tolerance = "Moderate"
            base_hourly_energy_kwh = cap * 0.09
        elif rtype == "Seminar Room":
            cap = int(np.random.choice([20, 30, 45]))
            amenities = list(np.random.choice(["Dual 4K Displays", "Video Conferencing Rig", "Acoustic Soundproofing", "Smart Whiteboard"], size=np.random.randint(2, 4), replace=False))
            noise_tolerance = "Strictly Quiet"
            base_hourly_energy_kwh = cap * 0.06
        else: # Study Space
            cap = int(np.random.choice([8, 15, 25]))
            amenities = list(np.random.choice(["Ergonomic Modular Desks", "Smart Whiteboard", "Acoustic Soundproofing", "High-Speed Gigabit LAN"], size=np.random.randint(1, 3), replace=False))
            noise_tolerance = "Quiet" if cap <= 15 else "Collaborative"
            base_hourly_energy_kwh = cap * 0.03

        floor = int(np.random.choice([1, 2, 3, 4]))
        room_name = f"{bldg['code']}-{floor}{room_id % 100:02d}"
        
        rooms.append({
            "room_id": f"RM_{room_id}",
            "room_name": room_name,
            "building": bldg["name"],
            "building_code": bldg["code"],
            "zone": np.random.choice(bldg["zones"]),
            "floor": floor,
            "room_type": rtype,
            "capacity": cap,
            "amenities": amenities,
            "noise_profile": noise_tolerance,
            "base_kwh": round(base_hourly_energy_kwh, 2),
            "historical_popularity_bias": round(float(np.random.uniform(0.6, 1.4)), 2) # some rooms naturally crowded
        })
        room_id += 1
        
    return pd.DataFrame(rooms)

def generate_live_occupancy(rooms_df):
    """
    Simulates real-time campus sensor state (IoT PIR sensor counts + WiFi density vs booked status).
    Detects ghost bookings: where status == 'Booked' but actual sensor occupancy == 0 or very low.
    """
    records = []
    now = datetime.now()
    current_hour = now.hour if 8 <= now.hour <= 21 else 14 # default to afternoon if outside hours
    
    for _, room in rooms_df.iterrows():
        cap = room["capacity"]
        bias = room["historical_popularity_bias"]
        
        # Simulated booking status
        booking_prob = min(0.95, 0.45 * bias)
        is_booked = np.random.random() < booking_prob
        
        if is_booked:
            booker_type = np.random.choice(["Faculty Lecture", "Student Club Rehearsal", "Hackathon Team", "Capstone Project", "Workshop"], p=[0.4, 0.25, 0.15, 0.1, 0.1])
            expected_headcount = int(np.random.uniform(0.4, 0.95) * cap)
            
            # Anomaly injection: 20% chance of Ghost Booking (no one showed up!)
            is_ghost = np.random.random() < 0.22
            if is_ghost:
                sensor_headcount = int(np.random.choice([0, 1, 2])) # almost nobody
                status = "Ghost Booking (Underutilized)"
            else:
                sensor_headcount = max(1, int(expected_headcount + np.random.normal(0, 3)))
                sensor_headcount = min(sensor_headcount, cap)
                status = "Active & Occupied"
        else:
            booker_type = "Unscheduled / Available"
            expected_headcount = 0
            # Ad-hoc walk-in study
            sensor_headcount = int(np.random.choice([0, 0, 1, 2, int(0.2 * cap)]))
            status = "Vacant & Available" if sensor_headcount == 0 else "Informal Walk-in"

        utilization_rate = round((sensor_headcount / cap) * 100, 1)
        
        records.append({
            "room_id": room["room_id"],
            "room_name": room["room_name"],
            "building": room["building"],
            "building_code": room["building_code"],
            "floor": room["floor"],
            "room_type": room["room_type"],
            "capacity": cap,
            "amenities": ", ".join(room["amenities"]),
            "is_booked": is_booked,
            "booker_type": booker_type,
            "expected_headcount": expected_headcount,
            "sensor_headcount": sensor_headcount,
            "utilization_pct": utilization_rate,
            "status": status,
            "noise_profile": room["noise_profile"],
            "wasted_kwh_if_ghost": round(room["base_kwh"] * 1.5, 2) if "Ghost" in status else 0.0
        })
        
    return pd.DataFrame(records)

def generate_historical_demand_series(days=30):
    """
    Generates hourly historical booking demand records across 30 days for forecasting.
    Features: day_of_week, hour, exam_period, is_club_active, room_type, demand_count.
    """
    rows = []
    base_date = datetime.now() - timedelta(days=days)
    
    for d in range(days):
        dt = base_date + timedelta(days=d)
        dow = dt.weekday() # 0 = Mon, 6 = Sun
        is_weekend = dow >= 5
        is_exam_week = (10 <= d <= 17) # simulated midterm season
        
        for hour in range(8, 22):
            # Time of day curve (peak at 10-12 and 14-17)
            tod_factor = np.sin((hour - 8) / 14 * np.pi) ** 1.3
            
            for rtype in ROOM_TYPES:
                base_demand = {
                    "Classroom": 28,
                    "Laboratory": 18,
                    "Seminar Room": 12,
                    "Study Space": 22
                }[rtype]
                
                # Apply modifier dynamics
                mult = 1.0
                if is_weekend:
                    mult *= 0.35 if rtype in ["Classroom", "Laboratory"] else 1.45 # study spaces boom on weekend
                if is_exam_week:
                    mult *= 1.8 if rtype == "Study Space" else 0.8
                
                # Clubs peak late afternoon
                if 16 <= hour <= 20 and rtype in ["Seminar Room", "Classroom"]:
                    mult *= 1.5
                    
                noise = np.random.normal(1.0, 0.12)
                demand = max(1, int(base_demand * tod_factor * mult * noise))
                
                rows.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "day_of_week": dow,
                    "hour": hour,
                    "is_exam_week": int(is_exam_week),
                    "is_weekend": int(is_weekend),
                    "room_type": rtype,
                    "demand_count": demand
                })
                
    return pd.DataFrame(rows)

def generate_sample_booking_requests(n=12):
    """
    Sample batch requests from students and clubs for batch optimization demo.
    """
    data = [
        {"request_id": "REQ_01", "entity": "Robotics Club", "category": "Club", "attendees": 35, "type_needed": "Laboratory", "req_amenities": "High-Performance GPU Workstations;High-Speed Gigabit LAN", "pref_time": "16:00 - 18:00", "urgency": "High"},
        {"request_id": "REQ_02", "entity": "ACM Coding Chapter", "category": "Club", "attendees": 48, "type_needed": "Classroom", "req_amenities": "High-Lumen Projector;High-Speed Gigabit LAN", "pref_time": "17:00 - 19:00", "urgency": "High"},
        {"request_id": "REQ_03", "entity": "Debate Society", "category": "Club", "attendees": 24, "type_needed": "Seminar Room", "req_amenities": "Acoustic Soundproofing;Audio PA & Mic System", "pref_time": "15:00 - 17:00", "urgency": "Medium"},
        {"request_id": "REQ_04", "entity": "Data Science Capstone Grp 4", "category": "Student", "attendees": 6, "type_needed": "Study Space", "req_amenities": "Smart Whiteboard;Ergonomic Modular Desks", "pref_time": "14:00 - 16:00", "urgency": "Low"},
        {"request_id": "REQ_05", "entity": "BioTech Research Cohort", "category": "Academic", "attendees": 20, "type_needed": "Laboratory", "req_amenities": "Lab Fume Hoods & Benches", "pref_time": "10:00 - 13:00", "urgency": "High"},
        {"request_id": "REQ_06", "entity": "Music & Performing Arts", "category": "Club", "attendees": 40, "type_needed": "Seminar Room", "req_amenities": "Acoustic Soundproofing;Audio PA & Mic System", "pref_time": "18:00 - 20:00", "urgency": "Medium"},
        {"request_id": "REQ_07", "entity": "FinTech Student Guild", "category": "Club", "attendees": 30, "type_needed": "Classroom", "req_amenities": "Dual 4K Displays;Video Conferencing Rig", "pref_time": "16:00 - 18:00", "urgency": "Low"},
        {"request_id": "REQ_08", "entity": "Peer Tutoring Calculus", "category": "Student", "attendees": 14, "type_needed": "Study Space", "req_amenities": "Smart Whiteboard", "pref_time": "11:00 - 13:00", "urgency": "Medium"},
        {"request_id": "REQ_09", "entity": "IEEE Student Branch", "category": "Club", "attendees": 55, "type_needed": "Classroom", "req_amenities": "High-Lumen Projector;Audio PA & Mic System", "pref_time": "17:00 - 19:00", "urgency": "High"},
        {"request_id": "REQ_10", "entity": "Quantum Computing Study Group", "category": "Student", "attendees": 8, "type_needed": "Study Space", "req_amenities": "Smart Whiteboard;High-Speed Gigabit LAN", "pref_time": "15:00 - 17:00", "urgency": "Low"},
        {"request_id": "REQ_11", "entity": "AI Hackathon Mentorship", "category": "Club", "attendees": 38, "type_needed": "Laboratory", "req_amenities": "High-Performance GPU Workstations", "pref_time": "14:00 - 18:00", "urgency": "High"},
        {"request_id": "REQ_12", "entity": "Philosophy Discussion Circle", "category": "Student", "attendees": 18, "type_needed": "Seminar Room", "req_amenities": "Acoustic Soundproofing", "pref_time": "16:00 - 18:00", "urgency": "Low"}
    ]
    return pd.DataFrame(data[:n])
