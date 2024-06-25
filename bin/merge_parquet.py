#!/bin/env python

import argparse
from pathlib import Path

import pyarrow.parquet as pq


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("tables", nargs="+", type=Path, help="Audio dir")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("merged.parquet"),
        help="Output",
    )
    return parser.parse_args()


def merge_parquets(tables: list[Path], output: Path):
    if not tables:
        raise ValueError("No tables provided")

    schema = pq.ParquetFile(tables[0]).schema_arrow
    with pq.ParquetWriter(output, schema=schema) as writer:
        for table in tables:
            writer.write_table(pq.read_table(table, schema=schema))


def main():
    args = parse_args()
    merge_parquets(args.tables, args.output)


if __name__ == "__main__":
    main()
