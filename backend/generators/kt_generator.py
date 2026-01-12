from openai import OpenAI
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def create_kt_plan(analyzed_files: List[Dict], role: str) -> Dict:
    """Generate personalized Knowledge Transfer plan"""
    
    context = prepare_kt_context(analyzed_files, role)
    
    prompt = f"""You are an expert engineering onboarding specialist. Create a detailed 10-day Knowledge Transfer plan for a new {role} developer joining this project.

Project Information:
{context}

Create a day-by-day learning plan with:
- Day number and focus area
- Key files to study
- Concepts to understand
- Hands-on exercises
- Knowledge checkpoints (questions to validate understanding)

Format as JSON:
{{
  "plan": [
    {{
      "day": 1,
      "title": "...",
      "focus": "...",
      "files_to_study": ["..."],
      "concepts": ["..."],
      "exercise": "...",
      "checkpoint_questions": ["..."]
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    import re

    # Extract JSON from OpenAI's response (handle markdown code blocks)
    response_text = response.choices[0].message.content

    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(1)

    # If no code block, try to find JSON object
    elif '{' in response_text:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse KT plan JSON. Response was:\n{response_text[:500]}")
        raise ValueError(f"Failed to parse Claude's response as JSON: {str(e)}")

def prepare_kt_context(analyzed_files: List[Dict], role: str) -> str:
    """Prepare context for KT generation"""
    
    # Group files by complexity
    simple = [f for f in analyzed_files if f['complexity'] < 5]
    moderate = [f for f in analyzed_files if 5 <= f['complexity'] < 15]
    complex = [f for f in analyzed_files if f['complexity'] >= 15]
    
    context = f"""
Role: {role}

File Statistics:
- Total files: {len(analyzed_files)}
- Simple files: {len(simple)}
- Moderate files: {len(moderate)}
- Complex files: {len(complex)}

Key Files:
{list_key_files(analyzed_files)}
"""
    return context

def list_key_files(files: List[Dict]) -> str:
    """List most important files"""
    # Sort by complexity
    sorted_files = sorted(files, key=lambda x: x['complexity'], reverse=True)
    
    output = []
    for f in sorted_files[:10]:  # Top 10 files
        output.append(f"- {f['file_name']} (complexity: {f['complexity']})")
    
    return '\n'.join(output)