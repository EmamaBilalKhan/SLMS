from config.db import get_db

db = get_db()

user_schema = {
    "$jsonSchema" : {
        "bsonType": "object",
        "required": ["username", "email", "password", "role"],
        "properties": {
            "username": {"bsonType": "string", "minLength": 8, "maxLength": 15},
            "email": {"bsonType": "string", "pattern": "^.+@[^.].*\\.[a-z]{2,10}$",
                "description": "Email must be a valid format",},
            "password": {"bsonType": "string"},
            "role": {
                "bsonType": "string",
                "enum": ["Admin", "Student", "Teacher"]
            },
            "created_at":{"bsonType":"date"},
            "updated_at":{"bsonType":"date"},
            "is_verified": {"bsonType": "bool"}
        }
    }
}

existing_collections = db.list_collection_names()
if "users" not in existing_collections:
    try:
        db.create_collection("users", validator=user_schema)
        db["users"].create_index([("email", 1)], unique=True)

        print("Collection 'users' created successfully.")

    except Exception as e:
        print(f"Error creating collection 'users': {e}")

def get_users_collection():
    return db["users"]