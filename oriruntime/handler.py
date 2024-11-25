from imageai.Prediction import ImagePrediction
import os
import oss2
import json
import random


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


def handler(event, context):
    events = json.loads(event.decode("utf-8"))["events"]
    auth = oss2.StsAuth(os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
                     os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
                     os.environ.get('ALIBABA_CLOUD_SECURITY_TOKEN'))
    bucket = oss2.Bucket(auth, os.environ.get('OSS_ENDPOINT'), os.environ.get('OSS_BUCKET'))
    for eveObject in events:
        # 路径处理
        file = eveObject["oss"]["object"]["key"]
        file_token = file.split('/')[-1]
        origin_file = os.environ.get('SOURCE') + file_token
        target_file = os.environ.get('TARGET') + file_token + '.txt'
        local_source_file = '/tmp/' + file_token + '.png'

        # 下载文件
        bucket.get_object_to_file(origin_file, local_source_file)

        # 获取结果
        result = json.dumps({"result": predFunc(local_source_file)})
        print(result)

        # 回传结果
        bucket.put_object(target_file, result)

    return True
