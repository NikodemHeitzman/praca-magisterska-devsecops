# Test cases for python-asgi-debug-enabled (run: semgrep --test semgrep-rules/).
# Written for the class "debug mode on in an ASGI app" (CWE-209, CWE-489), not for the catalogue patch.
import os

import fastapi
from fastapi import FastAPI
from starlette.applications import Starlette

# ruleid: python-asgi-debug-enabled
app = FastAPI(debug=True)

# ruleid: python-asgi-debug-enabled
app2 = fastapi.FastAPI(title="demo", debug=True, version="1.0")

# ruleid: python-asgi-debug-enabled
app3 = Starlette(debug=True, routes=[])

DEBUG = True
# ruleid: python-asgi-debug-enabled
app4 = FastAPI(debug=DEBUG)

app5 = FastAPI()
# ruleid: python-asgi-debug-enabled
app5.debug = True

# ok: python-asgi-debug-enabled
app6 = FastAPI()

# ok: python-asgi-debug-enabled
app7 = FastAPI(debug=False)

# ok: python-asgi-debug-enabled
app8 = FastAPI(debug=os.getenv("APP_DEBUG") == "1")


class Settings:
    debug = True


settings = Settings()
# ok: python-asgi-debug-enabled
settings.debug = True
