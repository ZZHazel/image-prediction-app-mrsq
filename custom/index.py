# -*- coding: utf-8 -*-
import requests
import base64
import bottle
import random
import json
import io
from PIL import Image

# Hugging Face 模型 API 配置
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
HEADERS = {"Authorization": "Bearer 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"}

# 随机字符串生成器
def random_str(num=5):
    return "".join(random.sample('abcdefghijklmnopqrstuvwxyz', num))

# 查询 Hugging Face 模型
# 查询 Hugging Face 模型
def query_model(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=HEADERS, json=payload,timeout=600)
    if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
        return response.content, None
    else:
        error_details = response.json() if response.headers.get("content-type") == "application/json" else response.text
        return None, error_details

# Bottle 路由
@bottle.route('/generate_image', method='POST')
def generate_image():
    try:
        # 获取 POST 数据
        post_data = json.loads(bottle.request.body.read().decode("utf-8"))
        prompt = post_data.get("prompt", None)

        if not prompt:
            return {"error": "Missing 'prompt' in the request body."}

        # 调用 Hugging Face 模型
        image_bytes, error = query_model(prompt)

        if error:
            return {"error": "Failed to generate image.", "details": error}

        # 将图像保存到临时路径
        image_path = f"/tmp/{random_str(10)}.png"
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        # 返回 Base64 编码图像
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        return {"image": f"data:image/png;base64,{encoded_image}"}

    except Exception as e:
        return {"error": str(e)}

@bottle.route('/', method='GET')
def index():
    return bottle.template('./html/index.html')

# Bottle 应用
app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(host='0.0.0.0', port=9000)
