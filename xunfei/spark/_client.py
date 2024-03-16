import _thread as thread
import base64
import hashlib
import hmac
import json
import ssl
import threading
import time
from datetime import datetime
from time import mktime
from typing import Dict, List, Literal
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time

import websocket

from xunfei.spark._response import ChatResponse


class Spark():
    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 gpt_url: str = "wss://spark-api.xf-yun.com/v3.5/chat",
                 domain: str = "generalv3.5"):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.gpt_url = gpt_url
        self.domain = domain
        self.host = urlparse(self.gpt_url).netloc
        self.path = urlparse(self.gpt_url).path
        self.response_content = ''
        self.message_queue = []
        self.wss_status: Literal['none', 'open', 'closed', 'error'] = 'none'

    def _generate_signature(self, date):
        signature_origin = f"host: {self.host}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {self.path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(signature_sha).decode(encoding='utf-8')

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{self._generate_signature(date)}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        return self.gpt_url + '?' + urlencode(v)

    def gen_params(self, domain, messages):
        data = {
            "header": {
                "app_id": self.app_id,
                "uid": "1234",
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": messages
                }
            }
        }
        return data

    def chat(self, messages: List[Dict[str, str]], domain: str = "generalv3.5") -> ChatResponse:
        """Chat with the model."""

        def run(ws, *args):
            data = json.dumps(self.gen_params(domain=ws.domain, messages=ws.messages))
            ws.send(data)

        def on_message(ws, message):
            data = json.loads(message)
            code = data['header']['code']
            if code != 0:
                self.response_content = data['header']['message']
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                self.response_content += content
                if status == 2:
                    self.prompt_tokens = data["payload"]["usage"]["text"]["prompt_tokens"]
                    self.completion_tokens = data["payload"]["usage"]["text"]["completion_tokens"]
                    self.total_tokens = data["payload"]["usage"]["text"]["total_tokens"]
                    ws.close()

        def on_error(ws, error):
            self.wss_status = 'error'

        def on_close(*args):
            self.wss_status = 'closed'

        def on_open(ws):
            self.wss_status = 'open'
            thread.start_new_thread(run, (ws,))

        websocket.enableTrace(False)
        ws_url = self.create_url()

        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close,
                                    on_open=on_open)
        ws.app_id = self.app_id
        ws.messages = messages
        ws.domain = self.domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        return ChatResponse(content=self.response_content, prompt_tokens=self.prompt_tokens,
                            completion_tokens=self.completion_tokens,
                            total_tokens=self.total_tokens
                            )

    def chat_stream(self, messages: List[Dict[str, str]], domain: str = "generalv3.5", timeout: int = 60):
        def run(ws, *args):
            data = json.dumps(self.gen_params(domain=ws.domain, messages=ws.messages))
            ws.send(data)

        def on_message(ws, message):
            data = json.loads(message)

            # 异常
            if data['header']['code'] != 0:
                self.message_queue.append({
                    "type": "chunk",
                    "content": data['header']['message']
                })
                self.message_queue.append({
                    "type": "stop",
                    "content": ""
                })
                ws.close()
            else:
                self.message_queue.append({
                    "type": "chunk",
                    "content": data["payload"]["choices"]["text"][0]["content"]
                })
                if data["payload"]["choices"]["status"] == 2:
                    self.message_queue.append({
                        "type": "stop",
                        "content": ""
                    })
                    ws.close()

        def on_error(ws, error):
            self.wss_status = 'error'

        def on_close(*args):
            self.wss_status = 'closed'

        def on_open(ws):
            self.wss_status = 'open'
            wst = threading.Thread(target=run(ws, ))
            wst.daemon = True
            wst.start()

        websocket.enableTrace(False)
        ws_url = self.create_url()

        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close,
                                    on_open=on_open)
        ws.messages = messages
        ws.domain = self.domain
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        start_time = time.time()
        while True:
            if self.message_queue:
                yield self.message_queue.pop(0)
            else:
                # Sleep for a short time to avoid busy waiting
                time.sleep(0.1)
            # Check timeout
            elapsed_time = time.time() - start_time
            # 全部取出或者超时则停止
            if (self.wss_status == 'closed' and len(self.message_queue) == 0) or elapsed_time >= timeout:
                break
