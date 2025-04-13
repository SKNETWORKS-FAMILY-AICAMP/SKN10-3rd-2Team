from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """문서를 청크로 분할합니다."""
        return self.text_splitter.split_documents(documents)
    
    @staticmethod
    def pretty_print_docs(docs: List[Document]) -> None:
        """문서를 보기 좋게 출력합니다."""
        print(
            f"\n{'-' * 100}\n".join(
                [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
            )
        ) 