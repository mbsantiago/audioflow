#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.10"
# dependencies = [
#     "metamoth",
#     "pandas",
#     "numpy",
#     "soundfile",
# ]
# ///

import argparse
import logging
from dataclasses import asdict, dataclass
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from metamoth import parse_metadata
from metamoth.mediainfo import MediaInfo
from metamoth.metadata import AMMetadata, ExtraMetadata


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
        return None


@dataclass
class AcousticFeatures:
    max_amplitude: float


def get_acoustic_features(path: Path) -> AcousticFeatures | None:
    try:
        audio, _ = sf.read(path)
        return AcousticFeatures(max_amplitude=np.max(np.abs(audio)))
    except Exception as e:
        logging.error("Error processing %s, Error: %s", path, e)
        return None


def get_all_recording_data(path: Path) -> dict | None:
    metadata = get_metadata(path)

    if metadata is None:
        return None

    acoustic_features = get_acoustic_features(path)

    if acoustic_features is None:
        return {**asdict(metadata)}

    return {
        **asdict(metadata),
        **asdict(acoustic_features),
    }


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
        metadata = [m for m in p.map(get_all_recording_data, files) if m is not None]

    df = pd.DataFrame(metadata)
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
