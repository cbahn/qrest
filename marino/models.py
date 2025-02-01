
class User:
    def __init__(self,
                 userId: str = None,
                 friendlyName: str = None,
                 sessionID: str = None,
                 role: str = None):
        self.userId: str = userId
        self.sessionID: str = sessionID
        self.friendlyName: str = friendlyName
        self.role: str = role

class Location:
    def __init__(self,
                 locationID: str = None,
                 fullName: str = None,
                 slug: str = None):
        self.locationID: str = locationID
        self.fullName: str = fullName
        self.slug: str = slug