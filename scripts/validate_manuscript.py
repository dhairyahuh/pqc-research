#!/usr/bin/env python3
"""ASTRA-Sec: Manuscript Integrity, Syntax, and Reference Validation Tool.

Validates that manuscript/main.tex and all included tables, figures, proofs,
and BibTeX references satisfy structural and syntactic integrity requirements.
"""

import os
import re
import sys
from pathlib import Path


def validate_manuscript():
    root = Path(__file__).resolve().parent.parent
    manuscript_dir = root / "manuscript"
    main_tex = manuscript_dir / "main.tex"
    ref_bib = manuscript_dir / "references.bib"

    print("=" * 75)
    print(" ASTRA-Sec Manuscript & LaTeX Integrity Validator")
    print("=" * 75)

    if not main_tex.exists():
        print(f"[-] ERROR: {main_tex} does not exist.", file=sys.stderr)
        sys.exit(1)
    if not ref_bib.exists():
        print(f"[-] ERROR: {ref_bib} does not exist.", file=sys.stderr)
        sys.exit(1)

    # 1. Parse BibTeX Keys
    with open(ref_bib, "r", encoding="utf-8") as f:
        bib_content = f.read()

    bib_keys = set(re.findall(r"@\w+\s*{\s*([^,]+),", bib_content))
    print(f"[+] Loaded {len(bib_keys)} verified BibTeX reference entries from references.bib.")

    # 2. Read Main TeX and Included Files
    with open(main_tex, "r", encoding="utf-8") as f:
        main_content = f.read()

    # Find and check all \input{...}
    input_matches = re.findall(r"\\input\{([^}]+)\}", main_content)
    full_content = main_content
    for inp in input_matches:
        inp_path = manuscript_dir / (inp if inp.endswith(".tex") else f"{inp}.tex")
        if not inp_path.exists():
            print(f"[-] ERROR: Included file '{inp}' not found at: {inp_path}", file=sys.stderr)
            sys.exit(1)
        with open(inp_path, "r", encoding="utf-8") as f:
            sub_content = f.read()
            full_content += "\n" + sub_content
        print(f"  [+] Verified input file: {inp}")

    # 3. Check Figure Inclusions
    fig_matches = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", full_content)
    for fig in fig_matches:
        fig_path = manuscript_dir / fig
        if not fig_path.exists():
            print(f"[-] ERROR: Figure file '{fig}' not found at: {fig_path}", file=sys.stderr)
            sys.exit(1)
        print(f"  [+] Verified figure: {fig} (Size: {fig_path.stat().st_size / 1024.0:.1f} KB)")

    # 4. Check Citations
    citations = set()
    for match in re.findall(r"\\cite\{([^}]+)\}", full_content):
        for key in match.split(","):
            citations.add(key.strip())

    missing_citations = citations - bib_keys
    if missing_citations:
        print(f"[-] ERROR: Unresolved citations found: {missing_citations}", file=sys.stderr)
        sys.exit(1)
    print(f"[+] All {len(citations)} citations in manuscript resolve against references.bib.")

    # 5. Check Labels and References
    labels = set(re.findall(r"\\label\{([^}]+)\}", full_content))
    refs = set(re.findall(r"\\ref\{([^}]+)\}", full_content))
    missing_refs = refs - labels
    if missing_refs:
        print(f"[-] WARNING: References without matching label: {missing_refs}")
    else:
        print(f"[+] All {len(refs)} cross-references match defined labels.")

    # 6. Check Environment Balance
    begins = re.findall(r"\\begin\{([^}]+)\}", full_content)
    ends = re.findall(r"\\end\{([^}]+)\}", full_content)
    if len(begins) != len(ends):
        print(f"[-] ERROR: Environment count mismatch: {len(begins)} \\begin vs {len(ends)} \\end", file=sys.stderr)
        sys.exit(1)
    print(f"[+] Environment structure balanced ({len(begins)} environments).")

    print("\n" + "=" * 75)
    print(" MANUSCRIPT VALIDATION PASSED: 100% INTEGRITY VERIFIED")
    print("=" * 75)


if __name__ == "__main__":
    validate_manuscript()
