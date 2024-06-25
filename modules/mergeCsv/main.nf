process mergeCsv {
    debug true
    cache false

    input:
    path 'table*.csv'

    output:
    path 'merged.csv'

    shell:
    '''
    awk 'NR == 1 || FNR > 1' table*.csv > merged.csv
    '''
}
