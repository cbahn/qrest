import pytest
from pymongo import MongoClient
from datetime import datetime
from config import Config
#from my_project.db_module import log_visit


DATABASE_NAME = 'test-db-1'
# Fixture to set up and tear down a test database
@pytest.fixture(scope="module")
def test_db():
    # Connect to MongoDB and create a new test database
    client = MongoClient(Config.MONGO_URI, tls=True, tlsCertificateKeyFile=Config.MONGO_CERT_PATH)
    db = client[DATABASE_NAME]

    # Ensure that the test database is empty
    db.locations.drop()
    db.users.drop()

    # Set up initial data in the test database
    db.locations.insert_many([
        {
            "name": "Grand Canyon",
            "visitors": []
        },
        {
            "name": "Yosemite",
            "visitors": []
        }
    ])
    
    db.users.insert_many([
        {
            "_id": "U12345",
            "name": "John Doe",
            "visited": []
        },
        {
            "_id": "U67890",
            "name": "Jane Smith",
            "visited": []
        }
    ])
    
    yield db  # Provide the test database to tests

    # Teardown: Drop the database after tests complete
    db.locations.drop()
    db.users.drop()
    client.close()

def test_some_dumb_bullshit(test_db):
    location = test_db.locations.find_one({"name":"Grand Canyon"})
    assert location is not None
    assert len(location["visitors"]) == 0

# # Example test: log visit to a location
# def test_log_visit_success(test_db):
#     log_visit("U12345", "Grand Canyon")  # Function call with test data

#     # Verify location data was updated
#     location = test_db.locations.find_one({"name": "Grand Canyon"})
#     assert location is not None
#     assert len(location["visitors"]) == 1
#     assert location["visitors"][0]["visitorID"] == "U12345"

#     # Verify user data was updated
#     user = test_db.users.find_one({"_id": "U12345"})
#     assert user is not None
#     assert "Grand Canyon" in user["visited"]

# # Example test: handle non-existent location
# def test_log_visit_nonexistent_location(test_db):
#     with pytest.raises(ValueError, match="Location not found"):
#         log_visit("U12345", "Nonexistent Location")
    
#     # Ensure no changes were made to the user's visited array
#     user = test_db.users.find_one({"_id": "U12345"})
#     assert user is not None
#     assert "Nonexistent Location" not in user["visited"]

# # Example test: handle non-existent user
# def test_log_visit_nonexistent_user(test_db):
#     with pytest.raises(ValueError, match="User not found"):
#         log_visit("NonexistentUserID", "Grand Canyon")
    
#     # Ensure no visitor was added to the location
#     location = test_db.locations.find_one({"name": "Grand Canyon"})
#     assert location is not None
#     assert len(location["visitors"]) == 0
