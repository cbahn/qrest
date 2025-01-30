from marino.db import UsersDB
from marino.models import User



def create_user_d(friendly_name: str):
    if len(friendly_name) > 5:
        return "fail, name too long"
    newUser = User(
        friendlyName=friendly_name,
        userId="butt6969",
        role = "admin"
    )
    UsersDB.create(newUser)