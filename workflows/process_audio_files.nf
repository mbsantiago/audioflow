params.audio_dir = '/mnt/gpfs/live/ritd-ag-project-rd00lk-kejon62/'
params.data_host = 'rdss'

include { copy_files } from '../modules/local/copy_files'
include { parse_metadata } from '../modules/local/parse_metadata'
include { extract_features } from '../modules/local/extract_features'
include { clean_files } from '../modules/local/clean_files'

workflow process_audio_files {
    take:
    file_list

    main:
    audio_files = copy_files(
        file_list,
        params.data_host,
        params.audio_dir
    )
    parse_metadata(audio_files)
    extract_features(audio_files)
    clean_files(
        audio_files,
        parse_metadata.out.is_ready,
        extract_features.out.is_ready,
    )

    emit:
    metadata = parse_metadata.out.metadata
    features = extract_features.out.features
}
