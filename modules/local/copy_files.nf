process copy_files {
    input:
    path file_list
    val host
    val base_dir

    output:
    path '*'

    shell:
    '''
    rsync -e "ssh" -azv --files-from=!{file_list} "!{host}:!{base_dir}" .
    '''
}
