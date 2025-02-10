import subprocess
import time
import os
import sys
import signal
import logging
from typing import List, Dict
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 디렉토리를 시스템 경로에 추가
sys.path.append(str(Path(__file__).parent))

# 이제 backend 패키지에서 import 가능
from backend.config import LOGS_DIR
from backend.common.logger import setup_logger

class ServiceMonitor:
    def __init__(self):
        self.service_status = {}
        # 서비스 모니터링용 로거 설정
        self.logger = setup_logger('service_monitor', 'service_monitor.log')
    
    def update_status(self, service_name: str, status: str):
        self.service_status[service_name] = {
            'status': status,
            'last_update': datetime.now()
        }
    
    def check_services(self):
        current_time = datetime.now()
        for service, info in self.service_status.items():
            if (current_time - info['last_update']).seconds > 30:
                self.logger.warning(f"{service} 응답 없음: {info['status']}")

class ProgramLauncher:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.monitor = ServiceMonitor()
        
        # logs 디렉토리 생성 (config.py의 LOGS_DIR 사용)
        LOGS_DIR.mkdir(exist_ok=True)
        
        # 로거 설정 (self.logger로 저장)
        self.logger = setup_logger('launcher', 'launcher.log')
        
    def start_backend_services(self):
        """백엔드 서비스 시작"""
        # Python 실행 파일 경로 확인
        python_path = sys.executable
        
        # 프로젝트 기본 경로
        base_path = self.base_dir

        service_groups = [
            # 그룹 1: 기본 서버들
            [
                ("Stocker Server", [python_path, str(base_path / "backend" / "stocker" / "stocker_async_server.py")]),
                ("Gas Cabinet Server", [python_path, str(base_path / "backend" / "gas_cabinet" / "gas_async_server.py")]),
            ],
            # 그룹 2: 웹 서버들
            [
                ("Stocker Web Server", [python_path, str(base_path / "backend" / "stocker" / "stocker_web_server.py")]),
                ("Gas Cabinet Web Server", [python_path, str(base_path / "backend" / "gas_cabinet" / "gas_web_server.py")]),
            ],
            # 그룹 3: 클라이언트들
            [
                ("Stocker Client", [python_path, str(base_path / "backend" / "stocker" / "stocker_async_client.py")]),
                ("Gas Cabinet Client1", [python_path, str(base_path / "backend" / "gas_cabinet" / "gas_async_client1.py")]),
                ("Gas Cabinet Client2", [python_path, str(base_path / "backend" / "gas_cabinet" / "gas_async_client2.py")]),
                ("Gas Cabinet Client3", [python_path, str(base_path / "backend" / "gas_cabinet" / "gas_async_client3.py")]),
            ]
        ]
        
        # 그룹별로 순차적 시작
        for i, group in enumerate(service_groups):
            self.logger.info(f"Starting service group {i+1}...")  # INFO로 변경
            for name, command in group:
                self._start_process(name, command)
                self.monitor.update_status(name, "started")
                time.sleep(3)
            
            wait_time = 5
            self.logger.info(f"Waiting {wait_time} seconds before starting next group...")  # INFO로 변경
            time.sleep(wait_time)
    
    def _start_process(self, name: str, command: List[str]):
        try:
            self.logger.info(f"Starting {name}...")
            self.logger.info(f"Command: {' '.join(command)}")
            self.logger.info(f"Working directory: {self.base_dir}")
            
            # 각 서비스별 로그 파일 설정
            log_file = LOGS_DIR / f'{name.lower().replace(" ", "_")}.log'
            
            # 환경변수에 PYTHONPATH 추가
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.base_dir)
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,  # 파이프로 변경
                stderr=subprocess.PIPE,  # 파이프로 변경
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(self.base_dir),
                env=env
            )
            
            # 비동기로 출력 읽기
            def log_output(pipe, is_error):
                for line in pipe:
                    if is_error:
                        self.logger.info(f"{name}: {line.strip()}")  # 에러 스트림은 ERROR로
                    else:
                        self.logger.info(f"{name}: {line.strip()}")   # 일반 출력은 INFO로
                
            import threading
            threading.Thread(target=log_output, args=(process.stdout, False), daemon=True).start()
            threading.Thread(target=log_output, args=(process.stderr, True), daemon=True).start()
            
            self.processes[name] = process
            self.logger.info(f"{name} started with PID {process.pid}")
            
            # 프로세스 상태 확인
            if process.poll() is None:
                self.monitor.update_status(name, "running")
            else:
                #self.logger.warning(f"{name} failed to start")  # 경고로 변경
                self.monitor.update_status(name, "failed")
                
        except Exception as e:
            #self.logger.error(f"Failed to start {name}: {str(e)}", exc_info=True)  # 실제 에러는 ERROR로 유지
            self.monitor.update_status(name, f"error: {str(e)}")
        
    def stop_all(self):
        """모든 프로세스 중지"""
        for name, process in self.processes.items():
            self.logger.info(f"Stopping {name}...")  # INFO로 변경
            try:
                if sys.platform == 'win32':
                    process.send_signal(signal.CTRL_C_EVENT)
                else:
                    process.terminate()
                process.wait(timeout=5)
                self.monitor.update_status(name, "stopped")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"{name} did not terminate gracefully, forcing...")  # 경고로 변경
                process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping {name}: {str(e)}")  # 실제 에러는 ERROR로 유지
        self.logger.info("All processes stopped")  # INFO로 변경

def main():
    base_dir = Path(__file__).parent
    launcher = ProgramLauncher(base_dir)
    
    try:
        launcher.start_backend_services()
        time.sleep(5)  # 백엔드 서비스 안정화 대기
        
        while True:
            launcher.monitor.check_services()
            time.sleep(5)
            
    except KeyboardInterrupt:
        logging.info("Shutting down all services...")
        launcher.stop_all()
    except Exception as e:
        #logging.error(f"An error occurred: {str(e)}")
        launcher.stop_all()

if __name__ == "__main__":
    main()