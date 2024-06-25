params.fileList = 'example_files.txt'
params.audioDir = '/mnt/gpfs/live/ritd-ag-project-rd00lk-kejon62/'
params.dataHost = 'rdss'
params.chunkSize = 3

include { splitFile } from './modules/splitFile'
include { copyFiles } from './modules/copyFiles'
include { getMetadata } from './modules/audio/parseMetadata'

workflow {
    main:
    file = channel.fromPath(params.fileList)
    fileChunks = splitFile(file, params.chunkSize) | flatten
    outputFiles = copyFiles(
        fileChunks,
        params.dataHost,
        params.audioDir
    )

    getMetadata(outputFiles) | view
}
