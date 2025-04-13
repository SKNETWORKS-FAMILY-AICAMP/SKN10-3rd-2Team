from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
import pandas as pd
import os

class VectorStore:
    def __init__(self, persist_directory="vector_store"):
        self.persist_directory = persist_directory
        # 성능 최적화: 더 적은 수의 임베딩 토큰 사용 및 캐싱 활성화
        self.embeddings = OllamaEmbeddings(
            model="gemma:2b", 
            base_url="http://localhost:11434", 
            num_ctx=512,  # 컨텍스트 창 크기 제한
            temperature=0.0  # 임베딩에는 낮은 temperature 사용
        )
        # 성능 최적화: LLM 구성 최적화
        self.llm = Ollama(
            model="gemma:2b", 
            base_url="http://localhost:11434",
            num_ctx=1024,  # 더 작은 컨텍스트 창
            num_gpu=1,  # GPU 사용 확인
            temperature=0.1,  # 더 낮은 온도로 더 빠른 생성
            num_thread=4  # 병렬 처리 스레드 수 지정
        )
        self.vector_store = None
        
    def load_data(self, csv_path):
        try:
            print(f"Loading data from {csv_path}")
            # CSV 파일 로드
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} rows from CSV")
            
            # Q&A 쌍을 문서로 변환
            documents = []
            for idx, row in df.iterrows():
                doc = f"Q: {row['Q']}\nA: {row['A']}"
                documents.append(doc)
            
            print(f"Created {len(documents)} documents")
            
            # 벡터 저장소 생성
            self.vector_store = FAISS.from_texts(
                documents,
                embedding=self.embeddings
            )
            
            print("Vector store created successfully")
            # 저장
            self.vector_store.save_local(self.persist_directory)
            print("Vector store saved")
            
        except Exception as e:
            print(f"Error in load_data: {str(e)}")
            raise
        
    def load_existing_store(self):
        try:
            if os.path.exists(self.persist_directory):
                print(f"Loading existing vector store from {self.persist_directory}")
                self.vector_store = FAISS.load_local(
                    self.persist_directory,
                    self.embeddings
                )
                print("Vector store loaded successfully")
                return True
            print("No existing vector store found")
            return False
        except Exception as e:
            print(f"Error in load_existing_store: {str(e)}")
            return False
    
    def similarity_search(self, query, k=1):
        if self.vector_store is None:
            print("Vector store is None, attempting to load existing store")
            if not self.load_existing_store():
                print("No existing store found, attempting to create new store")
                csv_path = os.path.join("data", "___RAG_QA_____.csv")
                self.load_data(csv_path)
        
        try:
            # 성능 최적화: k 값을 줄여 검색하는 문서 수 감소
            relevant_docs = self.vector_store.similarity_search(query, k=1)
            print(f"Found {len(relevant_docs)} similar documents")
            
            # 검색된 문서를 기반으로 Gemma가 응답 생성
            if relevant_docs:
                context = "\n".join([doc.page_content for doc in relevant_docs])
                # 성능 최적화: 프롬프트 간소화
                prompt = f"""
                정보: {context}
                질문: {query}
                답변:
                """
                
                response = self.llm(prompt)
                return [response]
            return []
            
        except Exception as e:
            print(f"Error in similarity_search: {str(e)}")
            raise 