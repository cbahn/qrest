from pymongo import MongoClient, ReturnDocument
from config import Config #My own config file


DATABASE_NAME = Config.DATABASE_NAME

class DatabaseManager:
    def __init__(self, database):
        # <- make sure to hand the database to DatabaseManager, not the client.
        # Call `client['database_name']` first

        self.users_collection = database.users
        self.locations_collection = database.locations

    def create_new_user(self, userID):
        new_user = {
            "userID": userID
        }
        self.users_collection.insert_one(new_user)

    def print_users(self):
        # Verify by retrieving and printing all documents
        for doc in self.users_collection.find():
            print(doc)

    def get_user(self, userID):
        return self.users_collection.find_one({"userID": userID})
    
    def user_visits_location(self,userID,locationID):
        with self.client.start_session() as session:
            with session.start_transaction():
                loc_data = self.locations_collection.find_one({"locationID":"25DD"},session=session)
                visitor_count = loc_data['totalVisitors']

                new_visitor_data = {
                    "visitorID":"v1442",
                    "name":"johh",
                    "VisitOrder": visitor_count + 1
                }

                self.locations_collection.update_one(
                    {"locationID":"25DD"},
                    {"$push":{"visitors":new_visitor_data}},
                    session=session
                )
        # check if user has visited that location yet
        # update location info
        # update user's info

    def get_location_info(self, locationID):
        location_data = self.locations_collection.find_one({"locationID": locationID})
        if location_data and "visitors" in location_data:
            # Extract the Visitor array and sort it by VisitOrder
            sorted_visitors = sorted(location_data["visitors"], key=lambda x: x["visitOrder"])
            return sorted_visitors
        else:
            return []  # Return an empty list if no document found or no Visitor array

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