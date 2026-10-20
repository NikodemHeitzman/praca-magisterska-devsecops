# Test cases for python-log-injection (run: semgrep --test semgrep-rules/).
# Written for the CWE-117 class, not for the catalogue patch: several FastAPI input kinds,
# logging styles and sanitisers.
import json
import logging
import re
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Form, Header
from pydantic import BaseModel
from starlette.requests import Request

app = FastAPI()
router = APIRouter()
logger = logging.getLogger(__name__)


class LoginForm(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(form: LoginForm):
    # ruleid: python-log-injection
    logger.warning("failed login for %s", form.username)


@app.post("/login-form")
async def login_form(username: str = Form(...)):
    # ruleid: python-log-injection
    logger.info(f"login attempt: {username}")


@router.get("/items/{name}")
def read_item(name: str, user_agent: str = Header(None)):
    # ruleid: python-log-injection
    logging.info("item " + name)
    # ruleid: python-log-injection
    logger.debug("ua=%s", user_agent)


@app.get("/search")
def search(q):
    message = "search: %s" % q
    # ruleid: python-log-injection
    logger.error(message)


@app.get("/raw")
async def raw(request: Request):
    # ruleid: python-log-injection
    logger.info("query %s", request.query_params.get("q"))
    body = await request.json()
    # ruleid: python-log-injection
    logger.log(logging.INFO, "body %s", body["user"])


@app.post("/login-safe")
def login_safe(form: LoginForm):
    safe = form.username.replace("\r", "\\r").replace("\n", "\\n")
    # ok: python-log-injection
    logger.warning("failed login for %s", safe)
    # ok: python-log-injection
    logger.warning("failed login for %r", repr(form.username))
    # ok: python-log-injection
    logger.warning("failed login for %s", re.sub(r"[\r\n]", "_", form.username))
    # ok: python-log-injection
    logger.warning("failed login for %s", json.dumps(form.username))


@app.get("/users/{user_id}")
def read_user(user_id: int, ref: uuid.UUID):
    # ok: python-log-injection
    logger.info("user %s ref %s", user_id, ref)


@app.get("/count")
def count(q: str):
    # ok: python-log-injection
    logger.info("query length %d", len(q))


def get_current_user():
    return "alice"


@app.get("/me")
def me(user=Depends(get_current_user), other: str = Depends(get_current_user)):
    # ok: python-log-injection
    logger.info("current user %s %s", user, other)


@app.get("/me2")
async def me2(user: Annotated[str, Depends(get_current_user)], q: Annotated[str, Header()]):
    # ok: python-log-injection
    logger.info("current user %s", user)
    # ruleid: python-log-injection
    logger.info("header %s", q)


def not_a_route(name):
    # ok: python-log-injection
    logger.info("internal call %s", name)


@app.get("/static")
def static_message():
    # ok: python-log-injection
    logger.info("static message")
