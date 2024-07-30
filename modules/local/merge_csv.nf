process merge_csv {
    input:
    path 'table*.csv'

    output:
    path 'merged.csv', emit: merged

    shell:
    '''
    awk 'NR == 1 || FNR > 1' table*.csv > merged.csv
    '''
}
