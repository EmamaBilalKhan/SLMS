from schema.user_schema import get_users_collection

users_collection = get_users_collection()

def get_all_users():
    try:
        results = users_collection.aggregate([
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "username": 1,
                    "email": 1,
                    "role": 1,
                    "created_at": {"$toString": "$created_at"},
                    "updated_at": {"$toString": "$updated_at"}
                }
            }
        ])
        return list(results)
    except Exception as e:
        return {"error": str(e)}