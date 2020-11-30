from pymongo import MongoClient
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client.clients
users = db.users
inventory = db.inventory

class DataBaseError(Exception):
    """Base Authentication Exception"""
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.msg) + ')'


class InventoryNotFound(DataBaseError):
    """no inventory for User """



def find_user_by_password(username, password):
    return users.find_one({"username" : username, "password":password})

def add_file_to_user(username, filename):
    inventory.update_one(
        {"username": username},
        { "$addToSet": {"files": filename}}
    )

def get_all_users():
    return users.find()

def insert_new_cv_for_user(username, filename):
    user_inventory = inventory.find_one({"username":username})
    if user_inventory == None:
        raise InventoryNotFound(username)
    add_file_to_user(username, filename)

def get_inventory_for_user(username):
    user_inventory = inventory.find_one({"username": username})
    if user_inventory == None:
        raise InventoryNotFound(username)
    return user_inventory["files"]
