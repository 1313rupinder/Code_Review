import os
def login(user, password):
    secret = "admin123"
    unused = 5
    if password == secret:
        return True
    return False
print("done")