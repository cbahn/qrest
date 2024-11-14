from pymongo import MongoClient, ReturnDocument
from config import Config #My own config file


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
    
    def get_session(self, sessionID):
        return self.users_collection.find_one({"sessionID": sessionID})
    
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

    def get_location_info(self, locationID):
        return self.locations_collection.find_one({"locationID": locationID})

    def get_location_by_slug(self, location_slug):
        location_data = self.locations_collection.find_one({"slug": location_slug})
        if location_data and "visitors" in location_data:
            # Extract the Visitor array and sort it by VisitOrder
            sorted_visitors = sorted(location_data["visitors"], key=lambda x: x["visitOrder"])
            return {"friendlyName": location_data['friendlyName'], "slug":location_data['slug'], "sorted_visitors":sorted_visitors}
        else:
            return None  # no match found, return None

    def set_user_friendly_name(self, userID, friendly_name):
        result = self.users_collection.update_one(
            {'userID': userID},
            {'$set':{'friendly_name':friendly_name}}
        )
        if result.modified_count > 0:
            return self.users_collection.find_one({"userID": userID})
        else:
            return None
