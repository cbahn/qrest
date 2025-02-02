from flask import current_app, g

from werkzeug.local import LocalProxy
from pymongo import MongoClient
import os
import datetime
#from pymongo.errors import DuplicateKeyError, OperationFailure

from .util import Util
from .models import User, Location

def get_client():
    """
    Used by the below LocalProxy
    """
    mongo = getattr(g, "_database_client", None)

    if mongo is None:
        # Get configuration from Flask app
        mongo_uri = current_app.config.get("MONGO_URI")
        mongo_cert_path = current_app.config.get("MONGO_CERT_PATH")

        if not mongo_uri:
            raise RuntimeError("MONGO_URI is not set in the Flask configuration")
        if not mongo_cert_path:
            raise RuntimeError("MONGO_CERT_PATH is not set in the Flask configuration")

        # Throw an exception if the cert file is missing
        if not os.path.isfile(mongo_cert_path):
            raise FileNotFoundError(f"Certificate file '{mongo_cert_path}' does not exist.")

        # Initialize the MongoClient with TLS options
        mongo = g._database_client = MongoClient(
            mongo_uri,
            tls=True,
            tlsCertificateKeyFile=mongo_cert_path
        )
    return mongo

def get_db():
    mongo_db_name = current_app.config.get("MONGO_DB_NAME")
    return get_client()[mongo_db_name]

mongo = LocalProxy(get_client)
db = LocalProxy(get_db)

######################### FUNCTIONS ###############################

class DuplicateDataError(Exception):
    """Raised when there's an attempt to insert a duplicate 
    value into a field that must be unique """
    pass

class TestingDB:

    def connection_test():
        """
        This is just used by the integration test to confirm that I can access
        the actual database
        """
        return db.connectiontest.find_one()
    
    def get_db_proxy():
        return db

class UsersDB:
    def create(user: User):
        with mongo.start_session() as session:
                with session.start_transaction():

                    # Enforce uniqueness of userID and friendly_name fields
                    existing_user = db.users.find_one({"userID": user.userId}, session=session)
                    if existing_user:
                        print(str(existing_user))
                        raise DuplicateDataError(f"UserID '{user.userId}' already exists.")
                    existing_user = db.users.find_one({"friendly_name": user.friendlyName}, session=session)
                    if existing_user:
                        raise DuplicateDataError(f"friendly_name '{str(user.friendlyName)}' already exists.")
                    
                    userData = {
                        "userID": user.userId,
                        "sessionID": "",
                        "friendly_name": user.friendlyName,
                        "fingerprint": user.fingerprint,
                    }
                    if user.role:
                        userData["role"] = user.role
                    db.users.insert_one( userData )

                    # I'm not sure what to return here. We know the function succeeded
                    # if no exceptions were thrown
                    return userData

    def lookup(user: User) -> None | User:
        param = {
            'userID':user.userId,
            'sessionID':user.sessionID,
            'friendly_name':user.friendlyName,
            'role':user.role,
            'fingerprint': user.fingerprint,
        }

        # Remove all non-specified data fields from search parameters
        cleaned_param = {k:v for k, v in param.items() if v is not None}

        found_user = db.users.find_one(cleaned_param)
        if found_user is not None:
            return User(
                userId=found_user.get('userID',None),
                sessionID=found_user.get('sessionID',None),
                friendlyName=found_user.get('friendly_name',None),
                role=found_user.get('role',None),
                fingerprint=found_user.get('fingerprint',None)
                )
        return None

    def cycleSessionID(userId: str) -> str:
        newSessionCode = Util.generate_session_code()
        db.users.update_one(
            {'userID':userId},
            {'$set': {'sessionID':newSessionCode}})
        return newSessionCode
    
class LocationsDB:
    def lookup(loc: Location) -> None | Location:
        param = {
            'locationID': loc.locationID,
            'fullName': loc.fullName,
            'slug': loc.slug,
            'description': loc.description,
            'puzzleText': loc.puzzleText,
            'puzzleAnswer': loc.puzzleAnswer
        }

        # Remove all non-specified data fields from search parameters
        cleaned_param = {k: v for k, v in param.items() if v is not None}

        found_loc = db.locations.find_one(cleaned_param)
        if found_loc is not None:
            return Location(
                locationID=found_loc.get('locationID', None),
                fullName=found_loc.get('fullName', None),
                slug=found_loc.get('slug', None),
                description=found_loc.get('description', None),
                puzzleText=found_loc.get('puzzleText', None),
                puzzleAnswer=found_loc.get('puzzleAnswer', None)
            )

        return None
    
    def check_visit(userID: str, locationID: str) -> bool:
        visit_data = {
            "userID": userID,
            "locationID": locationID
        }
        visit_found = db.visits.find_one(visit_data)
        return visit_found is not None
    
    def record_visit(userID: str, locationID: str) -> bool:
        """ Record a visit if no existing record with the same userID and locationID exists.
        Return True if a new visit was recorded, false otherwise.
        """
        with mongo.start_session() as session:
            with session.start_transaction():

                visit_data = {
                    "userID": userID,
                    "locationID": locationID
                }

                existing_visit = db.visits.find_one(visit_data)

                if existing_visit is not None:
                    return False # Visit was already recorded

                visit_data["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc)
                db.visits.insert_one(visit_data)
                return True
    
    def get_all_visits():
        """Retrieve all (name, location) pairs sorted by timestamp."""
        cursor = db.visits.find({}, {"userID": 1, "locationID": 1, "timestamp": 1}).sort("timestamp", 1)
        
        # Extract and return list of (name, location) tuples
        return [{"userID":doc["userID"], "locationID":doc["locationID"]} for doc in cursor]