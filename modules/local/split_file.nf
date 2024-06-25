process split_file {
    input:
    path file
    val chunk_size

    output:
    path 'chunk_*'

    shell:
    '''
    cat !{file} | split -l !{chunk_size} - "chunk_"
    '''
}
