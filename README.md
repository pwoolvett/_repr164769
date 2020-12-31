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

### Install

* Install python requirements:

  ```console
  $ pip install -r requirements.txt 
  Processing /opt/nvidia/deepstream/deepstream/lib
  Installing collected packages: pyds
    Running setup.py install for pyds ... done
  Successfully installed pyds-1.0.1
  ```

* Copy models, config, and images

  ```console
  $ make
  cp -r /opt/nvidia/deepstream/deepstream/samples/models/Primary_Detector ./data/models
  cp -r /opt/nvidia/deepstream/deepstream/samples/models/Secondary_CarColor ./data/models
  cp data/configs/config_infer_primary.txt ./data/models/Primary_Detector
  cp data/configs/config_infer_secondary_carcolor.txt ./data/models/Secondary_CarColor
  ffmpeg -i /opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264 -start_number 0 -vframes 1088 data/cars/%012d.jpg
  ...
  Output #0, image2, to 'data/cars/%012d.jpg':
  ...
  ```
