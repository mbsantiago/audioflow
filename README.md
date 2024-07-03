# Audio Pipelines for Environmental Analysis

This repository provides standardized data processing pipelines to streamline the analysis of large-scale environmental audio recordings. Whether you're tackling a massive dataset or need individual processing components for a custom workflow, we've got you covered.

**Key Components:**

- **Data Transfer:** Efficiently copy recordings from remote servers.
- **Metadata Extraction:** Automatically gather essential information from your audio files.
- **ML-Powered Analysis:** Employ powerful machine learning models to extract audio features and detections.

## Getting Started

### Prerequisites

- **Conda:** For creating isolated environments to run ML models (we recommend installing with [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)).
- **Nextflow:** For managing the pipeline's workflow and execution (see [installation instructions](https://www.nextflow.io/docs/latest/install.html)).

### Running the Pipeline

To process all audio data on a remote server, simply provide a list of file paths:

```bash
nextflow run . --file_list <file_with_list_of_recordings> --chunk_size 200 --audio_dir <base_audio_dir> --data_host <hostname_of_server_with_data> --model "birdnet_analyzer" --batch_size 64 --threshold 0.1
```

**Explanation:**

- `file_list`: Path to your text file containing the list of recordings.
- `chunk_size`: Number of files to process at once (adjust for your system).
- `audio_dir`: Base directory where the audio files are located on the server.
- `data_host`: Hostname of the server containing your audio data.
- `model`: The ML model to use for analysis (e.g., "birdnet_analyzer").
- `batch_size`: Batch size for ML model inference.
- `threshold`: Confidence threshold for detections.

## Nextflow Advantages

Leveraging Nextflow brings a host of benefits:

- **Parallel Processing:** Speed up analysis by handling multiple files concurrently.
- **Resilience:** Automatically resume from where you left off if the pipeline is interrupted.
- **Flexibility:** Run on various platforms (local, cloud, HPC clusters, etc.).
- **Insightful Reporting:** Get detailed logs and reports for troubleshooting and optimization.
