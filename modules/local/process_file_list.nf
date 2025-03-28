process process_file_list {
    label 'gpu'
    label 'network'

    input:
    path 'file_list'
    val host
    val base_dir
    val threshold

    output:
    path 'metadata.csv', emit: metadata
    path 'features.parquet', emit: features
    path 'detections.parquet', emit: detections

    shell:
    '''
    echo "Downloading files from !{host}:!{base_dir}"
    echo "Using file list: !{file_list}"

    rsync -e "ssh" -azv --files-from=!{file_list} "!{host}:!{base_dir}" downloads/

    parse_metadata.py --directory downloads/ --output metadata.csv

    extract_features_and_detections_batdetect2.py \
        --directory downloads/ \
        --features-output features.parquet \
        --detections-output detections.parquet \
        --threshold !{threshold}

    rm -rf downloads/
    '''
}
