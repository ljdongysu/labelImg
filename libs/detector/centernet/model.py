#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 焦子傲
@contact: jiao1943@qq.com
@file: model.py
@time: 2021/4/14 9:51
@desc:
'''
import os
from libs.detector.ssd.onnxmodel import ONNXModel
from libs.detector.centernet.preprocess import pre_process as centerNetPreProcess
from libs.detector.centernet.postprocess.postprocess import PostProcessor_CENTER_NET
from libs.detector.centernet.postprocess.postprocess import CONFIDENCE_THRESHOLD, IMAGE_SIZE_CENTER_NET
from libs.detector.yolov3.postprocess.postprocess import load_class_names
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__)).split('libs')[0]

class CenterNet(object):
    def __init__(self, file='./config/human/centernet.onnx',class_sel=[]):
        self.classes = load_class_names(CURRENT_DIR+"config/human/classes.names")
        self.class_sel = class_sel

        if os.path.isfile(file):
            self.net = ONNXModel(file)
        else:
            raise IOError("no such file {}".format(file))

    def forward(self, img_input):
        image, meta = centerNetPreProcess(img_input, IMAGE_SIZE_CENTER_NET, 1, None)
        out = self.net.forward(image)
        results_batch = PostProcessor_CENTER_NET(out, meta)  # CenterNet

        # TODO : get rect
        shapes = []
        results_box=[]
        for result in results_batch.values():
            if len(result) > 0:
                result = result.tolist()
                result = [r for r in result if r[4] > CONFIDENCE_THRESHOLD]
                for r in result:
                    x, y, x2, y2, score = r
                    label=0
                    if int(label) > len(self.classes)-1 or self.classes[int(label)] not in self.class_sel:
                        continue

                    x, y, x2, y2, score = int(x), int(y), int(x2), int(y2), float(score)
                    shapes.append(("person", [(x, y), (x2, y), (x2, y2), (x, y2)], None, None, False))
                    results_box.append([x, y, x2, y2, score, self.classes[label]])
        return shapes,results_box
