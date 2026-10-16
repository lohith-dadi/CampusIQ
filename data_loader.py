"""
data_loader.py
Loads, cleans, and enriches the official Datathon Campus Space datasets:
- rooms.csv
- class_schedule.csv
- events.csv
- room_requests.csv
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_data_paths():
    # Primary: local project data folder
    if os.path.exists(os.path.join(DATA_DIR, "rooms.csv")):
        return DATA_DIR
    # Fallback: original datasets folder
    fallback = r"C:\Users\dadil\.datasets1\02_education_campus_space\02_education_campus_space"
    if os.path.exists(fallback):
        return fallback
    raise FileNotFoundError("Could not locate Datathon datasets folder.")

def load_all_datasets():
    data_path = get_data_paths()
    
    rooms_df = pd.read_csv(os.path.join(data_path, "rooms.csv"))
    schedule_df = pd.read_csv(os.path.join(data_path, "class_schedule.csv"))
    events_df = pd.read_csv(os.path.join(data_path, "events.csv"))
    requests_df = pd.read_csv(os.path.join(data_path, "room_requests.csv"))
    
    # 1. Clean & Enrich Rooms
    # Compute estimated base power rating (kWh/hr)
    rooms_df["power_rating_kw"] = (
        (rooms_df["capacity"] * 0.04) + 
        (rooms_df["projector"] * 0.35) + 
        (rooms_df["computers"] * 0.25 * (rooms_df["capacity"] * 0.5)) +
        (rooms_df["power_outlets"] * 0.05)
    ).round(2)
    
    # 2. Enrich Events (Analyze Ghost Bookings)
    events_df["start_time"] = pd.to_datetime(events_df["start_time"])
    events_df["event_date"] = events_df["start_time"].dt.date
    events_df["start_hour"] = events_df["start_time"].dt.hour
    events_df["weekday"] = events_df["start_time"].dt.strftime("%a")
    
    events_df["attendance_gap"] = events_df["expected_attendance"] - events_df["actual_attendance"]
    events_df["attendance_retention_pct"] = (
        (events_df["actual_attendance"] / np.maximum(1, events_df["expected_attendance"])) * 100
    ).clip(0, 200).round(1)
    
    # Flag ghost bookings: expected >= 20 people and actual attendance is less than 30% or drop >= 50
    events_df["is_ghost_booking"] = (
        (events_df["expected_attendance"] >= 20) & 
        ((events_df["actual_attendance"] <= 0.25 * events_df["expected_attendance"]) | (events_df["attendance_gap"] >= 50))
    )
    
    # Merge room metadata into events
    events_enriched = events_df.merge(rooms_df[["room_id", "building", "floor", "room_type", "capacity", "power_rating_kw"]], on="room_id", how="left")
    events_enriched["wasted_kwh"] = np.where(
        events_enriched["is_ghost_booking"],
        (events_enriched["power_rating_kw"] * events_enriched["duration_hours"]).round(2),
        0.0
    )
    
    # 3. Enrich Class Schedule
    schedule_enriched = schedule_df.merge(rooms_df[["room_id", "building", "floor", "room_type", "capacity"]], on="room_id", how="left")
    schedule_enriched["utilization_pct"] = (
        (schedule_enriched["expected_attendance"] / np.maximum(1, schedule_enriched["capacity"])) * 100
    ).round(1)
    
    # 4. Enrich Requests
    requests_df["request_date"] = pd.to_datetime(requests_df["request_date"])
    requests_df["weekday"] = requests_df["request_date"].dt.strftime("%a")
    requests_df["is_rejected_or_waitlist"] = requests_df["status"].isin(["Waitlisted", "Rejected"])
    
    # Calculate room occupancy load summary
    room_metrics = []
    for rid, grp in schedule_enriched.groupby("room_id"):
        room_row = rooms_df[rooms_df["room_id"] == rid].iloc[0]
        event_sub = events_enriched[events_enriched["room_id"] == rid]
        
        ghost_count = event_sub["is_ghost_booking"].sum()
        total_event_count = len(event_sub)
        ghost_rate = round((ghost_count / max(1, total_event_count)) * 100, 1) if total_event_count > 0 else 0.0
        
        avg_class_util = round(grp["utilization_pct"].mean(), 1) if len(grp) > 0 else 0.0
        total_sched_hours = grp["duration_hours"].sum()
        
        room_metrics.append({
            "room_id": rid,
            "building": room_row["building"],
            "room_type": room_row["room_type"],
            "capacity": room_row["capacity"],
            "floor": room_row["floor"],
            "projector": room_row["projector"],
            "computers": room_row["computers"],
            "accessible": room_row["accessible"],
            "power_outlets": room_row["power_outlets"],
            "power_rating_kw": room_row["power_rating_kw"],
            "weekly_scheduled_hours": total_sched_hours,
            "avg_class_utilization_pct": avg_class_util,
            "total_events": total_event_count,
            "ghost_event_count": ghost_count,
            "ghost_booking_rate_pct": ghost_rate
        })
    room_metrics_df = pd.DataFrame(room_metrics)
    
    return {
        "rooms": rooms_df,
        "schedule": schedule_enriched,
        "events": events_enriched,
        "requests": requests_df,
        "room_metrics": room_metrics_df
    }

if __name__ == "__main__":
    d = load_all_datasets()
    print("Loaded data successfully!")
    print(f"Rooms: {len(d['rooms'])}, Sched: {len(d['schedule'])}, Events: {len(d['events'])}, Reqs: {len(d['requests'])}")
    print(f"Ghost events flagged: {d['events']['is_ghost_booking'].sum()}")
