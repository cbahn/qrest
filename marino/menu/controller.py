from marino.db import UsersDB, LocationsDB
from marino.util import Util
from marino.models import User
from typing_extensions import Annotated
import tabulate
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