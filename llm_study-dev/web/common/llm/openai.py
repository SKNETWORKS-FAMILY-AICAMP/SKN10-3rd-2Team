import enum
import time
from openai import OpenAI
from .provider import Provider

class OPENAI_LLMs(enum.Enum):
  gpt_4o_mini = (enum.auto(), "gpt-4o-mini") 
  gpt_4o = (enum.auto(), "gpt-4o") 


class Provider_OPENAI(Provider):
  def __init__(self, provider_LLMs=OPENAI_LLMs) -> None:
    super().__init__(provider_LLMs)
    self.client = OpenAI()

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
  

