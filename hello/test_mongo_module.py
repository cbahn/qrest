import pytest
from pymongo import MongoClient
from datetime import datetime
from config import Config
from mongo_module import DatabaseManager

TESTING_DATABASE_NAME = 'test-db-1'

# Fixture to set up and tear down a test database
@pytest.fixture(scope="module")
def test_db():
    # Connect to MongoDB and create a new test database
    client = MongoClient(Config.MONGO_URI, tls=True, tlsCertificateKeyFile=Config.MONGO_CERT_PATH)
    db = client[TESTING_DATABASE_NAME]

    # Ensure that the test database is empty
    db.locations.drop()
    db.users.drop()

    # Set up initial data in the test database
    db.locations.insert_many([
        {
            "locationID":"L52358",
            "friendlyName": "Grand Canyon",
            "totalVisitors": 2,
            "visitors": [
                {"visitorID": "U12345","visitOrder": 1 },
                {"visitorID": "U67890","visitOrder": 2 }
            ]
        },
        {
            "locationID":"L84168",
            "friendlyName": "Graceland",
            "totalVisitors": 1,
            "visitors": [
                {"visitorID": "U12345","visitOrder": 1 }
            ]
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

    # Teardown: Drop the collections after tests complete
    db.locations.drop()
    db.users.drop()
    client.close()


def test_location_info(test_db):
    my_db = DatabaseManager(test_db)
    leaderboard = my_db.get_location_info("L5235")

    assert leaderboard is not None
    assert len(leaderboard) == 2
    assert leaderboard[0]['visitorID'] == 'U12345'
