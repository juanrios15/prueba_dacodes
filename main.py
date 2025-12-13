from __future__ import annotations

import sys

import uvicorn
from fastapi import FastAPI

from app.drivers.http_api import router as repair_orders_router


def create_app() -> FastAPI:
    app = FastAPI(title="Repair Orders System", version="1.0.0")
    app.include_router(repair_orders_router)
    return app


app = create_app()


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "run":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
