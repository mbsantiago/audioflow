process mergeParquet {
    input:
    path 'tables/*.parquet'

    output:
    path 'merged.parquet'

    script:
    """merge_parquet.py tables/*.parquet --output merged.parquet"""
}
