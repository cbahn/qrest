from pymongo import MongoClient, ReturnDocument
from config import Config #My own config file
from util_module import Util


DATABASE_NAME = Config.DATABASE_NAME

class DatabaseManager:
    def __init__(self, database):
        # <- make sure to hand the database to DatabaseManager, not the client.
        # Call `client['database_name']` first

        self.users_collection = database.users
        self.locations_collection = database.locations
        self.visits_collection = database.visits

    def create_new_user(self, userID, sessionID):
        new_user = {
            'userID': userID,
            'sessionID': sessionID
        }
        self.users_collection.insert_one(new_user)

    def print_users(self):
        # Verify by retrieving and printing all documents
        for doc in self.users_collection.find():
            print(doc)

    def get_user(self, userID):
        return self.users_collection.find_one({"userID": userID})
    
    def check_admin(self, sessionID):
        """
        :param sessionID: user's session
        :result: True if user is admin, False if not admin or not found
        """
        result = self.users_collection.find_one({"sessionID": sessionID})
        if result is not None:
            if result["role"] == "admin":
                return True
        return False
    
    def get_session(self, sessionID):
        return self.users_collection.find_one({"sessionID": sessionID})
    
    def rotate_session(self, userID):
        new_sessionID = Util.generate_session_code()
        self.users_collection.update_one(
            {"userID": userID},
            {"$set": {"sessionID": new_sessionID}}
        )
        return new_sessionID

    def log_visit(self, userID, locationID, TEST_number):
        # Construct the filter to find an existing check-in by username and location_id
        filter_query = {
            "userID": userID,
            "locationID": locationID,
        }
        
        # Define the data to upsert
        update_data = {
            "$set": {
                "TEST_number": TEST_number
            },
            "$setOnInsert": {
                "userID": userID,
                "locationID": locationID,
                "note": "First time here!"  # Optional: only set if it's a new document
            }
        }
        result = self.visits_collection.update_one(filter_query, update_data, upsert=True) # hashtag upsert
        
        if result.upserted_id: # if upserted_id exists, it means a new document was created
            return result
        return None

    def list_user_visits(self, userID):
        # returns a list of documents (sorted alphabeticaly by friendlyName)
        # for each location the user has visited
        visits = self.visits_collection.find({"userID": userID})
        visited_locationIDs = [s['locationID'] for s in visits]
        locations = self.locations_collection.find({"locationID": {"$in": visited_locationIDs}})
        return sorted(locations, key=lambda d: d['friendlyName'])
    
    def get_location_info(self, locationID):
        return self.locations_collection.find_one({"locationID": locationID})

    def get_location_by_slug(self, location_slug):
        return self.locations_collection.find_one({"slug": location_slug})

    def set_user_friendly_name(self, userID, friendly_name):
        result = self.users_collection.update_one(
            {'userID': userID},
            {'$set':{'friendly_name':friendly_name}}
        )
        if result.modified_count > 0:
            return self.users_collection.find_one({"userID": userID})
        else:
            return None

    def calculate_leaderboard(self, remove_admins=True):
        visits_list = self.visits_collection.find()
        leaderboard_count = {}
        for visit in visits_list:
            userID = visit.get("userID")
            if userID:
                leaderboard_count[userID] = leaderboard_count.get(userID, 0) + 1
        
        # I want to return a list of friendly_names not user IDs
        leaderboard_friendly = []
        for id, count in leaderboard_count.items():
            user_data = self.get_user(id)
            if user_data and "friendly_name" in user_data:
                if not (remove_admins and user_data.get('role', '') == 'admin'):  # Remove Admins from list
                    leaderboard_friendly.append( {
                        "friendly_name": user_data["friendly_name"],
                        "visit_count": count,
                    })
        return leaderboard_friendly