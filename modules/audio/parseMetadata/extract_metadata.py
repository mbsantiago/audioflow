#!/bin/env python

import argparse
from pathlib import Path

import pandas as pd
from metamoth import parse_metadata
from multiprocessing import Pool


def get_audio_files(path: Path) -> list[Path]:
    return path.glob("*.[wW][aA][vV]")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, help="Audio dir")
    parser.add_argument("--ouptut", type=Path, help="Output")
    return parser.parse_args()


def main():
    args = parse_args()

