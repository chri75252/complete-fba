import pathlib
import re

input_path = pathlib.Path(r"RESERACH/REPORT/part 8 jan/OC/PHASEA_MANUAL_REPORT_20260129.md")
output_path = pathlib.Path(
    r"RESERACH/REPORT/part 8 jan/OC/PHASEA_MANUAL_REPORT_20260129_REVIEWED.md"
)

lines = input_path.read_text(encoding="utf-8", errors="replace").splitlines()

sections = {
    "HEADER": [],
    "VERIFIED_REC": [],
    "VERIFIED_AO": [],
    "HL_REC": [],
    "HL_AO": [],
    "NV": [],
    "FOOTER": [],
}
current_section = "HEADER"
corrections_log = []

SEC_HEADERS = {
    "## VERIFIED - RECOMMENDED": "VERIFIED_REC",
    "## VERIFIED - AUDITED OUT": "VERIFIED_AO",
    "## HIGHLY LIKELY - RECOMMENDED": "HL_REC",
    "## HIGHLY LIKELY - AUDITED OUT": "HL_AO",
    "## NEEDS VERIFICATION": "NV",
    "## Reconciliation": "FOOTER",
}

for line in lines:
    stripped = line.strip()
    for header, key in SEC_HEADERS.items():
        if stripped.startswith(header):
            current_section = key
            break

    sections[current_section].append(line)


def parse_row(line):
    if not line.strip().startswith("|"):
        return None
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(parts) < 10:
        return None
    return {
        "line": line,
        "asin": parts[6],
        "verdict": parts[0],
        "supplier_title": parts[2],
        "pack_verdict": parts[12] if len(parts) > 12 else "",
        "evidence": parts[14] if len(parts) > 14 else "",
        "parts": parts,
    }


moved_to_nv = []
removed_to_unrelated = []

verified_moves_to_nv = [
    "B07WDRQ4J7",
    "B0CCJS5GKB",
    "B098P62161",
    "B07HJ6V448",
    "B074V9468X",
    "B07YPPK4JY",
    "B00LZRJTEA",
    "B01APK7CDC",
]
verified_edits_unknown = ["B0DJDH23JW", "B007IGLUIK", "B009SJXB32", "B00W3RVAG6"]
verified_ao_move_to_nv = ["B0DT71SSPT"]

new_verified_rec = []
for line in sections["VERIFIED_REC"]:
    row = parse_row(line)
    if not row:
        new_verified_rec.append(line)
        continue

    if row["asin"] in verified_moves_to_nv:
        row["parts"][0] = "NEEDS_VERIFICATION"
        row["line"] = "| " + " | ".join(row["parts"]) + " |"
        moved_to_nv.append(row)
        corrections_log.append(
            f'- MOVE ASIN {row["asin"]} from VERIFIED to NEEDS_VERIFICATION (Manual Correction: Pack/Split issue)'
        )
    elif row["asin"] in verified_edits_unknown:
        row["parts"][12] = "1:1 Match"
        row["line"] = "| " + " | ".join(row["parts"]) + " |"
        new_verified_rec.append(row["line"])
        corrections_log.append(
            f'- EDIT ASIN {row["asin"]} Pack Verdict UNKNOWN -> 1:1 Match (Manual Correction)'
        )
    else:
        new_verified_rec.append(line)
sections["VERIFIED_REC"] = new_verified_rec

new_verified_ao = []
for line in sections["VERIFIED_AO"]:
    row = parse_row(line)
    if not row:
        new_verified_ao.append(line)
        continue

    if row["asin"] in verified_ao_move_to_nv:
        row["parts"][0] = "NEEDS_VERIFICATION"
        row["line"] = "| " + " | ".join(row["parts"]) + " |"
        moved_to_nv.append(row)
        corrections_log.append(
            f'- MOVE ASIN {row["asin"]} from VERIFIED-AUDITED_OUT to NEEDS_VERIFICATION (Manual Correction: Match dispute)'
        )
    else:
        new_verified_ao.append(line)
sections["VERIFIED_AO"] = new_verified_ao

new_hl_rec = []
for line in sections["HL_REC"]:
    row = parse_row(line)
    if not row:
        new_hl_rec.append(line)
        continue

    pack = row["pack_verdict"]
    evidence = row["evidence"]

    if "SPLIT CANDIDATE" in pack or pack == "UNKNOWN":
        row["parts"][0] = "NEEDS_VERIFICATION"
        row["line"] = "| " + " | ".join(row["parts"]) + " |"
        moved_to_nv.append(row)
        corrections_log.append(
            f'- MOVE ASIN {row["asin"]} from HL-REC to NEEDS_VERIFICATION (Rule: {pack})'
        )
    elif "BUNDLE" in pack and "Brand match:" not in evidence:
        row["parts"][0] = "NEEDS_VERIFICATION"
        row["line"] = "| " + " | ".join(row["parts"]) + " |"
        moved_to_nv.append(row)
        corrections_log.append(
            f'- MOVE ASIN {row["asin"]} from HL-REC to NEEDS_VERIFICATION (Rule: Bundle with generic evidence)'
        )
    else:
        new_hl_rec.append(line)
sections["HL_REC"] = new_hl_rec

new_hl_ao = []
for line in sections["HL_AO"]:
    row = parse_row(line)
    if not row:
        new_hl_ao.append(line)
        continue

    evidence = row["evidence"]
    if "Brand match:" not in evidence and "Shared anchors:" in evidence:
        removed_to_unrelated.append(row)
        corrections_log.append(
            f'- REMOVE ASIN {row["asin"]} from HL-AO to UNRELATED (Rule: Weak evidence)'
        )
    else:
        new_hl_ao.append(line)
