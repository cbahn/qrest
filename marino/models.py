
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