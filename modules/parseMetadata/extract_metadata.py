#!/bin/env python

import argparse
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

import soundfile as sf
import pandas as pd
from metamoth import parse_metadata
from metamoth.metadata import AMMetadata, ExtraMetadata
from metamoth.mediainfo import MediaInfo
from multiprocessing import Pool


@dataclass
class Metadata(MediaInfo, ExtraMetadata):
    """Metadata for non-AudioMoth recordings."""


def get_non_audiomoth_metadata(path: Path) -> Metadata:
    with sf.SoundFile(path) as f:
        samples = int(f.frames)
        return Metadata(
            path=str(path),
            samplerate_hz=f.samplerate,
            duration_s=samples / f.samplerate,
            samples=samples,
            channels=f.channels,
            firmware_version="N/A",
        )


def get_audio_files(path: Path) -> list[Path]:
    return list(path.glob("**/*.[wW][aA][vV]"))


def get_metadata(path: Path) -> Metadata | AMMetadata | None:
    try:
        metadata = parse_metadata(path)
        return metadata
    except ValueError:
        return get_non_audiomoth_metadata(path)
    except Exception as e:
        logging.error("Error processing %s, Error: %s", path, e)
        print(e)
        return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, help="Audio dir")
    parser.add_argument("--output", type=Path, help="Output")
    parser.add_argument(
        "--nprocs",
        type=int,
        help="Number of processes",
        default=2,
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    files = get_audio_files(args.directory)

    with Pool(args.nprocs) as p:
        metadata = [m for m in p.map(get_metadata, files) if m is not None]

    df = pd.DataFrame([asdict(m) for m in metadata])
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
