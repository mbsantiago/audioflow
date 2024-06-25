params.model = 'birdnet_analyzer'
params.iterator = 'tensorflow'
params.batch_size = 32

process extractFeatures {
    debug true
    maxForks 1

    input:
    path 'inputDir'

    output:
    path 'features.parquet'

    script:
    """
    python $moduleDir/extract_features.py \
        --directory $inputDir \
        --output features.parquet \
        --model $params.model \
        --iterator $params.iterator \
        --batch_size $params.batch_size
    """
}
