process clean_files {
    cache false

    input:
    path 'input_dir'
    val process_ready
    val metadata_ready

    output:
    val true, emit: is_clean

    script:
    """
    clean_files.py input_dir
    """
}
