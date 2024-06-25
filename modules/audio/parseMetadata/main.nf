process getMetadata {
    debug true
    cache false

    input:
    path 'inputDir'

    output:
    path 'metadata.csv'

    script:
    template 'get_metadata.sh'
}
