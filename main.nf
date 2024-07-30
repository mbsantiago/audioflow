params.chunk_size = 200
params.file_list = 'example_files.txt'
params.audio_dir = '/home/user/audio/'
params.data_host = 'username@hostname'
params.model = 'birdnet_analyzer'
params.iterator = 'tensorflow'
params.batch_size = 32
params.threshold = 0.1

include { merge_csv } from './modules/local/merge_csv'
include { merge_parquet as merge_detections; merge_parquet as merge_features } from './modules/local/merge_parquet'
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
        params.model,
        params.iterator,
        params.batch_size,
        params.threshold,
    )

    metadata_files = process_file_list.out.metadata.collect()
    feature_files = process_file_list.out.features.collect()
    detection_files = process_file_list.out.detections.collect()

    metadata = merge_csv(metadata_files)
    features = merge_features(feature_files)
    detections = merge_detections(detection_files)

    emit:
    metadata
    features
    detections

    publish:
    metadata >> 'metadata'
    features >> 'features'
    detections >> 'detections'
}

output {
    directory params.resultsDir
    mode 'copy'
}
