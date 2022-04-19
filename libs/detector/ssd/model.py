#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 焦子傲
@contact: jiao1943@qq.com
@file: model.py
@time: 2021/4/14 10:42
@desc:
'''
import os
from libs.detector.ssd.onnxmodel import ONNXModel
from libs.detector.ssd.preprocess import pre_process
from libs.detector.ssd.postprocess.ssd import PostProcessor_SSD
from libs.detector.ssd.postprocess.ssd import THRESHOLD
from libs.detector.yolov3.postprocess.postprocess import load_class_names
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__)).split('libs')[0]

class SSD(object):
    def __init__(self, file='./config/cleaner/ssd.onnx',class_sel=[]):
        self.classes = load_class_names(CURRENT_DIR+"config/cleaner/classes.names")
        self.class_sel = class_sel

        if os.path.isfile(file):
            self.net = ONNXModel(file)
        else:
            raise IOError("no such file {}".format(file))

    def forward(self, image, class_names_4_detect):
        image, ratio = pre_process(image)
        out = self.net.forward(image)
        results_batch = PostProcessor_SSD(out[0], out[1], out[2])

        # TODO : get rect
        shapes = []
        results_box=[]
        for result in results_batch:
            if len(result) > 0:
                result = result.tolist()
                for r in result:
                    x, y, x2, y2, label, score = r
                    x, y, x2, y2, label = int(x) * ratio[0], int(y) * ratio[1], int(x2) * ratio[0], int(y2) * ratio[
                        1], int(label)
                    # if int(label) > len(self.classes) - 1 or self.classes[int(label)] not in self.class_sel:
                    #     continue

                    shapes.append(
                        (self.classes[label], [(x, y), (x2, y), (x2, y2), (x, y2)], None, None, False))
                    results_box.append([x, y, x2, y2, score, self.classes[label]])
        return shapes,results_box
