from bson import ObjectId
from schema.assignment_schema import get_assignment_collection
from datetime import datetime, timezone
from schema.submission_schema import get_submissions_collection

assignment_collection = get_assignment_collection()
submissions_collection = get_submissions_collection()

def get_all_assignments():
    result = assignment_collection.aggregate([
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "title": 1,
                    "description": 1,
                    "role": 1,
                    "due_date": {"$toString": "$due_date"},
                }
            }
        ])
    if result is None:
        return []
    else:
        return list(result)

def create_new_assignment(assignment):
    try:
        assignment["due_date"] = datetime.strptime(assignment["due_date"], "%d/%m/%Y")
        result = assignment_collection.insert_one(assignment)
        assignment["_id"] = str(result.inserted_id)
        assignment["due_date"] = assignment["due_date"].strftime("%d/%m/%Y")
        return assignment
    except Exception as e:
        return {"error": str(e)}

def submit_new_assignment(submitted_assignment):
    try:
        submitted_assignment["submitted_at"] = datetime.now(timezone.utc)
        result = submissions_collection.insert_one(submitted_assignment)
        submitted_assignment["submitted_at"] = submitted_assignment["submitted_at"].isoformat()
        submitted_assignment["_id"] = str(result.inserted_id)
        return submitted_assignment
    except Exception as e:
        return {"error": str(e)}

def grade_submission(graded_submission):
        result = submissions_collection.update_one({"_id": ObjectId(graded_submission["submission_id"])}, {"$set": {"grade": graded_submission["grade"]}})
        if result.modified_count == 0:
            return {"error": "Assignment Grade Update Failed"}
        else:
            return {"success": "Assignment Grade Updated"}

def get_all_submissions():
    pipeline = [
        {
            "$match": {"grade": None}
        },
        {
            "$addFields": {
                "student_id": {"$toObjectId": "$student_id"},
                "assignment_id": {"$toObjectId": "$assignment_id"}
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "student_id",
                "foreignField": "_id",
                "pipeline": [
                    {"$project": {"username": 1, "_id": 0}}
                ],
                "as": "student"
            }
        },
        {
            "$unwind": "$student"
        },
        {
            "$lookup": {
                "from": "assignments",
                "localField": "assignment_id",
                "foreignField": "_id",
                "pipeline": [
                    {"$project": {"title": 1, "_id": 0}}
                ],
                "as": "assignment"
            }
        },
        {
            "$unwind": "$assignment"
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "student_name": "$student.username",
                "assignment_name": "$assignment.title",
                "submitted_at": {"$toString": "$submitted_at"},
                "grade": 1,
                "file_url": 1
            }
        }
    ]

    result = list(submissions_collection.aggregate(pipeline))
    if result is None:
        return []
    else:
        return list(result)