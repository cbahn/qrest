import pytest
from pymongo.errors import DuplicateKeyError
from unittest.mock import patch, MagicMock
from flask import Flask
from marino.config import Config
from marino.db import TestingDB, UsersDB, LocationsDB, CommentsDB
from marino.models import User, Location
from pprint import pprint
import os

# Fixture to create a test Flask app
@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
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
    assert test_doc is not None
    assert test_doc['testString'] == "Welcome Home John"

def test_create_user(app, db):
    try:
        UsersDB.create(User(
            friendlyName="john",
            userID = "abc123"
        ))
    except Exception as e:
        assert False, f"An exception was raised while creating user: {e}"

    with pytest.raises(DuplicateKeyError, match=r"userID.*already exists."):
        UsersDB.create(User(
            friendlyName="billy_fakename",
            userID = "abc123"
        ))

    with pytest.raises(DuplicateKeyError, match=r"friendlyName.*already exists."):
        UsersDB.create(User(
            friendlyName="john",
            userID = "xyz789"
        ))

    # Verify that the failing users weren't inserted
    assert db.users.count_documents({"friendlyName": "billy_fakename"}) == 0
    assert db.users.count_documents({"userID": "xyz789"}) == 0

def test_lookup_user(app,db):

    UsersDB.create(User(friendlyName="alex",userID = "fed345"))
    UsersDB.create(User(friendlyName="bill",userID = "xyz789"))

    result1 = UsersDB.lookup(User(friendlyName="bill")) 
    assert result1.userID == "xyz789"

    result2 = UsersDB.lookup(User(userID="fed345"))
    assert result2.friendlyName == "alex"

    assert UsersDB.lookup(User(userID="doesnt4exist")) == None

    assert UsersDB.lookup(User(userID="AECHVDR")) == None

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

def test_comments(app,db):
    CommentsDB.create_comment('abc123','l4567','comment one')
    CommentsDB.create_comment('fed345','l4567','comment two')

    all_comments = CommentsDB.get_comments_for_location('l4567')
    assert pprint(all_comments) == 'bug'