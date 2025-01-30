from flask import current_app, g

from werkzeug.local import LocalProxy
from pymongo import MongoClient
import os
from pymongo.errors import DuplicateKeyError, OperationFailure

from .util import Util
from .models import User


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
                        raise DuplicateDataError(f"Friendly Name '{user.friendlyName}' already exists.")
                    
                    userData = {
                        "userID": user.userId,
                        "sessionID": "",
                        "friendly_name": user.friendlyName,
                    }
                    if user.role:
                        userData["role"] = user.role
                    db.users.insert_one( userData )

                    # I'm not sure what to return here. We know the function succeeded
                    # if no exceptions were thrown
                    return userData

    def lookup_user(user: User) -> User:
        param = {
            'userID':user.userId,
            'sessionID':user.sessionID,
            'friendly_name':user.friendlyName,
            'role':user.role,
        }

        # Remove all non-specified data fields from search parameters
        cleaned_param = {k:v for k, v in param.items() if v is not None}

        found_user = db.users.find_one(cleaned_param)
        if found_user:
            return User(
                userId=found_user.get('userID',None),
                sessionID=found_user.get('sessionID',None),
                friendlyName=found_user.get('friendly_name',None),
                role=found_user.get('role',None)
                )
        
        return None

    def CycleSessionID(userId: str):
        newSessionCode = Util.generate_session_code()
        db.users.update_one(
            {'userID':userId},
            {'$set': {'sessionID':newSessionCode}})
        return newSessionCode
    
    