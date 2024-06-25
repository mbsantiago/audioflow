params.file_list = 'example_files.txt'
params.chunk_size = 3

include { merge_csv } from './modules/local/merge_csv'
include { merge_parquet } from './modules/local/merge_parquet'
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

    metadata = merge_csv(metadata_files)
    features = merge_parquet(feature_files)

    emit:
    metadata
    features

    publish:
    metadata >> 'metadata'
    features >> 'features'
}

output {
    directory 'results'
    mode 'copy'
}
