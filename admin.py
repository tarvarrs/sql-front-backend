from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin, BaseView, ModelView, expose
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from src.api.task import run_sql_query
from src.schemas.task import SQLRequest
from src.models import Task, TaskSolved, Achievement
from src.repositories.task import TaskRepository
# from src.models.user import User
from database import engine, get_db, AsyncSessionLocal
from src.api.dependencies import get_task_repository
import uvicorn
from config import settings
import httpx
from plotly.express import bar
import pandas as pd

app = FastAPI(title="Admin")
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="admin_session",
    max_age=3600
)

# for production
# app.add_middleware(HTTPSRedirectMiddleware)
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
templates = Jinja2Templates(directory="templates")
class TaskStatsView(BaseView):
    name = "Статистика по задачам"
    icon = "fa-solid fa-chart-bar"

    @expose("/stats/", methods=["GET"])
    async def stats_page(self, request: Request):
        async with AsyncSessionLocal() as session:
            repo = TaskRepository(session)
            stats = await repo.get_task_stats()
        df = pd.DataFrame(stats)
        fig = bar(df, x="task_global_id", y="total_solved", title="Решенные задачи")
        graph_html = fig.to_html(full_html=False)
        
        return templates.TemplateResponse(
            "stats.html", 
            {"request": request, "graph_html": graph_html}
        )

class TaskAdmin(ModelView, model=Task):
    column_list = [Task.task_id, Task.mission_id, Task.title, Task.description, Task.clue, Task.expected_result, Task.tags]
    form_columns = [Task.mission_id, Task.task_id, Task.title, Task.description, Task.clue, Task.correct_query, Task.tags] # Task.expected_result,
    column_searchable_list = [Task.task_id, Task.mission_id, Task.title]
    column_default_sort = (Task.task_global_id, False)
    can_create = True
    can_edit = True
    can_delete = True
    async def on_model_change(self, data, model, is_created, request):
        if is_created and data.get("correct_query"):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"http://192.168.1.206:8000/api/missions/0/tasks/1/run",
                        json={"sql_query": data["correct_query"]}
                    )
                    response.raise_for_status()
                    model.expected_result = {
                                            "data":response.json()["data"],
                                            "columns": response.json()["columns"],
                                            "row_count": response.json()["row_count"]
                                            }
                except Exception as e:
                    model.expected_result = f"Ошибка: {str(e)}"
        
        # await super().on_model_change(data, model, is_created)
        return await super().on_model_change(data, model, is_created, request)

class AchievementAdmin(ModelView, model=Achievement):
    column_list = [Achievement.achievement_id, Achievement.category_name, Achievement.icon, Achievement.name, Achievement.description, Achievement.historical_info, Achievement.tag, Achievement.required_count]
    column_searchable_list = [Achievement.achievement_id, Achievement.category_name, Achievement.name,]
    column_default_sort = (Achievement.achievement_id, False)
    # form_excluded_columns = [Achievement.users]

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session.update({"token": "admin-token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token or token != "admin-token":
            return False
        return True

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
admin = Admin(app, engine, base_url="/admin", authentication_backend=authentication_backend)

admin.add_view(TaskStatsView)
admin.add_view(TaskAdmin)
admin.add_view(AchievementAdmin)


if __name__ == "__main__":
    uvicorn.run("admin:app", host="0.0.0.0", port=8001, reload=True)