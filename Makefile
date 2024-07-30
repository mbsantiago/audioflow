run-cpu:
	nextflow run -profile local_cpu -params-file params.json .

run-gpu:
	nextflow run -profile local_gpu -params-file params.json .

clean-work:
	rm -rf work

clean-logs:
	rm -rf report .nextflow.log* .nextflow.pid .nextflow.pid .nextflow-console.log

clean-results:
	rm -rf results
	rm -rf outputs

clean-all: clean-work clean-logs clean-results
