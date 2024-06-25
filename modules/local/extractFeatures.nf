params.model = 'birdnet_analyzer'
params.iterator = 'tensorflow'
params.batch_size = 32

process extractFeatures {
    input:
    path 'inputDir'

    output:
    path 'features.parquet'

    script:
    """
    extract_features.py \
        --directory $inputDir \
        --output features.parquet \
        --model $params.model \
        --iterator $params.iterator \
        --batch_size $params.batch_size
    """
}
