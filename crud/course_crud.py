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