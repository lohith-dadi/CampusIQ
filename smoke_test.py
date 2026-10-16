import sys
from core.data_manager import DataManager
from core.analytics import CampusAnalytics
from core.conflict_detector import ConflictDetector
from core.matcher import SmartRoomMatcher
from core.recommendations import RecommendationEngine

def main():
    print("1. Loading Datasets...")
    dm = DataManager()
    data = dm.load_and_validate_all()
    print(f"   Rooms: {len(data['rooms'])}, Sched: {len(data['schedule'])}, Events: {len(data['events'])}, Reqs: {len(data['requests'])}")
    
    print("2. Calculating Analytics & Scheduled Utilization...")
    analytics = CampusAnalytics(data['rooms'], data['schedule'], data['events'], data['requests'])
    kpis = analytics.get_overall_kpis(8.0, 20.0, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
    print(f"   Campus Scheduled Utilization: {kpis['campus_scheduled_utilization_pct']}%")
    print(f"   Total Occupied Union Hours: {kpis['total_occupied_union_hours']} hrs")
    print(f"   Total Available Hours: {kpis['total_available_hours']} hrs")
    
    print("3. Detecting Conflicts...")
    detector = ConflictDetector(data['rooms'], data['schedule'], data['events'])
    conflicts = detector.detect_all_conflicts()
    print(f"   Total Conflicts Detected: {conflicts['total_conflicts']}")
    print(f"   - Class vs Class Overlaps: {len(conflicts['class_class_conflicts'])}")
    print(f"   - Event vs Event Overlaps: {len(conflicts['event_event_conflicts'])}")
    print(f"   - Class vs Event Clashes: {len(conflicts['class_event_conflicts'])}")
    print(f"   - Schedule Capacity Overflows: {len(conflicts['capacity_overflows'])}")
    
    print("4. Testing Smart Room Matcher...")
    matcher = SmartRoomMatcher(data['rooms'], data['schedule'], data['events'], kpis['utilization_df'])
    res = matcher.find_candidates(required_capacity=45, weekday="Mon", start_hour=14.0, duration_hours=2.0, projector_required=True)
    best_id = res['best_candidate']['room_id'] if res['best_candidate'] else "None"
    print(f"   Feasible Candidates for 45 pax: {res['feasible_count']}, Best: {best_id}")
    
    print("5. Evaluating Request Feasibility Rate...")
    feas = matcher.evaluate_requests_batch_feasibility(data['requests'], max_samples=100)
    print(f"   Sample Feasibility Rate: {feas['match_rate_pct']}% ({feas['with_feasible_candidate']}/{feas['total_evaluated']})")
    
    print("6. Generating Admin Recommendations...")
    rec_eng = RecommendationEngine(data['rooms'], data['schedule'], data['events'], data['requests'], kpis['utilization_df'], conflicts)
    recs = rec_eng.generate_recommendations()
    print(f"   Generated {len(recs)} prioritized administrative recommendations.")
    for r in recs:
        print(f"   * [{r['priority']}] {r['title']} -> {r['impact_metric']}")
        
    print("\nALL SMOKE TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