sections["HL_AO"] = new_hl_ao

new_nv = []
existing_nv_rows = []
for line in sections["NV"]:
    row = parse_row(line)
    if not row:
        existing_nv_rows.append(line)
        continue

    evidence = row["evidence"]
    anchors_text = (
        evidence.split("Shared anchors:")[-1].strip() if "Shared anchors:" in evidence else ""
    )
    has_digit = any(c.isdigit() for c in anchors_text)

    if "Brand match:" not in evidence and "Shared anchors:" in evidence and not has_digit:
        removed_to_unrelated.append(row)
        corrections_log.append(
            f'- REMOVE ASIN {row["asin"]} from NV to UNRELATED (Rule: Generic anchors)'
        )
    else:
        existing_nv_rows.append(line)

final_nv_lines = []
header_lines = [
    l for l in existing_nv_rows if not l.strip().startswith("|") or "Verdict" in l or "---" in l
]
data_lines = [
    l
    for l in existing_nv_rows
    if l.strip().startswith("|") and "Verdict" not in l and "---" not in l
]

final_nv_lines.extend(header_lines)
final_nv_lines.extend(data_lines)

for row in moved_to_nv:
    final_nv_lines.append(row["line"])

sections["NV"] = final_nv_lines

count_verified_rec = sum(
    1
    for l in sections["VERIFIED_REC"]
    if l.strip().startswith("|") and "Verdict" not in l and "---" not in l
)
count_verified_ao = sum(
    1
    for l in sections["VERIFIED_AO"]
    if l.strip().startswith("|") and "Verdict" not in l and "---" not in l
)
count_hl_rec = sum(
    1
    for l in sections["HL_REC"]
    if l.strip().startswith("|") and "Verdict" not in l and "---" not in l
)
count_hl_ao = sum(
    1
    for l in sections["HL_AO"]
    if l.strip().startswith("|") and "Verdict" not in l and "---" not in l
)
count_nv = sum(
    1 for l in sections["NV"] if l.strip().startswith("|") and "Verdict" not in l and "---" not in l
)

removed_count = len(removed_to_unrelated)
original_unrelated = 2707
new_unrelated = original_unrelated + removed_count
total = (
    count_verified_rec + count_verified_ao + count_hl_rec + count_hl_ao + count_nv + new_unrelated
)

new_header = []
summary_start = False
for line in sections["HEADER"]:
    if "## Summary Counts" in line:
        summary_start = True
        new_header.append(line)
        continue

    if summary_start and line.strip().startswith("-"):
        if "VERIFIED - RECOMMENDED" in line:
            new_header.append(f"- VERIFIED - RECOMMENDED: {count_verified_rec}")
        elif "VERIFIED - AUDITED OUT" in line:
            new_header.append(f"- VERIFIED - AUDITED OUT: {count_verified_ao}")
        elif "HIGHLY LIKELY - RECOMMENDED" in line:
            new_header.append(f"- HIGHLY LIKELY - RECOMMENDED: {count_hl_rec}")
        elif "HIGHLY LIKELY - AUDITED OUT" in line:
            new_header.append(f"- HIGHLY LIKELY - AUDITED OUT: {count_hl_ao}")
        elif "NEEDS VERIFICATION" in line:
            new_header.append(f"- NEEDS VERIFICATION: {count_nv}")
        elif "UNRELATED" in line:
            new_header.append(f"- UNRELATED / NOT INCLUDED: {new_unrelated}")
        elif "TOTAL ANALYZED" in line:
            new_header.append(f"- **TOTAL ANALYZED: {total}**")
        else:
            new_header.append(line)
    else:
        new_header.append(line)

corrections_section = (
    [
        "",
        "## Corrections (Manual Review Mode)",
        "The following corrections were applied based on manual review rules:",
        "",
    ]
    + corrections_log
    + [""]
)


def update_section_header(lines, count):
    new_lines = []
    for l in lines:
        if l.strip().startswith("## ") and "count=" in l:
            base = l.split("(")[0]
            new_lines.append(f"{base}(count={count})")
        else:
            new_lines.append(l)
    return new_lines


sections["VERIFIED_REC"] = update_section_header(sections["VERIFIED_REC"], count_verified_rec)
sections["VERIFIED_AO"] = update_section_header(sections["VERIFIED_AO"], count_verified_ao)
sections["HL_REC"] = update_section_header(sections["HL_REC"], count_hl_rec)
sections["HL_AO"] = update_section_header(sections["HL_AO"], count_hl_ao)
sections["NV"] = update_section_header(sections["NV"], count_nv)

new_footer = []
for line in sections["FOOTER"]:
    if "VERIFIED(" in line:
        new_footer.append(
            f"- VERIFIED({count_verified_rec + count_verified_ao}) + HIGHLY_LIKELY({count_hl_rec + count_hl_ao}) + NEEDS VERIFICATION({count_nv}) + UNRELATED({new_unrelated}) = TOTAL({total})"
        )
    else:
        new_footer.append(line)

final_content = (
    new_header
    + corrections_section
    + sections["VERIFIED_REC"]
    + sections["VERIFIED_AO"]
    + sections["HL_REC"]
    + sections["HL_AO"]
    + sections["NV"]
    + new_footer
)

output_path.write_text("\n".join(final_content), encoding="utf-8")
print("Successfully generated reviewed report.")
print(
    f"New Counts: V-REC={count_verified_rec}, V-AO={count_verified_ao}, HL-REC={count_hl_rec}, HL-AO={count_hl_ao}, NV={count_nv}, UNRELATED={new_unrelated}"
)
print(f"Removed to Unrelated: {removed_count}")
