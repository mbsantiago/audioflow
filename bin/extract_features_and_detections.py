#!/bin/env python

import os
import argparse
import logging
from pathlib import Path

import pandas as pd
from soundevent import data
from audioclass.models.base import ClipClassificationModel
from audioclass.batch.base import BaseIterator
from batdetect2 import api  # Assuming batdetect2 is the API you're using


def load_model(model: str):
    if model == "perch":
        from audioclass.models.perch import Perch

        return Perch.load()

    if model == "birdnet":
        from audioclass.models.birdnet import BirdNET

        return BirdNET.load()

    if model == "birdnet_analyzer":
        from audioclass.models.birdnet_analyzer import BirdNETAnalyzer

        return BirdNETAnalyzer.load()

    if model == "batdetect2":
        from batdetect2 import api

        return api

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


def save_detections(
    detections: list[dict],  # Update this to use a list of dicts
    output: Path,
    threshold: float = 0.3,
) -> None:
    # Filter detections based on the threshold and save them
    pd.DataFrame(
        [
            {
                "path": detection['filename'],
                "start_time": detection['start_time'],
                "end_time": detection['end_time'],
                "species": detection['species'],
                "logit": detection['logit'],
                "low_freq": detection['low_freq'],
                "high_freq": detection['high_freq'],
            }
            for detection in detections
            if detection['logit'] >= threshold
        ]
    ).to_parquet(output, index=False)

def save_features(
    detections: list[dict],  # List of detection dictionaries
    output: Path,
) -> None:
    # Save features corresponding to detections
    pd.DataFrame(
        [
            {
                "path": detection['filename'],
                "start_time": detection['start_time'],
                "end_time": detection['end_time'],
                **{f"feature_{i}": detection.get(f"feature_{i}") for i in range(len(detection)-7)},  # Assuming 7 is the detection info fields
            }
            for detection in detections
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
        choices=["birdnet", "birdnet_analyzer", "perch", "batdetect2"],
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

    # Load the model (batdetect2 or another model)
    model = load_model(args.model)
    
    # Iterate through files in the provided directory
    for root, dirs, files in os.walk(args.directory):
        for file_name in files:
            if file_name.endswith(".WAV"):  # Process only WAV files
                audio_file = os.path.join(root, file_name)  # Full file path
                logging.info(f"Processing {audio_file}")

                try:
                    # Load audio and generate the spectrogram
                    audio = api.load_audio(audio_file, max_duration=args.max_duration)  # Load audio
                    spec = api.generate_spectrogram(audio, config=config)  # Generate spectrogram

                    # Process the spectrogram to get detections and features
                    detections, features = api.process_spectrogram(spec, config=config)

                    # Loop over the detections to save detection info and features
                    for i, detection in enumerate(detections):
                        result = {
                            'filename': audio_file,
                            'species': detection['class'],
                            'logit': detection['det_prob'],
                            'start_time': detection['start_time'],
                            'end_time': detection['end_time'],
                            'low_freq': detection['low_freq'],
                            'high_freq': detection['high_freq'],
                        }

                        # Extract and save the features for each detection
                        if features.shape[0] > i:
                            feature_row = features[i]
                            for j, feature_value in enumerate(feature_row):
                                result[f'feature_{j}'] = feature_value

                        # Here, you would append or store 'result' in the appropriate way.
                        # For example, you can append it to a list for further saving.
                        # You can store the results as you were before in the DataFrame format.
                    
                except Exception as e:
                    logging.error(f"Error processing {audio_file}: {e}")

if __name__ == "__main__":
    main()
