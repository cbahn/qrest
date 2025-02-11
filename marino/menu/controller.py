from marino.db import UsersDB, LocationsDB
from marino.models import User
from collections import Counter

def generate_leaderboard_data():
    visits = LocationsDB.get_all_visits()

    # Count occurrences of each userID
    user_visit_counts = Counter(entry["userID"] for entry in visits)

    # Convert Counter object into a list of dictionaries
    tallies = [{"userID": user, "visit_count": count} for user, count in user_visit_counts.items()]
    
    for i in tallies:
        user = UsersDB.lookup(User(userID=i.get('userID')))
        if user is not None:
            i['friendlyName'] = user.friendlyName
        else:
            i['friendlyName'] = "-- error --"

    return sorted(tallies, key=lambda x: -x["visit_count"])

def all_locations_visited_by_user(userID: str):
    locations = LocationsDB.get_all_locations()
    all_visits = LocationsDB.get_all_visits()
    user_visits = [visit for visit in all_visits if visit["userID"] == userID]
    
    location_map = {location.locationID: location for location in locations}
    
    results = []
    for visit in user_visits:
        location_id = visit.get('locationID')
        # Only add if we can find the matching location object
        if location_id in location_map:
            results.append({
                'loc': location_map[location_id],
                'visit_type': visit.get('visit_type')
            })
    return results