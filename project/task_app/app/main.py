from fastapi import FastAPI
from .api_routes import manage_task
from .promethus import promethus


app = FastAPI(title="Task Management System")
app.include_router(manage_task.router)
app.include_router(promethus.router)