from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from prometheus_client import Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from task_app.app.database_setup.db_session import get_db
from sqlalchemy import text
import time
from fastapi import APIRouter
DB_UP = Gauge("db_up", "Database connectivity status (1=up, 0=down)")
DB_QUERY_LATENCY = Histogram("db_query_latency_seconds", "DB query latency in seconds")
DB_ERRORS_TOTAL = Counter("db_errors_total", "Total number of DB errors")

router = APIRouter(tags=["Health"])
@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    start = time.time()
    try:
        db.execute(text("SELECT 1"))
        DB_UP.set(1)
    except Exception:
        DB_UP.set(0)
        DB_ERRORS_TOTAL.inc()
    finally:
        DB_QUERY_LATENCY.observe(time.time() - start)
    
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
