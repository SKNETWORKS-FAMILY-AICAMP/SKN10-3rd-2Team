import os
import subprocess
import time
import requests
from typing import Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('OllamaManager')

class OllamaManager:
    """
    Ollama 서버 관리를 위한 클래스
    """
    
    @staticmethod
    def start_ollama_server() -> bool:
        """
        Ollama 서버를 시작합니다.
        
        Returns:
            bool: 서버 시작 성공 여부
        """
        try:
            # Ollama 서버가 이미 실행 중인지 확인
            if OllamaManager._is_ollama_running():
                logger.info("Ollama 서버가 이미 실행 중입니다.")
                return True
                
            # Ollama 서버 시작
            logger.info("Ollama 서버를 시작합니다...")
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
            # 서버가 시작될 때까지 대기
            max_retries = 30
            retry_count = 0
            while retry_count < max_retries:
                if OllamaManager._is_ollama_running():
                    logger.info("Ollama 서버가 성공적으로 시작되었습니다.")
                    return True
                time.sleep(1)
                retry_count += 1
                
            logger.error("Ollama 서버 시작 실패: 타임아웃")
            return False
            
        except Exception as e:
            logger.error(f"Ollama 서버 시작 중 오류 발생: {str(e)}")
            return False
            
    @staticmethod
    def _is_ollama_running() -> bool:
        """
        Ollama 서버가 실행 중인지 확인합니다.
        
        Returns:
            bool: 서버 실행 여부
        """
        try:
            response = requests.get("http://localhost:11434/api/version")
            return response.status_code == 200
        except:
            return False
            
    @staticmethod
    def pull_model(model_name: str) -> bool:
        """
        Ollama 모델을 다운로드합니다.
        
        Args:
            model_name: 다운로드할 모델 이름
            
        Returns:
            bool: 다운로드 성공 여부
        """
        try:
            logger.info(f"모델 {model_name} 다운로드를 시작합니다...")
            result = subprocess.run(["ollama", "pull", model_name],
                                  capture_output=True,
                                  text=True)
            
            if result.returncode == 0:
                logger.info(f"모델 {model_name} 다운로드가 완료되었습니다.")
                return True
            else:
                logger.error(f"모델 다운로드 실패: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"모델 다운로드 중 오류 발생: {str(e)}")
            return False 