import enum

class Provider:
  def __init__(self, provider_LLMs:enum.Enum) -> None:
    self.provider_LLMs = provider_LLMs # provider가 제공하는 모델 리스트 
  # 호출함수 역할
  def __call__(self, 
      model_name, messages):
    pass

