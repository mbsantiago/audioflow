params.fileList = 'example_files.txt'
params.audioDir = '/mnt/gpfs/live/ritd-ag-project-rd00lk-kejon62/'
params.dataHost = 'rdss'
params.chunkSize = 3

include { splitFile } from './modules/local/splitFile'
include { copyFiles } from './modules/local/copyFiles'
include { mergeCsv } from './modules/local/mergeCsv'
include { parseMetadata } from './modules/local/parseMetadata'
include { extractFeatures } from './modules/local/extractFeatures'
include { mergeParquet } from './modules/local/mergeParquet'

nextflow.preview.output = true

workflow {
    main:
    file = channel.fromPath(params.fileList)
    fileChunks = splitFile(file, params.chunkSize) | flatten
    outputFiles = copyFiles(
        fileChunks,
        params.dataHost,
        params.audioDir
    )
    metadataFiles = parseMetadata(outputFiles).collect()
    featureFiles = extractFeatures(outputFiles).collect()
    metadata = mergeCsv(metadataFiles)
    features = mergeParquet(featureFiles)

    emit:
    metadata
    features

    publish:
    metadata >> 'metadata'
    features >> 'features'
}

output {
    directory 'results'
    mode 'copy'
}
