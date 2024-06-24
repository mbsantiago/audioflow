process copyFiles {
    input:
    path fileList
    val host
    val baseDir

    output:
    path '*'

    shell:
    '''
    rsync -e "ssh" -azv --files-from=!{fileList} "!{host}:!{baseDir}" .
    '''
}
