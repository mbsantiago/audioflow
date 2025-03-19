#!/bin/env python

import argparse
import logging
from pathlib import Path

import pandas as pd
from soundevent import data
from audioclass.models.base import ClipClassificationModel
from audioclass.batch.base import BaseIterator


def load_model(model: str) -> ClipClassificationModel:
    if model == "perch":
        from audioclass.models.perch import Perch

        return Perch.load()

    if model == "birdnet":
        from audioclass.models.birdnet import BirdNET

        return BirdNET.load()

    if model == "birdnet_analyzer":
        from audioclass.models.birdnet_analyzer import BirdNETAnalyzer

        return BirdNETAnalyzer.load()

    raise ValueError(f"Unknown model {model}")


def get_iterator(
    model: ClipClassificationModel,
    directory: Path,
    iterator: str = "tensorflow",
    batch_size: int = 32,
) -> BaseIterator:
    if iterator == "tensorflow":
        from audioclass.batch.tensorflow import TFDatasetIterator

        return TFDatasetIterator.from_directory(
            directory,
            samplerate=model.samplerate,
            input_samples=model.input_samples,
            batch_size=batch_size,
        )

    if iterator == "simple":
        from audioclass.batch.simple import SimpleIterator

        return SimpleIterator.from_directory(
            directory,
            samplerate=model.samplerate,
            input_samples=model.input_samples,
            batch_size=batch_size,
        )

    raise ValueError(f"Unknown iterator {iterator}")


def save_features(
    predictions: list[data.ClipPrediction],
    output: Path,
) -> None:
    pd.DataFrame(
        [
            {
                "path": str(prediction.clip.recording.path),
                "start_time": prediction.clip.start_time,
                "end_time": prediction.clip.end_time,
                **{feat.name: feat.value for feat in prediction.features},
            }
            for prediction in predictions
        ]
    ).to_parquet(output, index=False)


def save_detections(
    predictions: list[data.ClipPrediction],
    output: Path,
    threshold: float = 0.1,
) -> None:
    pd.DataFrame(
        [
            {
                "path": str(prediction.clip.recording.path),
                "start_time": prediction.clip.start_time,
                "end_time": prediction.clip.end_time,
                "species": tag.tag.value,
                "score": tag.score,
            }
            for prediction in predictions
            for tag in prediction.tags
            if tag.score >= threshold
        ]
    ).to_parquet(output, index=False)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, help="Audio dir")
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
        "--model",
        type=str,
        default="birdnet_analyzer",
        help="Model to use",
        choices=["birdnet", "birdnet_analyzer", "perch"],
    )
    parser.add_argument(
        "--iterator",
        type=str,
        help="Iterator to use",
        default="tensorflow",
        choices=["tensorflow", "simple"],
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        help="Batch size",
        default=32,
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Detection threshold",
        default=0.1,
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    model = load_model(args.model)
    iterator = get_iterator(
        model,
        args.directory,
        iterator=args.iterator,
        batch_size=args.batch_size,
    )
    output = model.process_iterable(iterator)
    save_features(output, args.features_output)
    save_detections(output, args.detections_output, threshold=args.threshold)


if __name__ == "__main__":
    main()
