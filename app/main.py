from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.graph import GraphRepository

BASE_DIR = Path(__file__).resolve().parent
repo = GraphRepository()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    repo.close()


app = FastAPI(title=settings.app_name, description="A graph-powered project discovery explorer", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = Query(default="")):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"projects": repo.projects(q), "stats": repo.stats(), "health": repo.health(), "query": q},
    )


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_page(request: Request, project_id: str):
    project = repo.project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={"project": project, "connections": repo.connections(project_id), "health": repo.health()},
    )


@app.get("/api/health")
def api_health():
    return repo.health()


@app.get("/api/projects")
def api_projects(q: str = Query(default="", max_length=80)):
    return {"items": repo.projects(q)}


@app.get("/api/projects/{project_id}")
def api_project(project_id: str):
    project = repo.project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project": project, "connections": repo.connections(project_id)}


@app.get("/api/stats")
def api_stats():
    return repo.stats()
