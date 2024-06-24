process getMetadata {
    conda './environment.yml'

    input:
    path 'audio_dir'

    output:
    stdout

    script:
    template 'get_metadata.sh'
}
