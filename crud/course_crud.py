from bson import ObjectId
from schema.courses_schema import get_courses_collection
from schema.student_course_schema import get_student_course_collection
from datetime import datetime
courses_collection = get_courses_collection()
student_course_collection = get_student_course_collection()

def create_course(course):
    try:
        course["created_at"] = datetime.now()
        result = courses_collection.insert_one(course)
        course["_id"] = str(result.inserted_id)
        course["created_at"] = course["created_at"].strftime("%c")
        return course

    except Exception as e:
        return {"error": str(e)}

def get_all_courses():
    try:
        pipeline = [
            {
                "$addFields": {
                    "teacherID": {"$toObjectId": "$teacherID"},
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "teacherID",
                    "foreignField": "_id",
                    "pipeline": [
                        {"$project": {"username": 1, "_id": 0}}
                    ],
                    "as": "teacher"
                }
            },
            {
                "$unwind": "$teacher"
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "teacher_name": "$teacher.username",
                    "course_name": 1,
                    "description": 1,
                    "created_at": {"$toString": "$created_at"}
                }
            }
        ]

        result = list(courses_collection.aggregate(pipeline))
        if result is None:
            return []
        else:
            return list(result)
    except Exception as e:
        return {"error": str(e)}

def register_new_course(new_course_reg):
    try:
        result = student_course_collection.insert_one(new_course_reg)
        new_course_reg["_id"] = str(result.inserted_id)
        return new_course_reg
    except Exception as e:
        return  {"error": str(e)}

def drop_course(enrollment_id):
    try:
        student_course_collection.delete_one({"_id": ObjectId(enrollment_id)})
        return "course dropped"
    except Exception as e:
        return  {"error": str(e)}

def get_all_enrollments_status(student_id):

    try:

        pipeline = [
            {
                "$addFields": {
                    "teacher_id_obj": {"$toObjectId": "$teacherID"},
                }
            },
            {

                "$lookup": {
                    "from": "student_course",
                    "let": {"courseId": {"$toString": "$_id"}},
                    "pipeline": [
                        {"$match": {"$expr": {"$and": [
                            {"$eq": ["$course_id", "$$courseId"]},
                            {"$eq": ["$student_id", student_id]}
                        ]}}},
                        {"$limit": 1}
                    ],
                    "as": "enrollment"
                }
            },

            {
                "$lookup": {
                    "from": "users",
                    "localField": "teacher_id_obj",
                    "foreignField": "_id",
                    "as": "teacher"
                }
            },

            {"$unwind": {"path": "$teacher", "preserveNullAndEmptyArrays": True}},

            {
                "$project": {
                    "_id": 0,
                    "course_id": {"$toString": "$_id"},
                    "course_name": 1,
                    "description": 1,
                    "created_at": {"$toString": "$created_at"},
                    "teacher_name": "$teacher.username",
                    "enrollment_id": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$enrollment"}, 0]},
                            "then": {"$toString": {"$arrayElemAt": ["$enrollment._id", 0]}},
                            "else": None
                        }
                    }
                }
            }
        ]

        result = list(courses_collection.aggregate(pipeline))

        if result is None:
            return []
        else:
            return list(result)
    except Exception as e:
        return {"error": str(e)}