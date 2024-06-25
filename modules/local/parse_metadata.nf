process parse_metadata {
    input:
    path 'input_dir'

    output:
    path 'metadata.csv', emit: metadata
    val true, emit: is_ready

    script:
    """parse_metadata.py --directory $input_dir --output metadata.csv"""
}
