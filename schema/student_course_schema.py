from config.db import get_db

db = get_db()

student_course_schema = {
    "$jsonSchema": {
        "bsonType" : "object",
        "required": ["student_id", "course_id"],
        "properties":{
            "student_id" :{
                "bsonType":"string",
                "maxLength": 24
            },
            "course_id":{
                "bsonType": "string",
                "maxLength": 24
            }
        }

    }
}

existing_collections = db.list_collection_names()
if "student_course" not in existing_collections:
    try:
        db.create_collection("student_course", validator = student_course_schema)
        print("Collection 'student_course' created successfully.")

    except Exception as e:
        print(f"Error creating collection 'student_course': {e}")


def get_student_course_collection():
    return db["student_course"]