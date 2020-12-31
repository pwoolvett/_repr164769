# repr164769

Reproduce issue/question `164769`, as reported [here](https://forums.developer.nvidia.com/t/no-sgie-metadata-for-some-pgie-detections-using-pyds/164769).

## Setup

### Pre-requisites

* Jetson (Xavier tested only)
* python

  ```console
  $ python -V
  Python 3.6.9
  ```

* Deepstream

  ```console
  $ cat /opt/nvidia/deepstream/deepstream/version
  Version: 5.0
  GCID: 23607587
  EABI: 
  DATE: Mon Sep 28 20:42:34 UTC 2020
  ```

* ffmpeg (to generate frames only):

  ```console
  $ ffmpeg -version | head -n 1
  ffmpeg version 3.4.8-0ubuntu0.2 Copyright (c) 2000-2020 the FFmpeg developers
  ```
* GNU make (to ease dev only):

  ```console
  $ make -v
  GNU Make 4.1
  ```



### Install

* Just run `make` in the repo root, which does the following:

  1. Ensure prerequisites are met
  1. Create python 3.6.9 venv in `.venv.` folder
  1. Install `requirements.txt`
  1. Copies models from `/opt` to allow engine creation with normal user perms
  1. Extracts frames from sample cars video
  1. Configure `nvinfer` pgie and `sgie` to reproduce issue

## Usage

  ```console
  $ ./demo.py
  ...
  detections: 16495

  classifications: 15248
  ```

Note: first run takes a while longer as it generates the engine. Subsequent runs should take around 10 [sec] for the demo data.
