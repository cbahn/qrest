import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from marino.config import Config
from marino.db import DuplicateDataError, TestingDB, UsersDB, LocationsDB
from marino.models import User, Location

# Fixture to create a test Flask app
@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = Config.MONGO_URI
    app.config['MONGO_CERT_PATH'] = Config.MONGO_CERT_PATH
    app.config['MONGO_DB_NAME'] = "test-db-1"
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def db():
    db = TestingDB.get_db_proxy()
    
    # clear the users collection once before the tests are run
    db.users.drop()
    db.visits.drop()
    yield db

def test_connection_to_real_database(app):
    """
    Verify that we can connect to the collection 'connectiontest' 
    and retrieve data from the one document there
    """
    test_doc = TestingDB.connection_test()
    assert test_doc['testString'] == "Welcome Home John"

def test_create_user(app, db):
    try:
        UsersDB.create(User(
            friendlyName="john",
            userId = "abc123"
        ))
    except Exception as e:
        assert False, f"An exception was raised while creating user: {e}"

    with pytest.raises(DuplicateDataError, match=r"UserID.*already exists."):
        UsersDB.create(User(
            friendlyName="billy_fakename",
            userId = "abc123"
        ))

    with pytest.raises(DuplicateDataError, match=r"friendly_name.*already exists."):
        UsersDB.create(User(
            friendlyName="john",
            userId = "xyz789"
        ))

    # Verify that the failing users weren't inserted
    assert db.users.count_documents({"friendly_name": "billy_fakename"}) == 0
    assert db.users.count_documents({"userId": "xyz789"}) == 0

def test_lookup_user(app,db):

    UsersDB.create(User(friendlyName="alex",userId = "fed345"))
    UsersDB.create(User(friendlyName="bill",userId = "xyz789"))

    result1 = UsersDB.lookup(User(friendlyName="bill")) 
    assert result1.userId == "xyz789"

    result2 = UsersDB.lookup(User(userId="fed345"))
    assert result2.friendlyName == "alex"

    assert UsersDB.lookup(User(userId="doesnt4exist")) == None

    assert UsersDB.lookup(User(userId="AECHVDR")) == None

def test_lookup_loc(app,db):

    result1 = LocationsDB.lookup(Location(locationID="L4567"))
    assert result1.slug == "ugly-bug"
    assert result1.fullName == "The Ugly Bug!"

    assert LocationsDB.lookup(Location(slug="doesnt-exist")) == None
    
def test_register_visit(app,db):
    example_user = 'A45'
    example_location = 'L67'

    assert LocationsDB.record_visit(userID=example_user, locationID=example_location, visit_type='discovered') == True
    assert LocationsDB.record_visit(userID=example_user, locationID=example_location, visit_type='discovered') == False

    assert LocationsDB.record_visit(userID=example_user, locationID=example_location, visit_type='solved') == True
    assert LocationsDB.record_visit(userID=example_user, locationID=example_location, visit_type='solved') == False