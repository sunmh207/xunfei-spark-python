# 科大讯飞星火模型 Python SDK

## 介绍

关于科大讯飞星火大模型，官网仅给出了[Web API文档](https://www.xfyun.cn/doc/spark/Web.html)，没有提供Python版SDK，使用起来不方便，尤其是在Stream交互的场景中。本项目封装了星火大模型的Web API，提供了类似OpenAI格式的SDK。

## 安装

```
pip install xunfei-spark-python==0.0.5
```

## 使用

### 1.问答接口

```python
from xunfei.spark.client import Spark
from xunfei.spark.response import ChatResponse

if __name__ == '__main__':
    config = {
        "app_id": "{your_app_id}",
        "api_secret": "{your_api_secret}",
        "api_key": "{your_api_key}",
        "gpt_url": "wss://spark-api.xf-yun.com/v3.5/chat",
        "domain": "generalv3.5",
    }
    spark = Spark(**config)
    messages = [{"role": "user", "content": "你是谁开发的？"}]

    response: ChatResponse = spark.chat(messages=messages)
    print('AI:', response.content)
    print('Token使用量:', response.usage)
```

### 2.Stream模式问答接口
    
```python
from xunfei.spark.client import Spark

if __name__ == '__main__':
    config = {
        "app_id": "{your_app_id}",
        "api_secret": "{your_api_secret}",
        "api_key": "{your_api_key}",
        "gpt_url": "wss://spark-api.xf-yun.com/v3.5/chat",
        "domain": "generalv3.5",
    }
    spark = Spark(**config)
    messages = [{"role": "user", "content": "你是谁开发的？"}]

    for message in spark.chat_stream(messages=messages):
        if message:
            if 'type' in message and message['type'] == 'chunk':
                print(f"客户端接受到的消息: {message}")
            elif 'type' in message and message['type'] == 'stop':
                print(f"结束")
                break
```