process splitFile {
    input:
    path file
    val chunkSize

    output:
    path 'chunk_*'

    shell:
    '''
    cat !{file} | split -l !{chunkSize} - "chunk_"
    '''
}
