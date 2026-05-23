import re
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("research.tools.audit")

def validate_md_template(filepath: str, protocol_name: str, root: Path) -> Dict[str, Any]:
    try:
        p = root / filepath
        if not p.exists() or not p.is_file():
            return {"status": "error", "message": f"File not found at {filepath}"}
            
        content = p.read_text()
        
        from research_os.server import get_protocol
        
        protocol_res = get_protocol(protocol_name, root)
        if "error" in protocol_res:
            return {"status": "error", "message": f"Could not load protocol {protocol_name}: {protocol_res['error']}"}
            
        protocol = yaml.safe_load(protocol_res["content"])
        
        # 2. Check for unfilled placeholders {placeholder}
        placeholders = re.findall(r'\{[^{}]+\}', content)
        
        # 4. Check banned phrases from writing_core.yaml
        banned_phrases = []
        core_res = get_protocol("writing_core", root)
        if "error" not in core_res:
            core_proto = yaml.safe_load(core_res["content"])
            banned_phrases = core_proto.get("rules", {}).get("banned_phrases", [])
            
        found_banned = []
        lower_content = content.lower()
        for phrase in banned_phrases:
            if phrase.lower() in lower_content:
                found_banned.append(phrase)
                
        errors = []
        if placeholders:
            errors.append(f"Found unfilled placeholders: {list(set(placeholders))}")
        if found_banned:
            errors.append(f"Found banned phrases: {found_banned}")
            
        # Check required sections
        if "template" in protocol:
            template = protocol["template"]
            headers = re.findall(r'^(#+ .*)$', template, flags=re.MULTILINE)
            missing_headers = []
            for h in headers:
                h_clean = re.sub(r'\{[^{}]+\}', '', h).strip()
                if h_clean and h_clean not in content:
                    missing_headers.append(h_clean)
            if missing_headers:
                errors.append(f"Missing required sections: {missing_headers}")
                
        if errors:
            return {"status": "error", "message": "Validation failed", "errors": errors}
            
        return {"status": "success", "message": "File passes MD template validation."}
        
    except Exception as e:
        logger.error(f"MD validate failed: {e}")
        return {"status": "error", "message": str(e)}
