import logging
from typing import Dict, Any
from pathlib import Path
import urllib.request

import json

logger = logging.getLogger("research.tools.literature")


def _check_unpaywall(url: str) -> Dict[str, Any]:
    # Try to extract DOI if present in URL, otherwise we just try
    import re
    import urllib.request

    match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", url, re.I)
    if not match:
        return {"is_oa": True, "reason": "No DOI found in URL, assuming direct link."}
    doi = match.group(1)
    try:
        req_url = f"https://api.unpaywall.org/v2/{doi}?email=research@os.local"
        data = json.loads(urllib.request.urlopen(req_url).read())
        is_oa = data.get("is_oa", False)
        return {
            "is_oa": is_oa,
            "reason": "Unpaywall reported closed access."
            if not is_oa
            else "Unpaywall reported open access.",
        }
    except Exception as e:
        return {"is_oa": True, "reason": f"Unpaywall check failed: {e}, assuming open."}


def download_literature(url: str, filename: str, root: Path) -> Dict[str, Any]:
    try:
        oa_check = _check_unpaywall(url)
        if not oa_check["is_oa"]:
            logger.warning(f"Paywall warning for {url}: {oa_check['reason']}")
            # Log the reason to a file
            log_path = root / "workspace" / "logs" / "errors.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a") as f:
                f.write(f"Paywall warning for {url}: {oa_check['reason']}\n")
            return {
                "status": "error",
                "message": f"Article is behind a paywall: {oa_check['reason']}",
            }

        out_path = root / "inputs" / "literature" / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, out_path)
        return {"status": "success", "filepath": str(out_path.absolute())}
    except Exception as e:
        logger.error(f"Download literature failed: {e}")
        return {"status": "error", "message": str(e)}
