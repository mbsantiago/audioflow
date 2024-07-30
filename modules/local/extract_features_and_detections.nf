params.model = 'birdnet_analyzer'
params.iterator = 'tensorflow'
params.batch_size = 32
params.threshold = 0.1

process extract_features_and_detections {
    label 'gpu'

    input:
    path 'input_dir'

    output:
    path 'features.parquet', emit: features
    path 'detections.parquet', emit: detections
    val true, emit: is_ready

    script:
    """
    extract_features_and_detections.py \
        --directory $input_dir \
        --features-output features.parquet \
        --detections-output detections.parquet \
        --threshold $params.threshold \
        --model $params.model \
        --iterator $params.iterator \
        --batch_size $params.batch_size
    """
}
