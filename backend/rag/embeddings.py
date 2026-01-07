import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def create_embeddings(analyzed_files: List[Dict], project_id: str):
    """Create embeddings for all code files"""
    
    collection = chroma_client.get_or_create_collection(
        name=f"project_{project_id}",
        embedding_function=embedding_func
    )
    
    documents = []
    metadatas = []
    ids = []
    
    for idx, file in enumerate(analyzed_files):
        # Create searchable text from file analysis
        text = create_searchable_text(file)
        
        documents.append(text)
        metadatas.append({
            'file_path': file['file_path'],
            'file_name': file['file_name'],
            'complexity': file['complexity']
        })
        ids.append(f"file_{idx}")
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def create_searchable_text(file: Dict) -> str:
    """Convert file analysis to searchable text"""
    parts = [f"File: {file['file_name']}"]
    
    for cls in file.get('classes', []):
        parts.append(f"Class {cls['name']}: {cls.get('docstring', '')}")
        for method in cls.get('methods', []):
            parts.append(f"Method {method['name']}: {method.get('docstring', '')}")
    
    for func in file.get('functions', []):
        parts.append(f"Function {func['name']}: {func.get('docstring', '')}")
    
    return '\n'.join(parts)

def search_codebase(query: str, project_id: str, n_results: int = 5) -> List[Dict]:
    """Search codebase for relevant information"""
    
    collection = chroma_client.get_collection(
        name=f"project_{project_id}",
        embedding_function=embedding_func
    )
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return results