from pymongo import MongoClient
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client.clients
users = db.users
inventory = db.inventory


def delete_all(doc):

    doc.delete_many({})

def add_users(values):
    for user in values:
        users.insert_one(user)

def add_user_to_inventory(username):
    inventory.insert_one({"username":username, "files":[]})

def add_file_to_user(username, filename):
    inventory.update_one(
        {"username": username},
        { "$addToSet": {"files": filename}}
    )


def get_inventory_for_user(username):
    user_inventory = inventory.find_one({"username": username})
    if user_inventory == None:
        raise ValueError(username)
    return user_inventory["files"]

if __name__ == '__main__':

    #delete_all_enabled()

    user1 = {"username":"demo", "password": "demo", "enabled": True , "admin":False}
    user2 = {"username": "lahsini", "password": "lahsini", "enabled": True, "admin": True}

    not_found = {"username": "ttoto", "password": "toto"}
    add_users([user1])
    #result = users.find_one(not_found)
    add_user_to_inventory("demo")
    #add_user_to_inventory("lahsini")
    #print(get_inventory_for_user("lahsini"))
    #delete_all(inventory)
    print("users")
    for value in users.find():
        print(value)
    print("inventory")
    for value in inventory.find():
        print(value)


