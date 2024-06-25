params.fileList = 'example_files.txt'
params.audioDir = '/mnt/gpfs/live/ritd-ag-project-rd00lk-kejon62/'
params.dataHost = 'rdss'
params.chunkSize = 3

include { splitFile } from './modules/splitFile'
include { copyFiles } from './modules/copyFiles'
include { mergeCsv } from './modules/mergeCsv'
include { parseMetadata } from './modules/parseMetadata'
include { extractFeatures } from './modules/extractFeatures'
include { mergeParquet } from './modules/mergeParquet'

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
