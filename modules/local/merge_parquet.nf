process merge_parquet {
    input:
    path 'tables/*.parquet'

    output:
    path 'merged.parquet', emit: merged

    script:
    """merge_parquet.py tables/*.parquet --output merged.parquet"""
}
