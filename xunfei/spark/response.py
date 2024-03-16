class ChatResponse():
    def __init__(self, content: str, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0):
        self.content = content
        self.usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
