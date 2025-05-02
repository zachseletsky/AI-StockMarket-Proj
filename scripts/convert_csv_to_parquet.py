"""
  convert_csv_to_parquet.py  (run as nightly job)
  for the future when data files become to large to store
  in csv format
"""
from pathlib import Path
import pyarrow.csv as pv
import pyarrow.parquet as pq

for csv_file in Path("data-lake/raw").rglob("*.csv"):
    tbl = pv.read_csv(
        csv_file,
        convert_options=pv.ConvertOptions(timestamp_parsers=["%Y-%m-%d %H:%M:%S"]),
    )
    pq_path = Path("data-lake/processed") / csv_file.relative_to("data-lake/raw")
    pq_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(tbl, pq_path.with_suffix(".parquet"), compression="zstd")
