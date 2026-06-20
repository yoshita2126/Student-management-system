from fastapi import HTTPException

def authorize_role(
    user_role,
    allowed_roles
):

    if user_role not in allowed_roles:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )