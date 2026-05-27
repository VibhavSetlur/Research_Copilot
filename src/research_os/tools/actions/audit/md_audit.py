import re
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
        
        from research_os.tools.actions.protocol import load_protocol
        try:
            protocol = load_protocol(protocol_name)
        except Exception as e:
            return {"status": "error", "message": f"Could not load protocol {protocol_name}: {e}"}
        
        # 2. Check for unfilled placeholders {placeholder}
        placeholders = re.findall(r'\{[^{}]+\}', content)
        
        # 4. Check banned phrases from writing_core.yaml
        banned_phrases = []
        try:
            core_proto = load_protocol("writing_core")
            banned_phrases = core_proto.get("rules", {}).get("banned_phrases", [])
        except Exception:
            core_proto = {}
            
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
