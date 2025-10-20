


class Profile:
    def __init__(self, email: str, username: str, password: str):
        self.__email = email
        self.__username = username
        self.__password = password  # in production, hash the password
    
    def profile(self):
        pass
        
