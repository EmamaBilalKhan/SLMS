from config.db import get_db

db = get_db()

submission_collection_schema = {
    "$jsonSchema":{
        "bsonType" : "object",
        "required": ["assignment_id","student_id","file_url","submitted_at"],
        "properties":{
            "assignment_id" :{
                "bsonType":"string",
                "maxLength" : 24
            },
            "student_id" :{
                "bsonType":"string",
                "maxLength" : 24
            },
            "file_url" :{
                "bsonType":"string",
            },
            "created_at":{
                "bsonType":"date"
            },
            "grade":{
                "bsonType": ["string", "null"]
            }

        }
    }
}


existing_collections = db.list_collection_names()
if "submissions" not in existing_collections:
    try:
        db.create_collection("submissions", validator= submission_collection_schema)
        print("collection submissions created")
    except Exception as e:
        print(f"Error creating collection 'submissions': {e}")

def get_submissions_collection():
    db["submissions"].create_index([("student_id", 1)])
    return db["submissions"]