process getMetadata {
    conda './environment.yml'

    input:
    path '*.WAV'

    output:
    stdout

    script:
    '''
    ls *.WAV
    '''
}
