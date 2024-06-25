process getMetadata {
    debug true

    input:
    path 'audio_dir'

    output:
    stdout

    script:
    template 'get_metadata.sh'
}
