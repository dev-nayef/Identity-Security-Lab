from fastapi import FastAPI, Request, Response, HTTPException, Depends
from app.auth.session_security import (
    create_session,
    validate_token,
    revoke_session,
)
from app.auth.csrf_protection import (
    create_csrf_token,
    validate_csrf_token,
    revoke_csrf_token,
)


app = FastAPI(
    title="Identity Authentication Lab",
    version="0.2.0",
)


SESSION_COOKIE = "lab_session"
TOKEN_COOKIE = "lab_protection"
CSRF_COOKIE = "lab_csrf"


def get_client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


def require_protection(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE)
    protection_token = request.cookies.get(TOKEN_COOKIE)

    if not session_id or not protection_token:
        raise HTTPException(
            status_code=403,
            detail="Protection token required",
        )

    user_agent = request.headers.get("user-agent", "")
    ip_address = get_client_ip(request)

    valid = validate_token(
        session_id=session_id,
        protection_token=protection_token,
        user_agent=user_agent,
        ip_address=ip_address,
        bind_ip=False,
    )

    if not valid:
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired protection token",
        )

    return session_id


def require_csrf(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE)
    csrf_token = request.headers.get("X-CSRF-Token")

    if not session_id:
        raise HTTPException(
            status_code=403,
            detail="Session required",
        )

    if not csrf_token:
        raise HTTPException(
            status_code=403,
            detail="CSRF token required",
        )

    if not validate_csrf_token(
        session_id=session_id,
        token=csrf_token,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid CSRF token",
        )

    return True


@app.get("/")
async def root(request: Request, response: Response):
    session_id = request.cookies.get(SESSION_COOKIE)
    protection_token = request.cookies.get(TOKEN_COOKIE)

    if not session_id or not protection_token:
        user_agent = request.headers.get("user-agent", "")
        ip_address = get_client_ip(request)

        session_id, protection_token = create_session(
            user_agent=user_agent,
            ip_address=ip_address,
        )

        response.set_cookie(
            key=SESSION_COOKIE,
            value=session_id,
            httponly=True,
            samesite="strict",
            secure=False,
            max_age=1800,
            path="/",
        )

        response.set_cookie(
            key=TOKEN_COOKIE,
            value=protection_token,
            httponly=True,
            samesite="strict",
            secure=False,
            max_age=1800,
            path="/",
        )

    csrf_token = create_csrf_token(session_id)

    response.set_cookie(
        key=CSRF_COOKIE,
        value=csrf_token,
        httponly=False,
        samesite="strict",
        secure=False,
        max_age=1800,
        path="/",
    )

    return {
        "project": "Identity Authentication Lab",
        "status": "running",
        "protection": "initialized",
        "csrf": "initialized",
    }


@app.get("/api/protected")
async def protected_endpoint(
    _: str = Depends(require_protection),
):
    return {
        "status": "success",
        "message": "Protected request accepted",
    }


@app.post("/api/protected-action")
async def protected_action(
    _: str = Depends(require_protection),
    __: bool = Depends(require_csrf),
):
    return {
        "status": "success",
        "message": "Protected action accepted",
        "security": "protection-token + csrf-token",
    }


@app.post("/auth/logout")
async def logout(
    request: Request,
    response: Response,
):
    session_id = request.cookies.get(SESSION_COOKIE)

    if session_id:
        revoke_session(session_id)
        revoke_csrf_token(session_id)

    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(TOKEN_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")

    return {
        "status": "logged_out",
    }