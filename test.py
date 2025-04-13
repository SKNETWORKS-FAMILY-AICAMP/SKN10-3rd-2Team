from common import DocumentProcessor, VectorStore, Reranker, Retriever, DataLoader
import os

def main():
    # 1. 데이터 로드
    data_loader = DataLoader("data/___RAG_QA_____.csv")
    documents = data_loader.load_csv()
    
    # 2. 문서 처리
    doc_processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    split_docs = doc_processor.split_documents(documents)
    
    # 3. 벡터 저장소 생성
    vector_store = VectorStore()
    vector_store.create_from_documents(split_docs)
    base_retriever = vector_store.get_retriever(k=5)
    
    # 4. 재순위화 설정
    reranker = Reranker()
    
    # 5. 검색기 설정
    retriever = Retriever()
    multi_query_retriever = retriever.create_multi_query_retriever(base_retriever)
    compression_retriever = retriever.create_compression_retriever(
        reranker.get_compressor(),
        multi_query_retriever
    )
    
    # 6. 검색 실행
    query = "수업 중 흡연이나 외출이 가능한가요?"
    results = compression_retriever.invoke(query)
    
    # 7. 결과 출력
    DocumentProcessor.pretty_print_docs(results)

if __name__ == "__main__":
    main()
