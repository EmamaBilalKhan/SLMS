from schema.submission_schema import get_submissions_collection

submissions_collection = get_submissions_collection()

def get_student_progress(student_id:str):
    result = submissions_collection.find(
        {"student_id": student_id, "grade": {"$ne": None}},
        {"_id": 0, "assignment_id": 1, "grade": 1, "file_url": 1}
    )
    if result is None:
        return []
    else:
        return list(result)