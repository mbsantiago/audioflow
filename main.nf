params.chunk_size = 2
params.file_list = 'tests/data/audio_files.txt'
params.audio_dir = '$HOME/Software/workflows/audioflow/tests/data/audio'
params.data_host = 'localhost'
params.threshold = 0.5
params.ssh = false

include { merge_csv } from './modules/local/merge_csv'
include { 
    merge_parquet as merge_birdnet_detections;
    merge_parquet as merge_birdnet_features;
    merge_parquet as merge_batdetect2_detections;
    merge_parquet as merge_batdetect2_features;
} from './modules/local/merge_parquet'
include { split_file } from './modules/local/split_file'
include { process_file_list } from './modules/local/process_file_list'

nextflow.preview.output = true

workflow {
    main:
    file = channel.fromPath(params.file_list)

    file_chunks = split_file(file, params.chunk_size) | flatten

    process_file_list(
        file_chunks,
        params.data_host,
        params.audio_dir,
        params.threshold,
    )

    metadata_files = process_file_list.out.metadata.collect()

    birdnet_feature_files = process_file_list.out.birdnet_features.collect()
    birdnet_detection_files = process_file_list.out.birdnet_detections.collect()

    batdetect2_feature_files = process_file_list.out.batdetect2_features.collect()
    batdetect2_detection_files = process_file_list.out.batdetect2_detections.collect()

    metadata = merge_csv(metadata_files)

    birdnet_features = merge_birdnet_features(birdnet_feature_files)
    birdnet_detections = merge_birdnet_detections(birdnet_detection_files)

    batdetect2_features = merge_batdetect2_features(batdetect2_feature_files)
    batdetect2_detections = merge_batdetect2_detections(batdetect2_detection_files)

    emit:
    metadata
    birdnet_features
    birdnet_detections
    batdetect2_features
    batdetect2_detections

    publish:
    metadata = metadata
    birdnet_features = birdnet_features
    birdnet_detections = birdnet_detections
    batdetect2_features = batdetect2_features
    batdetect2_detections = batdetect2_detections
}

output {
    metadata {
        path "metadata"
        mode "copy"
    }
    birdnet_features {
        path "birdnet_features"
        mode "copy"
    }
    birdnet_detections {
        path "birdnet_detections"
        mode "copy"
    }
    batdetect2_features {
        path "batdetect2_features"
        mode "copy"
    }
    batdetect2_detections {
        path "batdetect2_detections"
        mode "copy"
    }
}
