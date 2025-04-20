import os
import sys
import asyncio
import subprocess
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.logger import configure_logging
from app.api.v1.router import api_router
from app.db.session import engine


configure_logging()
logger = logging.getLogger(__name__)

is_testing = os.getenv("TESTING", "0") == "1"


async def wait_for_db(max_retries: int = 10, delay: float = 1.0):
    for attempt  in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))
            logger.info("Database is up!")
            return
        except OperationalError:
            logger.warning(
                "Database is unavailable, retrying in %.1fs… (%d/%d)",
                delay, attempt, max_retries
            )
            await asyncio.sleep(delay)
    logger.error("Cannot connect to the database after %d attempts", max_retries)
    raise RuntimeError("Cannot connect to the database.")


def run_migrations():
    logger.info("Running migrations…")
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=os.getcwd(),
        check=True
    )
    logger.info("Migrations applied")
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Waiting for DB…")
    await wait_for_db()
    
    logger.info("Applying migrations…")
    run_migrations()
    
    yield
    logger.info("Shutdown complete")


app = FastAPI(
    title="WinDI Messenger", 
    version="0.1.0",
    lifespan=None if is_testing else lifespan
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    detail = str(exc)
    status_code = 404 if "not found" in detail.lower() else 400
    logger.warning("ValueError on %s %s – %s", request.method, request.url.path, detail)
    return JSONResponse(status_code=status_code, content={"detail": detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s", request.method, request.url.path,
        exc_info=True
    )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


app.include_router(api_router, prefix="/api/v1")
