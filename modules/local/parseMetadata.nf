process parseMetadata {
    input:
    path 'inputDir'

    output:
    path 'metadata.csv'

    script:
    """parse_metadata.py --directory $inputDir --output metadata.csv"""
}
