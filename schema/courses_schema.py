from config.db import get_db

db = get_db()

course_schema = {
    "$jsonSchema" : {
        "bsonType": "object",
        "required": ["course_name", "description", "teacherID"],
        "properties": {
            "course_name": {"bsonType": "string", "minLength": 5, "maxLength": 15},
            "description": {"bsonType": "string", "minLength": 5, "maxLength": 30},
            "teacherID": {"bsonType": "string", "maxLength": 24},
            "created_at": {"bsonType":"date"}
        }
    }
}

existing_collections = db.list_collection_names()
if "courses" not in existing_collections:
    try:
        db.create_collection("courses", validator=course_schema)

        print("Collection 'courses' created successfully.")

    except Exception as e:
        print(f"Error creating collection 'courses': {e}")

def get_courses_collection():
    return db["courses"]