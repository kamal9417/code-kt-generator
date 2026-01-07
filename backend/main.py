from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions
from database import init_database, get_db_connection
from curd import (
    save_to_db, 
    get_project, 
    get_documentation, 
    get_kt_plan,
    get_files,
    get_user_progress,
    update_progress,
    get_all_projects
)
from models import ProjectInput, ProjectResponse

# Import analyzers and generators
from analyzer.python_analyzer import analyze_python_file
from generators.doc_generator import generate_documentation
from generators.kt_generator import create_kt_plan
from rag.embeddings import create_embeddings

app = FastAPI(title="Code KT Generator API")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    print("🚀 Server started successfully!")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Code KT Generator API",
        "version": "1.0.0",
        "endpoints": [
            "/api/analyze",
            "/api/projects",
            "/api/docs/{project_id}",
            "/api/kt/{project_id}",
            "/api/chat"
        ]
    }

@app.post("/api/analyze", response_model=ProjectResponse)
async def analyze_project(project: ProjectInput):
    """Analyze a project folder and generate documentation"""
    
    # Validate path
    if not os.path.exists(project.path):
        raise HTTPException(status_code=400, detail="Path does not exist")
    
    project_path = Path(project.path)
    
    try:
        # 1. Scan files
        files = scan_project_files(project_path)
        
        if not files:
            raise HTTPException(status_code=400, detail="No supported files found")
        
        # 2. Analyze each file
        analyzed_data = []
        for file_path in files:
            analysis = analyze_file(file_path)
            if analysis:
                analyzed_data.append(analysis)
        
        # 3. Generate documentation
        documentation = generate_documentation(analyzed_data, project.role)
        
        # 4. Create KT plan
        kt_plan = create_kt_plan(analyzed_data, project.role)
        
        # 5. Save to database
        project_id = save_to_db(
            str(project_path), 
            analyzed_data, 
            documentation, 
            kt_plan
        )
        
        # 6. Create embeddings for RAG
        create_embeddings(analyzed_data, project_id)
        
        return ProjectResponse(
            project_id=project_id,
            files_analyzed=len(analyzed_data),
            status="completed"
        )
    
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"❌ Error analyzing project: {error_details}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects():
    """Get all projects"""
    projects = get_all_projects()
    return {"projects": projects}

@app.get("/api/docs/{project_id}")
async def get_project_documentation(project_id: str):
    """Get documentation for a project"""
    
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    documentation = get_documentation(project_id)
    files = get_files(project_id)
    
    return {
        "project": project,
        "documentation": documentation,
        "files": files
    }

@app.get("/api/kt/{project_id}")
async def get_kt_plan_endpoint(project_id: str):
    """Get KT plan for a project"""
    
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    kt_plan = get_kt_plan(project_id)
    progress = get_user_progress(project_id)
    
    return {
        "project": project,
        "kt_plan": kt_plan,
        "progress": progress
    }

@app.post("/api/progress/{project_id}")
async def update_kt_progress(
    project_id: str, 
    day: int, 
    completed: bool, 
    notes: str = None
):
    """Update progress for a KT day"""
    
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_progress(project_id, day, completed, notes)
    
    return {"status": "success", "message": "Progress updated"}

class ChatRequest(BaseModel):
    question: str
    project_id: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Answer questions about the codebase"""

    from rag.embeddings import search_codebase
    import anthropic

    project = get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Search for relevant code
    results = search_codebase(request.question, request.project_id)

    # Prepare context
    context = '\n\n'.join(results['documents'][0])

    # Ask Claude (or use mock if no API key)
    if os.environ.get("ANTHROPIC_API_KEY"):
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = f"""Answer this question about the codebase:

Question: {request.question}

Relevant Code Information:
{context}

Provide a clear, helpful answer with code examples if needed."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = message.content[0].text
    else:
        answer = f"Mock answer for: {request.question}\n\nRelevant files found: {len(results['documents'][0])}"
    
    return {
        "answer": answer,
        "sources": results['metadatas'][0]
    }

