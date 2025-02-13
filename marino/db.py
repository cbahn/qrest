from flask import current_app, g

from werkzeug.local import LocalProxy
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import datetime
from zoneinfo import ZoneInfo
#from pymongo.errors import DuplicateKeyError, OperationFailure

from .util import Util
from .models import User, Location, Comment

def get_client():
    """
    Used by the below LocalProxy
    """
    mongo = getattr(g, "_database_client", None)

    if mongo is None:
        # Get configuration from Flask app
        mongo_uri = current_app.config.get("MONGO_URI")

        if not mongo_uri:
            raise RuntimeError("MONGO_URI is not set in the Flask configuration")

        # Initialize the MongoClient
        mongo = g._database_client = MongoClient(mongo_uri)
    return mongo

def get_db():
    mongo_db_name = current_app.config.get("MONGO_DB_NAME")
    return get_client()[mongo_db_name]

mongo = LocalProxy(get_client)
db = LocalProxy(get_db)

######################### FUNCTIONS ###############################

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

    FULL_PROJECTION = {
        "userID": 1,
        "sessionID": 1,
        "friendlyName": 1,
        "role": 1,
        "fingerprint": 1,
        "admin": 1,
        "ephemeralID": 1,
        "coins": 1,
        "_id": 0,
    }

    def create(user: User) -> dict:

        new_user_record = user.to_dict()

        # All users are created as non-admins by default
        new_user_record['admin'] = False

        # All users are created with 0 coins by default
        new_user_record['coins'] = 0

        with mongo.start_session() as session:
            with session.start_transaction():

                if db.users.find_one({"userID": user.userID}, session=session):
                    raise DuplicateKeyError(f"userID '{user.userID}' already exists.")
                
                if db.users.find_one({"friendlyName": user.friendlyName}, session=session):
                    raise DuplicateKeyError(f"friendlyName '{user.friendlyName}' already exists.")
                
                db.users.insert_one( new_user_record, session=session)
        return new_user_record

    def lookup(user: User) -> None | User:
        user_query = user.to_dict()

        found_user = db.users.find_one(user_query, UsersDB.FULL_PROJECTION)
        if found_user is not None:
            return User(**found_user)
        return None

    def modify_coins(userID: str, coin_delta: int, cause: str) -> int:
        """ 
        Modify the coin count for the user with the given userID.
        
        Returns:
            int: The updated coin count.

        Raises:
            ValueError: If the user is not found or if the new coin count would be negative.
        """
        # Create history entry
        new_entry = {
            "timestamp": datetime.datetime.now(tz=ZoneInfo("UTC")),
            "cause": cause,
            "coin_delta": coin_delta
        }

        with mongo.start_session() as session:
            with session.start_transaction():
                user = db.users.find_one({"userID": userID})
                if user is None:
                    raise ValueError(f"User with userID '{userID}' not found")

                new_coin_count = user.get('coins', 0) + coin_delta

                if new_coin_count < 0:
                    raise ValueError("Coin count cannot be negative")

                # Update user document
                db.users.update_one(
                    {"userID": userID},
                    {
                        "$set": {"coins": new_coin_count},
                        "$push": {"coinHistory": new_entry}
                    }
                )
        return new_coin_count

    def cycleSessionID(userID: str) -> str:
        newSessionCode = Util.generate_session_code()
        db.users.update_one(
            {'userID':userID},
            {'$set': {'sessionID':newSessionCode}})
        return newSessionCode
    
    def cycleEphemeralID(userID: str) -> str:
        newEphemeralID = Util.generate_new_ephemeralID()
        db.users.update_one(
            {'userID':userID},
            {'$set': {'ephemeralID':newEphemeralID}})
        return newEphemeralID

    def transfer_coin(sender_userID: str, recipient_friendlyName: str, amount: int):
        """ 
        Transfer coins from one user to another.
        
        Args:
            sender_userID (str): The userID of the sender.
            recipient_friendlyName (str): The friendlyName of the recipient.
            amount (int): The amount of coins to transfer.

        Returns:
            bool: True if the transfer was successful, False otherwise.

        Raises:
            ValueError: If the sender or recipient is not found, or if the sender has insufficient coins.
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        with mongo.start_session() as session:
            with session.start_transaction():
                sender = db.users.find_one({"userID": sender_userID})
                if sender is None:
                    raise ValueError(f"Sender with userID '{sender_userID}' not found")

                recipient = db.users.find_one({"friendlyName": recipient_friendlyName})
                if recipient is None:
                    raise ValueError(f"Recipient with friendlyName '{recipient_friendlyName}' not found")

                sender_new_coin_count = sender.get('coins', 0) - amount
                if sender_new_coin_count < 0:
                    raise ValueError("Sender has insufficient coins")

                recipient_new_coin_count = recipient.get('coins', 0) + amount

                # Create history entries
                timestamp = datetime.datetime.now(tz=ZoneInfo("UTC"))
                sender_entry = {
                    "timestamp": timestamp,
                    "cause": f"Transfer to {recipient_friendlyName}",
                    "coin_delta": -amount
                }
                recipient_entry = {
                    "timestamp": timestamp,
                    "cause": f"Transfer from {sender_userID}",
                    "coin_delta": amount
                }

                # Update sender document
                db.users.update_one(
                    {"userID": sender_userID},
                    {
                        "$set": {"coins": sender_new_coin_count},
                        "$push": {"coinHistory": sender_entry}
                    }
                )

                # Update recipient document
                db.users.update_one(
                    {"friendlyName": recipient_friendlyName},
                    {
                        "$set": {"coins": recipient_new_coin_count},
                        "$push": {"coinHistory": recipient_entry}
                    }
                )
    
    def get_all_users():
        all_users = db.users.find({}, UsersDB.FULL_PROJECTION)
        return [User(**user) for user in all_users]

class LocationsDB:

    FULL_PROJECTION = {
        "locationID": 1,
        "fullName": 1,
        "slug": 1,
        "imageFile": 1,
        "description": 1,
        "puzzleText": 1,
        "puzzleAnswer": 1,
        "_id": 0,
    }

    def create(loc: Location) -> None | Location:
        loc.locationID = Util.generate_new_locationID()
        new_location_record = loc.to_dict()
        db.locations.insert_one( new_location_record )
        return loc

    def lookup(loc: Location) -> None | Location:
        param = loc.to_dict()

        found_loc = db.locations.find_one(param, LocationsDB.FULL_PROJECTION)
        if found_loc is not None:
            return Location(**found_loc)
        return None
    
    def get_all_locations():
        """
        Returns a list of all locations in the database.
        """
        all_locs = db.locations.find({}, LocationsDB.FULL_PROJECTION)
        return [Location(**loc) for loc in all_locs]

    def delete(locationID: str) -> bool:
        result = db.locations.delete_one({"locationID": locationID})

        if result.acknowledged and result.deleted_count == 1:
            return True # Success
        else:
            return False # Unknown failure

    def check_visit(userID: str, locationID: str) -> str:
        visit_data = {
            "userID": userID,
            "locationID": locationID
        }
        visit_found = db.visits.find_one(visit_data)
        if visit_found is None:
            return 'undiscovered'
        return visit_found['visit_type']
    
    def record_visit(userID: str, locationID: str, visit_type: str) -> bool:
        """ 
        Record a visit if no existing record with the same userID and locationID exists.
        Return True if a new visit was created or updated, false otherwise.
        """
        if visit_type not in ['discovered','solved']:
            raise ValueError(f"'{visit_type}' is not a valid visit_type")

        with mongo.start_session() as session:
            with session.start_transaction():

                visit_data = {
                    "userID": userID,
                    "locationID": locationID
                }
                existing_visit = db.visits.find_one(visit_data)
                
                if existing_visit is None:
                    # Log the visit for the first time
                    visit_data['timestamp'] = datetime.datetime.now(tz=ZoneInfo("UTC"))
                    visit_data['visit_type'] = visit_type
                    db.visits.insert_one(visit_data)
                    return True
                
                if existing_visit['visit_type'] == 'discovered' and visit_type == 'solved':
                    # Newly solved location, update visit type
                    db.visits.update_one(
                        visit_data,
                        {'$set': {'visit_type': visit_type}}
                        )
                    return True
                # Any other case, no update is needed
                return False
    
    def change_discovery_status(userID: str, locationID: str, new_status: str):
        if new_status not in ['undiscovered', 'discovered', 'solved']:
            raise ValueError(f"'{new_status}' is not a valid discovery status")

        visit_data = {
            "userID": userID,
            "locationID": locationID
        }
        
        existing_visit = db.visits.find_one(visit_data)
        
        if existing_visit is None:
            # Create a new visit record
            visit_data['timestamp'] = datetime.datetime.now(tz=ZoneInfo("UTC"))
            visit_data['visit_type'] = new_status
            db.visits.insert_one(visit_data)
        else:
            # Update the existing visit record
            db.visits.update_one(
                visit_data,
                {'$set': {'visit_type': new_status}}
            )

    def get_all_visits():
        """Retrieve all {name, location, visit_type} entires sorted by timestamp."""
        cursor = db.visits.find({}, {
            "userID": 1,
            "locationID": 1,
            "timestamp": 1,
            "visit_type": 1,
            "_id":0
            }).sort("timestamp", 1)
        
        # Extract and return list of (name, location, visit_type) dictionaries
        return [{"userID":doc["userID"], "locationID":doc["locationID"], "visit_type":doc["visit_type"]} for doc in cursor]
    
    def calculate_leaderboard():
        """
        Calculate the leaderboard based on the points system:
        2 points for each discovered location and 5 points for each solved location.
        
        Returns:
            list: A list of dictionaries with friendlyName and their total points, sorted by points in descending order.
        """
        leaderboard = {}

        visits = db.visits.find({}, {
            "userID": 1,
            "visit_type": 1,
            "_id": 0
        })

        for visit in visits:
            userID = visit["userID"]
            visit_type = visit["visit_type"]

            if userID not in leaderboard:
                leaderboard[userID] = 0

            if visit_type == "discovered":
                leaderboard[userID] += 2
            elif visit_type == "solved":
                leaderboard[userID] += 5

        # Convert userID to friendlyName and create the sorted leaderboard list
        sorted_leaderboard = []
        for userID, points in leaderboard.items():
            user = db.users.find_one({"userID": userID}, {"friendlyName": 1, "admin":1, "_id": 0})
            if user:
                is_admin = user.get('admin',False)
                if is_admin == False: # Admins can't show up on the leaderboard
                    sorted_leaderboard.append({"friendlyName": user["friendlyName"], "points": points})

        sorted_leaderboard.sort(key=lambda x: x["points"], reverse=True)

        return sorted_leaderboard

class CommentsDB:
    def create_comment(userID: str, locationID: str, comment: str):
        new_comment = {
            "userID": userID,
            "locationID": locationID,
            "comment": comment,
            "timestamp": datetime.datetime.now(tz=ZoneInfo("UTC"))
        }
        db.comments.insert_one(new_comment)



    def get_comments_for_location(locationID: str) -> list:
        pipeline = [
            {"$match": {"locationID": locationID}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "userID",
                    "foreignField": "userID",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$project": {
                    "_id": 0,
                    "friendlyName": "$user_info.friendlyName",
                    "timestamp": 1,
                    "comment": 1
                }
            },
            {"$sort": {"timestamp": -1}}
        ]
        comments_dict = list(db.comments.aggregate(pipeline))

        def format_chicago_time(dt: datetime) -> str:
            """Return the datetime formatted as Thu Feb 13,  8:43am (Chicago time)."""
            chicago_tz = ZoneInfo("America/Chicago")
            local_dt = dt.astimezone(chicago_tz)
            date = local_dt.strftime("%a %b %d")
            time = local_dt.strftime("%I:%M%p").lower()
            return f"{date}, {time}"

        for c in comments_dict:
            c['chicago_time'] = format_chicago_time(c['timestamp'])

        return [Comment(**c) for c in comments_dict]