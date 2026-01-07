import json
import uuid
from typing import List, Dict, Optional
from database import get_db_connection
from datetime import datetime

def save_to_db(
    project_path: str, 
    analyzed_data: List[Dict], 
    documentation: str, 
    kt_plan: Dict
) -> str:
    """
    Save project analysis, documentation, and KT plan to database
    Returns: project_id
    """
    
    # Generate unique project ID
    project_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Save project
        cursor.execute("""
            INSERT INTO projects (id, path, role, files_analyzed, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            project_id,
            project_path,
            "fullstack",  # You can pass this as parameter
            len(analyzed_data),
            "completed"
        ))
        
        # 2. Save analyzed files
        for file_data in analyzed_data:
            cursor.execute("""
                INSERT INTO files (
                    project_id, file_path, file_name, 
                    complexity, classes, functions, imports
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                file_data['file_path'],
                file_data['file_name'],
                file_data['complexity'],
                json.dumps(file_data.get('classes', [])),
                json.dumps(file_data.get('functions', [])),
                json.dumps(file_data.get('imports', []))
            ))
        
        # 3. Save documentation
        cursor.execute("""
            INSERT INTO documentation (project_id, content)
            VALUES (?, ?)
        """, (project_id, documentation))
        
        # 4. Save KT plan
        cursor.execute("""
            INSERT INTO kt_plans (project_id, plan)
            VALUES (?, ?)
        """, (project_id, json.dumps(kt_plan)))
        
        # 5. Initialize progress tracking (create entries for each day)
        if 'plan' in kt_plan:
            for day_plan in kt_plan['plan']:
                cursor.execute("""
                    INSERT INTO user_progress (project_id, day, completed)
                    VALUES (?, ?, ?)
                """, (project_id, day_plan['day'], False))
    
    print(f"✅ Saved project to database: {project_id}")
    return project_id

def get_project(project_id: str) -> Optional[Dict]:
    """Get project details by ID"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM projects WHERE id = ?
        """, (project_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None

def get_documentation(project_id: str) -> Optional[str]:
    """Get documentation for a project"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content FROM documentation 
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (project_id,))
        
        row = cursor.fetchone()
        
        if row:
            return row['content']
        return None

def get_kt_plan(project_id: str) -> Optional[Dict]:
    """Get KT plan for a project"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan FROM kt_plans 
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (project_id,))
        
        row = cursor.fetchone()
        
        if row:
            return json.loads(row['plan'])
        return None

def get_files(project_id: str) -> List[Dict]:
    """Get all analyzed files for a project"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM files WHERE project_id = ?
        """, (project_id,))
        
        rows = cursor.fetchall()
        
        files = []
        for row in rows:
            file_dict = dict(row)
            # Parse JSON strings back to objects
            file_dict['classes'] = json.loads(file_dict['classes'])
            file_dict['functions'] = json.loads(file_dict['functions'])
            file_dict['imports'] = json.loads(file_dict['imports'])
            files.append(file_dict)
        
        return files

def get_user_progress(project_id: str) -> List[Dict]:
    """Get user's KT progress"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_progress 
            WHERE project_id = ?
            ORDER BY day
        """, (project_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_progress(project_id: str, day: int, completed: bool, notes: str = None):
    """Update user's progress for a specific day"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if completed:
            cursor.execute("""
                UPDATE user_progress 
                SET completed = ?, completed_at = ?, notes = ?
                WHERE project_id = ? AND day = ?
            """, (True, datetime.now(), notes, project_id, day))
        else:
            cursor.execute("""
                UPDATE user_progress 
                SET completed = ?, notes = ?
                WHERE project_id = ? AND day = ?
            """, (False, notes, project_id, day))

def get_all_projects() -> List[Dict]:
    """Get all projects"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM projects 
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]