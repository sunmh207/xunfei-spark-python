# 科大讯飞星火模型 Python SDK

## 介绍

关于科大讯飞星火模型 Python调用，科大讯飞官网仅给出了Web API文档。 本项目是对官方Web API封装，便于用户调用。

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