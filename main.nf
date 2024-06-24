nextflow.preview.output = true

params.fileList = 'example_files.txt'
params.audioDir = '/mnt/gpfs/live/ritd-ag-project-rd00lk-kejon62/'
params.dataHost = 'rdss'
params.chunkSize = 3

include { splitFile } from './modules/local/splitFile'
include { copyFiles } from './modules/local/copyFiles'
include { getMetadata } from './modules/local/audio/getAudioMothMetadata'

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
