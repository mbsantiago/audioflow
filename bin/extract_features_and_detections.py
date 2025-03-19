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

    if model == "batdetect2": 
        from batdetect2.cli import detect
        
        return detect()

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
    model_name: str = "",
) -> None:
    features_data = []
    
    for prediction in predictions:
        # Create base record with common fields
        base_record = {
            "path": str(prediction.clip.recording.path),
            "start_time": prediction.clip.start_time,
            "end_time": prediction.clip.end_time,
        }
        
        # Add features
        feature_dict = {feat.name: feat.value for feat in prediction.features}
        
        # For batdetect2, extract additional fields if available
        if model_name == "batdetect2" and hasattr(prediction.clip, "metadata"):
            if "low_freq" in prediction.clip.metadata:
                base_record["low_freq"] = prediction.clip.metadata["low_freq"]
            if "high_freq" in prediction.clip.metadata:
                base_record["high_freq"] = prediction.clip.metadata["high_freq"]
        
        # Combine base record with features
        record = {**base_record, **feature_dict}
        features_data.append(record)
    
    pd.DataFrame(features_data).to_parquet(output, index=False)


def save_detections(
    predictions: list[data.ClipPrediction],
    output: Path,
    threshold: float = 0.1,
    model_name: str = "",
) -> None:
    detections_data = []
    
    for prediction in predictions:
        # Create base record with common fields
        base_path = str(prediction.clip.recording.path)
        base_start = prediction.clip.start_time
        base_end = prediction.clip.end_time
        
        # For batdetect2, handle multiple detections per prediction
        if model_name == "batdetect2" and hasattr(prediction, "detections"):
            for detection in prediction.detections:
                record = {
                    "path": base_path,
                    "start_time": detection.get("start_time", base_start),
                    "end_time": detection.get("end_time", base_end),
                    "species": detection.get("class", "unknown"),
                    "score": detection.get("det_prob", 0.0),
                    "logit": detection.get("det_prob", 0.0),  # Same as score for compatibility
                    "low_freq": detection.get("low_freq", None),
                    "high_freq": detection.get("high_freq", None),
                }
                if record["score"] >= threshold:
                    detections_data.append(record)
        else:
            # Handle standard tag-based predictions from other models
            for tag in prediction.tags:
                if tag.score >= threshold:
                    record = {
                        "path": base_path,
                        "start_time": base_start,
                        "end_time": base_end,
                        "species": tag.tag.value,
                        "score": tag.score,
                        "logit": tag.score,  # Same as score for compatibility
                    }
                    
                    # Add low_freq and high_freq if available in clip metadata
                    if hasattr(prediction.clip, "metadata"):
                        if "low_freq" in prediction.clip.metadata:
                            record["low_freq"] = prediction.clip.metadata["low_freq"]
                        if "high_freq" in prediction.clip.metadata:
                            record["high_freq"] = prediction.clip.metadata["high_freq"]
                    
                    detections_data.append(record)
    
    pd.DataFrame(detections_data).to_parquet(output, index=False)


def extract_batdetect2_features(
    predictions: list[data.ClipPrediction],
    output: Path,
) -> None:
    """Extract feature embeddings for batdetect2 detections."""
    embeddings = []
    
    for prediction in predictions:
        base_path = str(prediction.clip.recording.path)
        
        # Check if this prediction has features and detections
        if hasattr(prediction, "detections") and hasattr(prediction, "features_array"):
            detections = prediction.detections
            features = prediction.features_array
            
            # Process each detection with its corresponding feature
            for i, detection in enumerate(detections):
                result = {
                    'filename': base_path,
                    'species': detection.get('class', 'unknown'),
                    'logit': detection.get('det_prob', 0.0),
                    'start_time': detection.get('start_time', prediction.clip.start_time),
                    'end_time': detection.get('end_time', prediction.clip.end_time),
                    'low_freq': detection.get('low_freq', None),
                    'high_freq': detection.get('high_freq', None),
                }
                
                # Extract the features for this detection
                if features is not None and features.shape[0] > i:
                    feature_row = features[i]
                    # Add features as numbered columns
                    for j, feature_value in enumerate(feature_row):
                        result[f'feature_{j}'] = feature_value
                
                embeddings.append(result)
    
    # Save as parquet
    if embeddings:
        pd.DataFrame(embeddings).to_parquet(output, index=False)


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
        "--embeddings-output",
        type=Path,
        default=Path("embeddings.parquet"),
        help="Feature embeddings output (for batdetect2)",
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
    model = load_model(args.model)
    iterator = get_iterator(
        model,
        args.directory,
        iterator=args.iterator,
        batch_size=args.batch_size,
    )
    
    # Process audio files
    logging.info(f"Processing audio files using {args.model}...")
    output = model.process_iterable(iterator)
    
    # Save outputs
    logging.info(f"Saving features to {args.features_output}")
    save_features(output, args.features_output, model_name=args.model)
    
    logging.info(f"Saving detections to {args.detections_output}")
    save_detections(output, args.detections_output, threshold=args.threshold, model_name=args.model)
    
    # Extract and save embeddings for batdetect2
    if args.model == "batdetect2":
        logging.info(f"Saving feature embeddings to {args.embeddings_output}")
        extract_batdetect2_features(output, args.embeddings_output)
        
    logging.info("Processing complete!")


if __name__ == "__main__":
    main()
