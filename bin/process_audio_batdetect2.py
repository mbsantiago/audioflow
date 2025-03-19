#!/usr/bin/env python3

import os
import argparse
import logging
import uuid
from pathlib import Path

import pandas as pd
import numpy as np
from batdetect2.cli import api


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, help="Audio dir")
    parser.add_argument"--features-output",
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
        default=".WAV", 
        help="File type",
    )
    return parser.parse_args()


def find_audio_files(directory, extensions, recursive=True):
    audio_files = []
    extensions_list = extensions.split(",")
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions_list):
                    audio_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if any(file.endswith(ext) for ext in extensions_list):
                audio_files.append(os.path.join(directory, file))
    
    return audio_files

def process_audio_files(audio_files, threshold, max_duration=None):
    config = api.get_config(
        detection_threshold=threshold,
        time_expansion_factor=1,
        max_duration=max_duration,
    )
    
    all_detections = []
    all_features = []
    
    for i, audio_file in enumerate(audio_files):
        try:
            audio = api.load_audio(audio_file, max_duration=max_duration)
            spec = api.generate_spectrogram(audio, config=config)
            detections, features = api.process_spectrogram(spec, config=config)
            
            filtered_detections = [d for d in detections if d['det_prob'] >= threshold]
            
            for i, detection in enumerate(filtered_detections):
                detection_id = str(uuid.uuid4())
                
                detection_record = {
                    'id': detection_id,
                    'file_path': audio_file,
                    'file_name': os.path.basename(audio_file),
                    'start_time': detection['start_time'],
                    'end_time': detection['end_time'],
                    'low_freq': detection['low_freq'],
                    'high_freq': detection['high_freq'],
                    'species': detection['class'],
                    'detection_score': detection['det_prob'],
                    'classification_score': detection.get('class_prob', None)
                }
                all_detections.append(detection_record)
                
                if features is not None and features.shape[0] > i:
                    feature_row = features[i]
                    feature_record = {'id': detection_id}
                    
                    for j, feature_value in enumerate(feature_row):
                        feature_record[f'feature_{j}'] = feature_value
                    
                    all_features.append(feature_record)
        
        except Exception as e:
            pass
    
    detections_df = pd.DataFrame(all_detections)
    features_df = pd.DataFrame(all_features)
    
    return detections_df, features_df

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    args = parse_args()
    audio_files = find_audio_files(
        args.directory, 
        args.file_extensions,
        recursive=args.recursive
    )
    
    if not audio_files:
        return
    
    detections_df, features_df = process_audio_files(
        audio_files, 
        args.threshold,
        max_duration=args.max_duration
    )
    
        detections_df.to_parquet(args.detections_output, index=False)
        features_df.to_parquet(args.features_output, index=False)

if __name__ == "__main__":
    main()
