# sdk调用示例
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

    # 非stream模式调用示例
    response: ChatResponse = spark.chat(messages=messages)
    print('AI:', response.content)
    print('Token使用量:', response.usage)

    # 以下是Stream模式调用示例
    for message in spark.chat_stream(messages=messages):
        if message:
            if 'type' in message and message['type'] == 'chunk':
                print(f"客户端接受到的消息: {message}")
            elif 'type' in message and message['type'] == 'stop':
                print(f"结束")
                break
