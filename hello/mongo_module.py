from pymongo import MongoClient, ReturnDocument
from config import Config #My own config file


DATABASE_NAME = Config.DATABASE_NAME

class DatabaseManager:
    def __init__(self):
        # Create a client connection
        self.client = MongoClient(Config.MONGO_URI, tls=True, tlsCertificateKeyFile=Config.MONGO_CERT_PATH)
        self.users_collection = self.client[DATABASE_NAME]['users']
        self.locations_collection = self.client[DATABASE_NAME]['locations']

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
    
    def update_user_status(self, userID, new_status):
        self.users_collection.update_one(
            {'userID': userID},
            {'$set':{'status': new_status}}
        )
        return


""" # Access or create a new database (e.g., 'exampledb')
db = client['exampledb']

# Access or create a new collection (e.g., 'users')
collection = db['users']

# Insert some example data
example_data = [
    {"userID": 1, "name": "Alice", "email": "alice@example.com"},
    {"userID": 2, "name": "Bob", "email": "bob@example.com"},
    {"userID": 3, "name": "Charlie", "email": "charlie@example.com"}
]

# Insert data into the collection
collection.insert_many(example_data)
print("Example data inserted successfully.")

# Verify by retrieving and printing all documents
for doc in collection.find():
    print(doc)

# Close the connection
client.close() """