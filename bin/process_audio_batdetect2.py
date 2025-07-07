#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.9"
# dependencies = [
#     "batdetect2",
#     "numpy",
#     "pandas",
#     "pyarrow",
# ]
# ///

import argparse
import logging
import os
import uuid
from pathlib import Path

import pandas as pd
from batdetect2 import api


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory",
        type=Path,
        help="Audio dir",
        required=True,
    )
    parser.add_argument(
        "--features-output",
        type=Path,
        default=Path("features.parquet"),
        help="Features output",
    )
    parser.add_argument(
        "--detections-output",
        type=Path,
        default=Path("detections.parquet"),
        help="Detections output",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Detection threshold",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively",
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=3,
        help="Maximum duration",
    )
    parser.add_argument(
        "--file-extensions",
        type=str,
        default="[wW][aA][vV]",
        help="File type",
    )
    return parser.parse_args()


def find_audio_files(directory: Path, extensions: str, recursive=True):
    if recursive:
        return list(Path(directory).glob(f"**/*.{extensions}"))

    return list(Path(directory).glob(f"*.{extensions}"))


def process_single_file(path: Path, config):
    outputs = api.process_file(path, config=config)

    detections = []
    features = []

    raw_dets = outputs["pred_dict"]["annotation"]

    if len(raw_dets) == 0:
        return detections, features

    for detection, feat in zip(
        raw_dets,
        outputs["cnn_feats"],
    ):
        detection_id = str(uuid.uuid4())
        detections.append(
            {
                "id": detection_id,
                "file_path": str(path),
                "file_name": os.path.basename(path),
                "start_time": detection["start_time"],
                "end_time": detection["end_time"],
                "low_freq": detection["low_freq"],
                "high_freq": detection["high_freq"],
                "species": detection["class"],
                "detection_score": detection["det_prob"],
                "classification_score": detection.get("class_prob", None),
            }
        )
        features.append(
            {
                "id": detection_id,
                **{f"feature_{j}": f for j, f in enumerate(feat)},
            }
        )

    return detections, features


def process_audio_files(audio_files, threshold):
    config = api.get_config(
        detection_threshold=threshold,
        time_expansion_factor=1,
        cnn_features=True,
    )

    all_detections = []
    all_features = []

    for audio_file in audio_files:
        try:
            detections, features = process_single_file(audio_file, config)
            all_detections.extend(detections)
            all_features.extend(features)

        except Exception as error:
            logging.error(
                f"Unknown error while processing file {audio_file}: {error}",
            )
            pass

    detections_df = pd.DataFrame(all_detections)
    features_df = pd.DataFrame(all_features)

    return detections_df, features_df


def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    args = parse_args()
    audio_files = find_audio_files(
        args.directory,
        args.file_extensions,
        recursive=args.recursive,
    )

    logging.info(f"Found {len(audio_files)} at {args.directory}")

    if not audio_files:
        return

    detections_df, features_df = process_audio_files(
        audio_files,
        args.threshold,
    )

    detections_df.to_parquet(args.detections_output, index=False)
    features_df.to_parquet(args.features_output, index=False)


if __name__ == "__main__":
    main()
