from pymongo import MongoClient

# Define the connection details
uri = "mongodb+srv://quest-cluster.rdm3o.mongodb.net/?authSource=$external&authMechanism=MONGODB-X509"

# Path to the certificate file
certificate_path = "/Users/barry/Downloads/X509-cert-8316495671987192482.pem"

class DatabaseManager:
    def __init__(self):
        # Create a client connection
        self.client = MongoClient(uri, tls=True, tlsCertificateKeyFile=certificate_path)
        self.users_collection = self.client['exampledb']['users']

    def print_users(self):
        # Verify by retrieving and printing all documents
        for doc in self.users_collection.find():
            print(doc)

    def get_user(self, userID):
        return self.users_collection.find_one({"userID": userID})
    
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