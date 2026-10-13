"""Validate experiment/ground-truth.yaml against the catalogue rules (task E03-03).

Checks the schema of every entry and the acceptance criteria of the catalogue:
  1. at least 15 entries in at least 5 groups,
  2. every entry has a CWE and an expected detector (empty only when out of tool reach),
  3. some entries are deliberately out of tool reach.

Usage: python experiment/scripts/validate_ground_truth.py [path]
Requires PyYAML.
"""

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "ground-truth.yaml"

REQUIRED_FIELDS = {
    "id", "tytul", "grupa", "cwe", "owasp_top10_2025", "owasp_cicd", "asvs",
    "lokalizacja", "wprowadzenie", "w_zasiegu_narzedzi", "pewnosc_detekcji",
    "oczekiwany_detektor", "najwczesniejszy_etap", "uzasadnienie",
}
GROUPS = {"kod", "zaleznosci", "kontener", "iac", "konfiguracja-web", "workflow"}
STAGES = {"PR", "main-przed-wdrozeniem", "po-uruchomieniu", "brak"}
CONFIDENCE = {"wysoka", "srednia", "niska", "brak"}
TOP10 = {f"A{i:02d}" for i in range(1, 11)}
CICD = {f"CICD-SEC-{i}" for i in range(1, 11)}

MIN_ENTRIES = 15
MIN_GROUPS = 5


def check_entry(e, errors):
    gid = e.get("id", "?")
    missing = REQUIRED_FIELDS - e.keys()
    if missing:
        errors.append(f"{gid}: missing fields {sorted(missing)}")
        return
    if not re.fullmatch(r"GT-\d{2}", gid):
        errors.append(f"{gid}: id must match GT-NN")
    if not re.fullmatch(r"CWE-\d+", str(e["cwe"])):
        errors.append(f"{gid}: invalid cwe {e['cwe']!r}")
    if e["grupa"] not in GROUPS:
        errors.append(f"{gid}: unknown group {e['grupa']!r}")
    if e["owasp_top10_2025"] is not None and e["owasp_top10_2025"] not in TOP10:
        errors.append(f"{gid}: invalid owasp_top10_2025 {e['owasp_top10_2025']!r}")
    if e["owasp_cicd"] is not None and e["owasp_cicd"] not in CICD:
        errors.append(f"{gid}: invalid owasp_cicd {e['owasp_cicd']!r}")
    if e["asvs"] is not None and not re.fullmatch(r"v5\.0\.0-\d+\.\d+\.\d+", str(e["asvs"])):
        errors.append(f"{gid}: asvs must look like v5.0.0-N.N.N")
    if e["najwczesniejszy_etap"] not in STAGES:
        errors.append(f"{gid}: unknown stage {e['najwczesniejszy_etap']!r}")
    if e["pewnosc_detekcji"] not in CONFIDENCE:
        errors.append(f"{gid}: unknown confidence {e['pewnosc_detekcji']!r}")

    detectors = e["oczekiwany_detektor"] or []
    for d in detectors:
        if not isinstance(d, dict) or not d.get("klasa") or not d.get("narzedzie"):
            errors.append(f"{gid}: detector needs klasa and narzedzie: {d!r}")
    in_reach = e["w_zasiegu_narzedzi"]
    if in_reach is True:
        if not detectors:
            errors.append(f"{gid}: in tool reach but no expected detector")
        if e["najwczesniejszy_etap"] == "brak" or e["pewnosc_detekcji"] == "brak":
            errors.append(f"{gid}: in tool reach but stage/confidence is 'brak'")
    elif in_reach is False:
        if detectors:
            errors.append(f"{gid}: out of tool reach but has detectors")
        if e["najwczesniejszy_etap"] != "brak" or e["pewnosc_detekcji"] != "brak":
            errors.append(f"{gid}: out of tool reach must have stage and confidence 'brak'")
    else:
        errors.append(f"{gid}: w_zasiegu_narzedzi must be true or false")


def main(path):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    entries = data.get("pozycje") or []
    errors = []

    ids = [e.get("id") for e in entries]
    for gid, n in Counter(ids).items():
        if n > 1:
            errors.append(f"{gid}: duplicate id")
    for e in entries:
        check_entry(e, errors)

    groups = Counter(e.get("grupa") for e in entries)
    out_of_reach = [e["id"] for e in entries if e.get("w_zasiegu_narzedzi") is False]
    dast_only = [
        e["id"] for e in entries
        if e.get("oczekiwany_detektor")
        and all(d.get("klasa") == "DAST" for d in e["oczekiwany_detektor"])
    ]
    top10 = sorted({e["owasp_top10_2025"] for e in entries if e.get("owasp_top10_2025")})

    criteria = [
        (f"min. {MIN_ENTRIES} entries in min. {MIN_GROUPS} groups",
         len(entries) >= MIN_ENTRIES and len(groups) >= MIN_GROUPS),
        ("every entry has a CWE and an expected detector (or is out of reach)",
         not any("cwe" in m or "detector" in m or "missing" in m for m in errors)),
        ("some entries deliberately out of tool reach", len(out_of_reach) > 0),
    ]

    n = len(entries)
    print(f"entries: {n}, groups: {len(groups)} {dict(groups)}")
    print(f"Top 10:2025 categories covered: {len(top10)}/10 {top10}")
    print(f"out of tool reach: {len(out_of_reach)} {out_of_reach}")
    print(f"DAST-only: {len(dast_only)} {dast_only}")
    if n:
        print(f"H1 ceiling (all in-reach entries stopped): {(n - len(out_of_reach)) / n:.0%}")
        print(f"H1 ceiling if DAST-only entries are not stopped: "
              f"{(n - len(out_of_reach) - len(dast_only)) / n:.0%}")
    for name, ok in criteria:
        print(f"[{'x' if ok else ' '}] {name}")
    for m in errors:
        print(f"ERROR {m}")
    return 0 if not errors and all(ok for _, ok in criteria) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH))
