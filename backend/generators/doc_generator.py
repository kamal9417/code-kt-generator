import anthropic
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def generate_documentation(analyzed_files: List[Dict], role: str) -> str:
    """Generate comprehensive documentation using Claude"""
    
    # Prepare context
    context = prepare_context(analyzed_files)
    
    prompt = f"""You are a technical documentation expert. Generate comprehensive, beginner-friendly documentation for this codebase.

Project Analysis:
{context}

Generate documentation with these sections:
1. **Project Overview** - What does this project do?
2. **Architecture** - High-level structure and key components
3. **Key Modules** - Detailed explanation of main files/classes
4. **API Endpoints** (if applicable)
5. **Data Flow** - How data moves through the system
6. **Setup Instructions** - How to run this project

Focus on: {role} perspective
Make it clear for someone new to this codebase.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def prepare_context(analyzed_files: List[Dict]) -> str:
    """Convert analysis data to readable context"""
    context = []
    
    for file in analyzed_files:
        file_summary = f"\n### File: {file['file_name']}\n"
        
        if file['classes']:
            file_summary += "Classes:\n"
            for cls in file['classes']:
                file_summary += f"  - {cls['name']}: {cls.get('docstring', 'No description')}\n"
                if cls['methods']:
                    file_summary += f"    Methods: {', '.join([m['name'] for m in cls['methods']])}\n"
        
        if file['functions']:
            file_summary += "Functions:\n"
            for func in file['functions']:
                args = ', '.join(func['args'])
                file_summary += f"  - {func['name']}({args}): {func.get('docstring', 'No description')}\n"
        
        context.append(file_summary)
    
    return '\n'.join(context)