import subprocess
import time
import os
import sys
import signal
import logging
from typing import List, Dict
from pathlib import Path
from datetime import datetime
import webbrowser

class ServiceMonitor:
    def __init__(self):
        self.service_status = {}
    
    def update_status(self, service_name: str, status: str):
        self.service_status[service_name] = {
            'status': status,
            'last_update': datetime.now()
        }
    
    def check_services(self):
        current_time = datetime.now()
        for service, info in self.service_status.items():
            if (current_time - info['last_update']).seconds > 30:
                logging.warning(f"{service} 응답 없음: {info['status']}")

class ProgramLauncher:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.monitor = ServiceMonitor()
        
        # logs 디렉토리 생성
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'launcher.log'),
                logging.StreamHandler()
            ]
        )
        
    def start_backend_services(self):
        """백엔드 서비스 시작"""
        service_groups = [
            # 그룹 1: 기본 서버들 (5초 대기)
            [
                ("Stocker Server", ["python", "backend/stocker/stocker_async_server.py"]),
                ("Gas Cabinet Server", ["python", "backend/gas_cabinet/gas_async_server.py"]),
            ],
            # 그룹 2: 웹 서버들 (5초 대기)
            [
                ("Stocker Web Server", ["python", "backend/stocker/stocker_web_server.py"]),
                ("Gas Cabinet Web Server", ["python", "backend/gas_cabinet/gas_web_server.py"]),
            ],
            # 그룹 3: 클라이언트들
            [
                ("Stocker Client", ["python", "backend/stocker/stocker_async_client.py"]),
                ("Gas Cabinet Client1", ["python", "backend/gas_cabinet/gas_async_client1.py"]),
                ("Gas Cabinet Client2", ["python", "backend/gas_cabinet/gas_async_client2.py"]),
                ("Gas Cabinet Client3", ["python", "backend/gas_cabinet/gas_async_client3.py"]),
            ]
        ]
        
        # 그룹별로 순차적 시작
        for i, group in enumerate(service_groups):
            logging.info(f"Starting service group {i+1}...")
            for name, command in group:
                self._start_process(name, command)
                self.monitor.update_status(name, "started")
                time.sleep(3)  # 각 프로세스 사이에 3초 간격
            
            # 그룹별 대기 시간 설정
            wait_time = 5
            logging.info(f"Waiting {wait_time} seconds before starting next group...")
            time.sleep(wait_time)
    
    def _start_process(self, name: str, command: List[str]):
        try:
            logging.info(f"Starting {name}...")
            
            # 각 서비스별 로그 파일 설정
            log_file = self.base_dir / 'logs' / f'{name.lower().replace(" ", "_")}.log'
            
            with open(log_file, 'a') as f:
                process = subprocess.Popen(
                    command,
                    stdout=f,
                    stderr=f,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
            
            self.processes[name] = process
            logging.info(f"{name} started successfully")
            
            # 프로세스 상태 확인
            if process.poll() is None:
                self.monitor.update_status(name, "running")
            else:
                logging.error(f"{name} failed to start")
                self.monitor.update_status(name, "failed")
                
        except Exception as e:
            logging.error(f"Failed to start {name}: {str(e)}")
            self.monitor.update_status(name, f"error: {str(e)}")
        
    def stop_all(self):
        """모든 프로세스 중지"""
        for name, process in self.processes.items():
            logging.info(f"Stopping {name}...")
            try:
                if sys.platform == 'win32':
                    process.send_signal(signal.CTRL_C_EVENT)
                else:
                    process.terminate()
                process.wait(timeout=5)
                self.monitor.update_status(name, "stopped")
            except subprocess.TimeoutExpired:
                logging.warning(f"{name} did not terminate gracefully, forcing...")
                process.kill()
            except Exception as e:
                logging.error(f"Error stopping {name}: {str(e)}")
        logging.info("All processes stopped")

def main():
    base_dir = Path(__file__).parent
    launcher = ProgramLauncher(base_dir)
    
    try:
        launcher.start_backend_services()
        time.sleep(5)  # 백엔드 서비스 안정화 대기
        
        while True:
            launcher.monitor.check_services()
            time.sleep(10)
            
    except KeyboardInterrupt:
        logging.info("Shutting down all services...")
        launcher.stop_all()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        launcher.stop_all()

if __name__ == "__main__":
    main()