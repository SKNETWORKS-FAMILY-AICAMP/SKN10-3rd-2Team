import enum
import time
from groq import Groq
from .provider import Provider

class GROQ_LLMs(enum.Enum):
  llama3 = (enum.auto(), "llama-3.3-70b-versatile") 
  qwen = (enum.auto(), "qwen-qwq-32b")

class Provider_GROQ(Provider):
  def __init__(self, provider_LLMs=GROQ_LLMs) -> None:
    super().__init__(provider_LLMs)
    self.client = Groq()

  def __call__(self, 
      model_name, messages):
    response = self.client.chat.completions.create(
      model=self.provider_LLMs[model_name].value[1],
      messages=messages,
      stream=True
    )

    for token in response:
      if token.choices[0].delta.content is not None:
        yield token.choices[0].delta.content
        time.sleep(0.05) 
