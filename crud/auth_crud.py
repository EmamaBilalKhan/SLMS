from datetime import datetime
from datetime import timezone

from bson import ObjectId

from utils.email_verification_manager import verify_email_code
from utils.password_manager import check_password
from schema.user_schema import get_users_collection
from utils.email_verification_manager import send_verification_email

users_collection = get_users_collection()

def create_user(user):
    try:
        user["created_at"] = datetime.now(timezone.utc)
        user["updated_at"] = user["created_at"]
        result = users_collection.insert_one(user)
        user["_id"] = str(result.inserted_id)
        user["created_at"] = user["created_at"].isoformat()
        user["updated_at"] = user["updated_at"].isoformat()
        return user

    except Exception as e:
        return {"error": str(e)}

def login_user(email, password):
    try:
        user = users_collection.find_one({"email": email})
        if user:
            user_password = user["password"].encode("utf-8")
            is_correct_password = check_password(password, user_password)
            if is_correct_password:
                user["_id"] = str(user["_id"])
                if not user["is_verified"]:
                    send_verification_email(
                        to=user["email"], id=str(user["_id"])
                    )
                return user
            else:
                return {"client_error": "Invalid Password"}
        else:
            return {"client_error": "Invalid email"}
    except Exception as e:
        return {"error": str(e)}

def verify_user_email(user_id: str, code: str):
    try:
        response = verify_email_code(user_id, code)
        if response:
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_verified": True}})
        return {"is_verified": response}
    except Exception as e:
        return {"error": str(e)}