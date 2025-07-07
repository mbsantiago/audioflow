params.ssh = true

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

    path 'batdetect2_features.parquet', emit: batdetect2_features
    path 'batdetect2_detections.parquet', emit: batdetect2_detections

    path 'birdnet_features.parquet', emit: birdnet_features
    path 'birdnet_detections.parquet', emit: birdnet_detections

    shell:
    '''
    echo "Downloading files from !{host}:!{base_dir}"
    echo "Using file list: !{file_list}"

    condition=!{params.ssh ? 1 : 0}
    echo $condition

    if [ $condition == 1 ]; then
        rsync -e "ssh" -azv --files-from=!{file_list} "!{host}:!{base_dir}" downloads/
    else
        rsync -azv --files-from=!{file_list} "!{base_dir}" downloads/
    fi

    parse_metadata.py --directory downloads/ --output metadata.csv

    process_audio_batdetect2.py \
        --directory downloads/ \
        --features-output batdetect2_features.parquet \
        --detections-output batdetect2_detections.parquet \
        --threshold !{threshold} \
        --recursive

    extract_features_and_detections.py \
        --directory downloads/ \
        --features-output birdnet_features.parquet \
        --detections-output birdnet_detections.parquet \
        --threshold !{threshold} \
        --model birdnet

    rm -rf downloads/
    '''
}
