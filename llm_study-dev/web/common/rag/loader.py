
from langchain_community.document_loaders.csv_loader import CSVLoader

def get_loader(file_path:str="new 질병.csv"):
  if file_path.endswith(".csv"):
    return CSVLoader(file_path=file_path, encoding='utf-8'
                    , source_column="video_url")
  else:
    raise Exception("지원하지 않는 파일 형식입니다.")