def scan_project_files(project_path: Path) -> List[Path]:
    """Scan project folder for code files"""
    supported_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx'}
    ignore_dirs = {'node_modules', 'venv', '__pycache__', '.git', 'dist', 'build'}
    
    files = []
    for file_path in project_path.rglob('*'):
        if any(ignored in file_path.parts for ignored in ignore_dirs):
            continue
        
        if file_path.suffix in supported_extensions:
            files.append(file_path)
    
    return files

def analyze_file(file_path: Path) -> dict:
    """Analyze a single file"""
    if file_path.suffix == '.py':
        return analyze_python_file(file_path)
    # Add more analyzers as needed
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import os
# from pathlib import Path
# from typing import List
# import sqlite3

# from backend.generators.doc_generator import generate_documentation
# from backend.generators.kt_generator import create_kt_plan

# app = FastAPI()

# # CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ProjectInput(BaseModel):
#     path: str
#     role: str = "fullstack"  # frontend, backend, fullstack

# class ProjectResponse(BaseModel):
#     project_id: str
#     files_analyzed: int
#     status: str

# @app.post("/api/analyze", response_model=ProjectResponse)
# async def analyze_project(project: ProjectInput):
#     """Analyze a project folder and generate documentation"""
    
#     # Validate path
#     if not os.path.exists(project.path):
#         raise HTTPException(status_code=400, detail="Path does not exist")
    
#     project_path = Path(project.path)
    
#     # Scan files
#     files = scan_project_files(project_path)
    
#     # Analyze each file
#     analyzed_data = []
#     for file_path in files:
#         analysis = analyze_file(file_path)
#         if analysis:
#             analyzed_data.append(analysis)
    
#     # Generate documentation
#     doc_id = generate_documentation(analyzed_data, project.role)
    
#     # Create KT plan
#     kt_plan = create_kt_plan(analyzed_data, project.role)
    
#     # Store in database
#     project_id = save_to_db(project.path, analyzed_data, doc_id, kt_plan)
    
#     return ProjectResponse(
#         project_id=project_id,
#         files_analyzed=len(analyzed_data),
#         status="completed"
#     )

# def scan_project_files(project_path: Path) -> List[Path]:
#     """Scan project folder for code files"""
#     supported_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go'}
#     ignore_dirs = {'node_modules', 'venv', '__pycache__', '.git', 'dist', 'build'}
    
#     files = []
#     for file_path in project_path.rglob('*'):
#         # Skip ignored directories
#         if any(ignored in file_path.parts for ignored in ignore_dirs):
#             continue
        
#         if file_path.suffix in supported_extensions:
#             files.append(file_path)
    
#     return files

# def analyze_file(file_path: Path) -> dict:
#     """Analyze a single file"""
#     # Implementation based on file type
#     if file_path.suffix == '.py':
#         from analyzers.python_analyzer import analyze_python_file
#         return analyze_python_file(file_path)
#     elif file_path.suffix in {'.js', '.jsx', '.ts', '.tsx'}:
#         from analyzers.js_analyzer import analyze_js_file
#         return analyze_js_file(file_path)
    
#     return None

# @app.post("/api/chat")
# async def chat(question: str, project_id: str):
#     """Answer questions about the codebase"""
    
#     from rag.embeddings import search_codebase
    
#     # Search for relevant code
#     results = search_codebase(question, project_id)
    
#     # Prepare context
#     context = '\n\n'.join(results['documents'][0])
    
#     # Ask Claude
#     prompt = f"""Answer this question about the codebase:

# Question: {question}

# Relevant Code Information:
# {context}

# Provide a clear, helpful answer with code examples if needed."""

#     message = client.messages.create(
#         model="claude-sonnet-4-20250514",
#         max_tokens=1000,
#         messages=[{"role": "user", "content": prompt}]
#     )
    
#     return {
#         "answer": message.content[0].text,
#         "sources": results['metadatas'][0]
#     }