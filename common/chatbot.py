from typing import List, Dict

class Chatbot:
    def _create_prompt(self, query: str, context: List[Dict]) -> str:
        """
        LLM 프롬프트 생성
        
        Args:
            query: 사용자 쿼리
            context: 검색된 문서 목록
            
        Returns:
            str: 생성된 프롬프트
        """
        if not context:
            return f"""다음 질문에 대해 정확한 답변을 할 수 있는 정보가 없습니다.
질문: {query}

답변: 죄송합니다. 질문에 대한 정확한 정보를 찾을 수 없습니다. 다른 방식으로 질문해주시거나, 다른 주제에 대해 물어보시겠습니까?"""
        
        # 참고 정보를 구조화된 형태로 변환
        context_str = "\n\n".join([
            f"""참고 정보 {i+1}:
제목: {doc.get('title', '제목 없음')}
내용: {doc.get('content', '')}
관련성 점수: {doc.get('score', 0):.2f}"""
            for i, doc in enumerate(context)
        ])
        
        return f"""다음 질문에 대해 정확하고 구조화된 답변을 생성해주세요.

답변 생성 규칙:
1. 참고 정보를 기반으로만 답변하세요. 참고 정보에 없는 내용은 추가하지 마세요.
2. 답변은 다음 구조를 따라주세요:
   - 핵심 답변: 질문에 대한 직접적인 답변
   - 상세 설명: 필요한 경우 추가 설명
   - 참고 사항: 주의할 점이나 추가 정보
3. 불확실한 정보는 포함하지 마세요.
4. 참고 정보가 충분하지 않거나 불확실한 경우, "정확한 정보를 찾을 수 없습니다"라고 답변하세요.

질문: {query}

참고 정보:
{context_str}

답변:""" 