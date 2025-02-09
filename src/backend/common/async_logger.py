import logging
import queue
import threading
import time
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

class AsyncQueueHandler(logging.Handler):
    def __init__(self, log_file, max_queue_size=1000, max_file_size=10*1024*1024, backup_count=5):
        super().__init__()
        
        # 로그 디렉토리 생성
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일 핸들러
        self.file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_file_size, 
            backupCount=backup_count
        )
        self.file_handler.setFormatter(self.formatter)
        
        # 로그 큐
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        
        # 중지 이벤트
        self.stop_event = threading.Event()
        
        # 로그 쓰기 스레드 시작
        self.log_thread = threading.Thread(target=self._log_worker)
        self.log_thread.daemon = True
        self.log_thread.start()

    def emit(self, record):
        try:
            # 비블로킹 모드로 큐에 로그 추가
            self.log_queue.put_nowait(record)
        except queue.Full:
            # 큐가 가득 찬 경우 가장 오래된 로그 제거
            try:
                self.log_queue.get_nowait()
                self.log_queue.put_nowait(record)
            except queue.Empty:
                pass

    def _log_worker(self):
        """백그라운드 로그 쓰기 스레드"""
        while not self.stop_event.is_set():
            try:
                # 0.1초 대기, 타임아웃 발생 시 다시 확인
                record = self.log_queue.get(timeout=0.1)
                
                # 포맷터 적용
                msg = self.format(record)
                
                # 로그 파일에 쓰기
                self.file_handler.emit(record)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"로깅 중 오류 발생: {e}")

    def close(self):
        """로깅 스레드 종료"""
        self.stop_event.set()
        self.log_thread.join()
        self.file_handler.close()
        super().close()

    def setup_async_queue_logger(
        logger_name='async_logger', 
        log_file='./log/app.log', 
        log_level=logging.INFO
    ):
        # 기존 로거 초기화
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        
        # 기존 핸들러 제거
        logger.handlers.clear()
        
        # 비동기 큐 핸들러 생성
        async_handler = AsyncQueueHandler(log_file)
        async_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        )
        
        # 로거에 핸들러 추가
        logger.addHandler(async_handler)
        
        # 콘솔 핸들러 추가 (옵션)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        )
        logger.addHandler(console_handler)
        
        return logger
