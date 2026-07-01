import os
from fastapi import Request, HTTPException

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "iara_admin_2026")
ADMIN_COOKIE_VALUE = "iara_staff_authenticated"


def is_admin(request: Request) -> bool:
    return request.cookies.get("admin_session") == ADMIN_COOKIE_VALUE