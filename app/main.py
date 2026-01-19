import os
import uuid
import json
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Submittal Checker", version="0.2.1")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DATA_FILE = "projects.json"

def load_projects() -> Dict[str, dict]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_projects(projects: Dict[str, dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)

# Load existing projects on startup
PROJECTS: Dict[str, dict] = load_projects()

@app.get("/health")
def health():
    return {"status": "ok"}

class ProjectCreateResponse(BaseModel):
    project_id: str

class ProjectResponse(BaseModel):
    project_id: str
    name: Optional[str] = None
    created_at: str
    plan_pdf: Optional[str] = None
    submittal_pdf: Optional[str] = None

@app.post("/projects", response_model=ProjectCreateResponse)
def create_project(name: Optional[str] = None):
    project_id = str(uuid.uuid4())
    PROJECTS[project_id] = {
        "project_id": project_id,
        "name": name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "plan_pdf": None,
        "submittal_pdf": None,
    }
    save_projects(PROJECTS)
    return {"project_id": project_id}

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    proj = PROJECTS.get(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@app.post("/projects/{project_id}/upload")
async def upload_pdf(
    project_id: str,
    file: UploadFile = File(...),
    doc_type: str = Form(...),  # "plan" or "submittal"
):
    proj = PROJECTS.get(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    doc_type = doc_type.strip().lower()
    if doc_type not in ("plan", "submittal"):
        raise HTTPException(status_code=400, detail="doc_type must be 'plan' or 'submittal'")

    # Basic file validation
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    safe_name = file.filename.replace("/", "_").replace("\\", "_")
    save_name = f"{project_id}_{doc_type}_{safe_name}"
    save_path = os.path.join(UPLOAD_DIR, save_name)

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    with open(save_path, "wb") as f:
        f.write(contents)

    if doc_type == "plan":
        proj["plan_pdf"] = save_path
    else:
        proj["submittal_pdf"] = save_path

    PROJECTS[project_id] = proj
    save_projects(PROJECTS)

    return {"ok": True, "project_id": project_id, "doc_type": doc_type, "path": save_path}
