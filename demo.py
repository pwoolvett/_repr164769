#!./.venv/bin/python3
# -*- coding: utf-8 -*-
""""""

import logging
from pathlib import Path

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst
from gi.repository import GObject
import pyds

logger = logging.getLogger(__name__)

PIPELINE_SRC = Path(__file__).parent / "pipeline.txt"

def file_logger(filepath):
    path = Path(filepath).resolve()
    logger = logging.getLogger(path.stem)
    logger.setLevel(logging.INFO)
    ch = logging.FileHandler(str(path))
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)
    return logger

def build_pipeline():
    with open(PIPELINE_SRC) as fp:
        pipeline_string = fp.read()

    pipeline = Gst.parse_launch(pipeline_string)
    if not pipeline:
        raise RuntimeError
    return pipeline

def on_eos(bus, message, loop):
    logger.info("Gstreamer: End-of-stream")
    loop.quit()

def on_error(bus, message, loop):
    err, debug = message.parse_error()
    logger.error("Gstreamer: %s: %s" % (err, debug))
    loop.quit()

def connect_messages(bus, loop):
    bus.add_signal_watch()
    bus.connect("message::eos", on_eos, loop)
    bus.connect("message::error", on_error, loop)

def _get_or_raise(obj, by, name=None):
    getter = getattr(obj, by)
    if name:
        attribute = getter(name)
    else:
        attribute = getter()
    if not attribute:
        raise AttributeError(f"""{obj}.{by}("{name or ''}") returned None""")
    return attribute

def osd_sink_pad_buffer_probe(pad, info, detslogger, classiflogger):
    num_rects=0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number=frame_meta.frame_num
        source_id = frame_meta.source_id
        l_obj=frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            detslogger.info(
                f"{source_id}\t{frame_number}\t{obj_meta.class_id}\t{obj_meta.confidence}\t"
            )
            classifier_meta_objects = obj_meta.classifier_meta_list  # THIS IS NONE SOMETIMES, but generally a `pyds.GList`
            while classifier_meta_objects is not None:
                try:
                    classifier_metadata = pyds.NvDsClassifierMeta.cast(classifier_meta_objects.data)
                except StopIteration:
                    break

                label_info_list = classifier_metadata.label_info_list  # I think we've got to iterate again here for the multilabel case...
                while label_info_list is not None:
                    try:
                        label_info = pyds.NvDsLabelInfo.cast(label_info_list.data)
                    except StopIteration:
                        break
                    classiflogger.info(
                        f"{source_id}\t{frame_number}\t{label_info.result_class_id}\t{label_info.result_prob}\t"
                    )
                    try:
                        label_info_list = label_info_list.next
                    except StopIteration:
                        break
                try:
                    classifier_meta_objects = classifier_meta_objects.next
                except StopIteration:
                    break
            try: 
                l_obj=l_obj.next
            except StopIteration:
                break
        try:
            l_frame=l_frame.next
        except StopIteration:
            break
    return Gst.PadProbeReturn.OK

def attach_buffer_probe(pipeline, detslogger, classiflogger):
    monitor = _get_or_raise(pipeline, "get_by_name", "monitor")
    sinkpad = _get_or_raise(monitor, "get_static_pad", "sink")
    sinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, detslogger, classiflogger)

def main():
    mainloop = GObject.MainLoop()
    pipeline = build_pipeline()
    connect_messages(pipeline.get_bus(), mainloop)

    attach_buffer_probe(
        pipeline,
        file_logger("logs/detections"),
        file_logger("logs/classifications")
    )

    pipeline.set_state(Gst.State.PLAYING)

    try:
        mainloop.run()
    finally:
        pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    logs = Path("logs")
    logs.mkdir(exist_ok=True, parents=True)
    for logfile in logs.iterdir():
        logfile.unlink()
    Gst.init(None)
    main()
