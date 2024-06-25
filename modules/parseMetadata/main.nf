process getMetadata {
    input:
    path 'inputDir'

    output:
    path 'metadata.csv'

    script:
    """python $moduleDir/extract_metadata.py --directory $inputDir --output metadata.csv"""
}
