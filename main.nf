params.chunk_size = 200
params.file_list = 'example_files.txt'
params.audio_dir = '/home/user/audio/'
params.data_host = 'username@hostname'

include { merge_csv } from './modules/local/merge_csv'
include { merge_parquet as merge_detections; merge_parquet as merge_features } from './modules/local/merge_parquet'
include { split_file } from './modules/local/split_file'

include { process_audio_files } from './workflows/process_audio_files'

nextflow.preview.output = true

workflow {
    main:
    file = channel.fromPath(params.file_list)

    file_chunks = split_file(file, params.chunk_size) | flatten

    process_audio_files(file_chunks)

    metadata_files = process_audio_files.out.metadata.collect()
    feature_files = process_audio_files.out.features.collect()
    detection_files = process_audio_files.out.detections.collect()

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
    directory 'results'
    mode 'copy'
}
