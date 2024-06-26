params.model = 'birdnet_analyzer'
params.iterator = 'tensorflow'
params.batch_size = 64

process extract_features {
    maxForks 1

    input:
    path 'input_dir'

    output:
    path 'features.parquet', emit: features
    val true, emit: is_ready

    script:
    """
    extract_features.py \
        --directory $input_dir \
        --output features.parquet \
        --model $params.model \
        --iterator $params.iterator \
        --batch_size $params.batch_size
    """
}
