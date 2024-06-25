#!/usr/bin/env python

import argparse
import os


def clean_file(path: str):
    if os.path.islink(path):
        path = os.readlink(path)

    if not os.path.exists(path):
        return

    open(path, "wb").close()


def clean_directory(path: str):
    if not os.path.isdir(path):
        return

    for root, _, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)

            clean_file(path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Directory to clean")
    return parser.parse_args()


def main():
    args = parse_args()
    clean_directory(args.directory)


if __name__ == "__main__":
    main()
