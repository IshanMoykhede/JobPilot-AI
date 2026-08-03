import json

with open('simulation_state.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

drafts = d.get('drafts', {})

md = '# V2 Orchestrator Complete Resume Drafts\n\n'

for section, data in drafts.items():
    md += f'## {section.title()}\n\n'
    
    # data is a list of historical drafts. We want the latest one.
    if isinstance(data, list) and len(data) > 0:
        latest = data[-1]
    else:
        latest = data
        
    if isinstance(latest, list):
        for item in latest:
            if isinstance(item, dict):
                # Try to find a title
                title = item.get("title") or item.get("degree") or item.get("certification_name") or item.get("project_name") or item.get("role") or "Item"
                md += f'### {title}\n'
                
                # Format remaining keys
                for k, v in item.items():
                    if k in ["title", "degree", "certification_name", "project_name", "role"]:
                        continue
                    if isinstance(v, list):
                        md += f"- **{k.title()}**:\n"
                        for list_item in v:
                            md += f"  - {list_item}\n"
                    elif v:
                        md += f"- **{k.title()}**: {v}\n"
                md += "\n"
            else:
                md += f"- {item}\n"
    elif isinstance(latest, dict):
        for k, v in latest.items():
            if isinstance(v, list):
                md += f"### {k.title()}\n"
                for list_item in v:
                    md += f"- {list_item}\n"
                md += "\n"
            else:
                md += f"- **{k.title()}**: {v}\n"
    else:
        md += str(latest) + '\n\n'

with open('C:/Users/igmoy/.gemini/antigravity-ide/brain/0be3712e-5955-49a3-9166-0a8c10184dc7/full_draft_results.md', 'w', encoding='utf-8') as f:
    f.write(md)
