from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectInput(BaseModel):
    path: str
    role: str = "fullstack"

class ProjectResponse(BaseModel):
    project_id: str
    files_analyzed: int
    status: str

class FileAnalysis(BaseModel):
    file_path: str
    file_name: str
    classes: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    imports: List[str]
    complexity: int

class Documentation(BaseModel):
    project_id: str
    content: str

class KTPlan(BaseModel):
    project_id: str
    plan: Dict[str, Any]

class Project(BaseModel):
    id: str
    path: str
    role: str
    files_analyzed: int
    status: str
    created_at: datetime

class UserProgress(BaseModel):
    project_id: str
    day: int
    completed: bool
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None