from config.db import get_db

db = get_db()

assignment_collection_schema = {
    "$jsonSchema":{
        "bsonType": "object",
        "required" : ["title","description","course_id","due_date"],
        "properties" : {
            "title":{
                "bsonType" : "string",
                "minLength" : 5,
                "maxLength" : 20
            },
            "description" : {
                "bsonType" : "string",
                "minLength": 8,
                "maxLength" : 30
            },
            "course_id": {
                "bsonType" : "string",
                "maxLength" : 24
            },
            "due_date" : {
                "bsonType":"date"
            }
        }
    }
}

existing_collections = db.list_collection_names()
if "assignments" not in existing_collections:
    try:
        db.create_collection("assignments", validator= assignment_collection_schema)
        print("collection assignments created")
    except Exception as e:
        print(f"Error creating collection 'student_course': {e}")

def get_assignment_collection():
    return db["assignments"]