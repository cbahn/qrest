
class User:
    def __init__(self,
                 userId: str = None,
                 friendlyName: str = None,
                 sessionID: str = None,
                 role: str = None,
                 fingerprint: str = None):
        self.userId: str = userId
        self.sessionID: str = sessionID
        self.friendlyName: str = friendlyName
        self.role: str = role
        self.fingerprint: str = fingerprint

class Location:
    def __init__(self,
                 locationID: str = None,
                 fullName: str = None,
                 slug: str = None,
                 description: str = None,
                 puzzleText: str = None,
                 puzzleAnswer: str = None):
        self.locationID: str = locationID
        self.fullName: str = fullName
        self.slug: str = slug
        self.description: str = description
        self.puzzleText: str = puzzleText
        self.puzzleAnswer: str = puzzleAnswer