
.DEFAULT_GOAL := all

ds=/opt/nvidia/deepstream/deepstream/
stream=$ds/
models_src=/opt/nvidia/deepstream/deepstream/samples/models
models_dst=./models
export

install:
	cat /opt/nvidia/deepstream/deepstream/version | fgrep "Version: 5.0" && exit 0 || echo "please install deepstream"
	which ffmpeg && exit 0 || echo "please install ffmpeg first"
	python3 -V | grep 3.6.9 && exit 0 || echo "python3.6.9 required" && exit 1
	make .venv
	make reqs

.venv:
	python3 -m venv .venv

reqs:
	.venv/bin/pip install -r requirements.txt

models:
	cp -r ${models_src}/Primary_Detector ${models_dst}/Primary_Detector
	cp -r ${models_src}/Secondary_CarColor ${models_dst}/Secondary_CarColor

config:
	cp configs/config_infer_primary.txt ${models_dst}/Primary_Detector
	cp configs/config_infer_secondary_carcolor.txt ${models_dst}/Secondary_CarColor

images:
	ffmpeg -i /opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264 -start_number 0 -vframes 1088 cars/%012d.jpg

all: install models config images

clean:
	-rm -rf .venv
	-rm cars/*.jpg
	-rm -rf ${models_dst}/Primary_Detector ${models_dst}/Secondary_CarColor

.PHONY: data config reqs models config images clean

