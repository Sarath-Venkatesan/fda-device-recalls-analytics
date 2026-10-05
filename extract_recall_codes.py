"""
Stream the openFDA device recall bulk file and extract a slim lookup:
recall_number -> product_code, root_cause.
Reads straight from the zip; never loads the full >1 GB JSON into memory.
"""
import csv
import zipfile
from pathlib import Path

import ijson

RAW = Path(r"C:\fda-recalls\data\raw")
OUT = Path(r"C:\fda-recalls\data\processed")
OUT.mkdir(parents=True, exist_ok=True)

zip_path = next(RAW.glob("device-recall-*.json.zip"))
out_path = OUT / "recall_product_codes.csv"

rows, seen, dupes = 0, set(), 0
with zipfile.ZipFile(zip_path) as z:
    with z.open(z.namelist()[0]) as f, open(out_path, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["recall_number", "product_code", "root_cause"])
        for rec in ijson.items(f, "results.item"):
            rn = rec.get("product_res_number")
            code = (rec.get("product_code") or "").replace("-", "").strip().upper()
            w.writerow([rn, code, rec.get("root_cause_description")])
            rows += 1
            if rn in seen:
                dupes += 1
            seen.add(rn)

print(f"Source: {zip_path.name}")
print(f"Rows written: {rows}")
print(f"Duplicate recall numbers: {dupes}")
print(f"Output: {out_path}")