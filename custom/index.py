# -*- coding: utf-8 -*-

from imageai.Prediction import ImagePrediction
import base64
import bottle
import random
import json
import urllib.request


# 随机字符串

def randomStr(num=5): return "".join(
    random.sample('abcdefghijklmnopqrstuvwxyz', num))


# 模型加载
prediction = ImagePrediction()
prediction.setModelTypeAsResNet()
prediction.setModelPath("/code/model/resnet50_weights_tf_dim_ordering_tf_kernels.h5")
prediction.loadModel()


def predFunc(imagePath):
    # 内容预测
    result = {}
    predictions, probabilities = prediction.predictImage(imagePath, result_count=5)
    for eachPrediction, eachProbability in zip(predictions, probabilities):
        result[str(eachPrediction)] = str(eachProbability)
    return result


@bottle.route('/image_prediction', method='POST')
def getNextLine():
    imagePath = "/tmp/%s" % randomStr(10)
    postData = json.loads(bottle.request.body.read().decode("utf-8"))
    image = postData.get("image", None)
    if image:
        image = image.split("base64,")[1]
        # 图片获取
        with open(imagePath, 'wb') as f:
            f.write(base64.b64decode(image))
    else:
        image_path = postData.get("image_path", None)
        response = urllib.request.urlopen(image_path).read()
        with open(imagePath, 'wb') as f:
            f.write(response)

    return predFunc(imagePath)


@bottle.route('/', method='GET')
def getNextLine():
    return bottle.template('./html/index.html')


app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(host='0.0.0.0', port=9000)
