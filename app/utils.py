import json, os
from datetime import datetime
from typing import Dict, Any, List

def load_personas(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def assumption_summary(a: Dict[str, Any]) -> str:
    return (
        f"Mix: US {a['us_eq']}% / Intl {a['intl_eq']}% / FI {a['fi']}% / AltsHF {a['altshf']}% / AltsPE {a['altspe']}% / AltsRE {a['altsre']}%  / Cash {a['cash']}%\n"
        f"Turnover {a['turnover']}%, Yield {a['yield']}%, Horizon {a['horizon']}y\n"
        f"Lots: {a['lots']}, HarvestLosses: {a['harvest']}, Reinvest: {a['reinvest']}\n"
        f"Tax: Ord {a['ord_rate']}%, LTCG {a['ltcg_rate']}%, NIIT {a['niit']}%, State {a['state_rate']}%\n"
        f"Acct: Tax-Deferred {a['tax_deferred']}%, Tax-Exempt {a['tax_exempt']}%"
    )

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_markdown(export_dir: str, filename: str, text: str) -> str:
    ensure_dir(export_dir)
    fp = os.path.join(export_dir, filename)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(text)
    return fp

def ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")
