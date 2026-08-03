import os
import ast
import sys

def get_imports(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return []
            
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('app.'):
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith('app'):
                imports.add(node.module)
    return imports

def resolve_module_to_path(module_name):
    # e.g. app.services.resume_parser -> app/services/resume_parser.py
    # or app/services/resume_parser/__init__.py
    parts = module_name.split('.')
    base_path = os.path.join(*parts)
    
    py_file = base_path + '.py'
    if os.path.exists(py_file):
        return py_file
        
    init_file = os.path.join(base_path, '__init__.py')
    if os.path.exists(init_file):
        return init_file
        
    # Sometimes they import a class directly: from app.models.user import User -> module is app.models.user
    # But user.py exists.
    # What if it's app.models.user.User?
    # Let's try popping the last part
    if len(parts) > 1:
        parent_path = os.path.join(*parts[:-1]) + '.py'
        if os.path.exists(parent_path):
            return parent_path
            
    return None

def check_all(start_files):
    visited = set()
    queue = list(start_files)
    missing = []
    
    while queue:
        current_file = queue.pop(0)
        if current_file in visited:
            continue
        visited.add(current_file)
        
        imports = get_imports(current_file)
        for imp in imports:
            resolved = resolve_module_to_path(imp)
            if resolved is None:
                # Is it an ignored missing module like job_search?
                missing.append((current_file, imp))
            else:
                if resolved not in visited:
                    queue.append(resolved)
                    
    return visited, missing

start_files = [
    r"app\routes\candidate_profile.py",
    r"app\services\resume_parser.py",
    r"app\services\evidence_engine.py",
    r"app\services\evidence_engine_v2.py",
    r"app\services\knowledge_engine.py",
    r"app\services\project_intelligence.py",
    r"app\services\experience_intelligence.py",
    r"app\services\academic_intelligence.py",
    r"app\services\knowledge_fusion.py",
    r"app\services\candidate_synthesizer.py",
    r"app\schemas\candidate_profile.py",
    r"app\schemas\evidence.py",
    r"app\models\candidate_insights.py",
    r"app\embedding\services\embedding_pipeline.py",
    r"app\embedding\services\candidate_document_builder.py",
    r"app\graph\workflow.py",
    r"app\graph\state.py"
]

visited, missing = check_all(start_files)

print(f"Checked {len(visited)} internal Python files in the dependency tree.")
if not missing:
    print("SUCCESS: 100% of internal imports resolve to existing files.")
else:
    print("FAILED: Found broken internal imports:")
    for file, imp in missing:
        print(f"  - File '{file}' tries to import missing module '{imp}'")
