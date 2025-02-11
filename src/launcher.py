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
        self.logger = setup_logger('service_monitor', None)
    
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
        self.services_ready: Dict[str, bool] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.monitor = ServiceMonitor()
        self.base_dir = Path(base_dir)
        self.logger = setup_logger('launcher', None)
        self.logger.setLevel(logging.ERROR)
        
        # logs 디렉토리 생성 (config.py의 LOGS_DIR 사용)
        LOGS_DIR.mkdir(exist_ok=True)
        
    def wait_for_services_ready(self, group, timeout):
        """서비스 그룹이 준비될 때까지 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            ready_count = 0
            for name, _ in group:
                if self.check_service_ready(name):
                    ready_count += 1
                else:
                    self.logger.debug(f"Still waiting for {name} to be ready... ({int(time.time() - start_time)}s elapsed)")
            
            if ready_count == len(group):
                self.logger.info(f"All services in group are ready: {[name for name, _ in group]}")
                return True
            
            time.sleep(2)  # 체크 간격 증가
            
        # 타임아웃 시 어떤 서비스가 준비되지 않았는지 상세히 기록
        not_ready = [name for name, _ in group if not self.check_service_ready(name)]
        self.logger.error(f"Timeout waiting for services. Not ready: {not_ready}")
        return False
        
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
        
        # 그룹별로 순차적 시작 및 준비 확인
        for i, group in enumerate(service_groups):
            self.logger.info(f"Starting service group {i+1}...")
            for name, command in group:
                self._start_process(name, command)
                self.monitor.update_status(name, "started")
                self.services_ready[name] = False  # Initialize readiness flag

            # Wait for services in the group to become ready
            timeout = 60 if 'Web Server' in str(group) else 30  # 웹 서버는 더 긴 타임아웃
            if not self.wait_for_services_ready(group, timeout=timeout):
                self.logger.error(f"Services in group {i+1} failed to start in time. Starting services were: {[name for name, _ in group]}")
                raise RuntimeError(f"Services in group {i+1} failed to start in time.")

            wait_time = 5
            self.logger.info(f"Waiting {wait_time} seconds before starting next group...")
            time.sleep(wait_time)
    
    def read_log_file(self, log_file):
        """여러 인코딩을 시도하여 로그 파일 읽기"""
        encodings = ['utf-8', 'cp949', 'euc-kr']
        
        for encoding in encodings:
            try:
                with open(log_file, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading log file: {e}")
                return None
                
        self.logger.error(f"Failed to read log file with any encoding: {log_file}")
        return None

    def check_service_ready(self, name):
        """서비스가 준비되었는지 확인"""
        # 프로세스가 실행 중인지 먼저 확인
        process = self.processes.get(name)
        if process is None or process.poll() is not None:
            self.logger.warning(f"Process check failed for {name}: process is {'None' if process is None else 'terminated'}")
            return False

        # Web Server나 Client는 즉시 준비 완료로 처리
        if 'Web Server' in name or 'Client' in name:
            if process.poll() is None:  # 프로세스가 실행 중이면
                self.services_ready[name] = True
                return True
            return False

        # Modbus 서버들에 대한 로그 파일 확인
        log_file = LOGS_DIR / f'{name.lower().replace(" ", "_")}.log'
        if log_file.exists():
            content = self.read_log_file(log_file)
            if content is None:
                return False
                
            if "Starting Modbus TCP" in content:
                self.logger.info(f"{name} is ready")
                self.services_ready[name] = True
                return True
            self.logger.warning(f"Modbus start message not found in {name} log")
        else:
            self.logger.warning(f"Log file not found for {name}: {log_file}")
        return False

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
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 인코딩 명시적 지정
                bufsize=1,
                universal_newlines=True,
                cwd=str(self.base_dir),
                env=env
            )
            
            # 비동기로 출력 읽기
            def log_output(pipe, is_error):
                try:
                    for line in iter(pipe.readline, ''):
                        # line이 이미 문자열인 경우 처리
                        if isinstance(line, str):
                            processed_line = line.strip()
                        else:
                            # bytes인 경우 디코딩
                            processed_line = line.decode('utf-8', errors='replace').strip()
                        
                        # 로깅 및 출력
                        print(processed_line)
                        if is_error and any(keyword in processed_line.lower() for keyword in ['error:', 'exception:', 'traceback:']):
                            self.logger.error(f"{name}: {processed_line}")
                        else:
                            self.logger.info(f"{name}: {processed_line}")
                    
                    # 파이프가 닫혔을 때
                    pipe.close()
                except Exception as e:
                    self.logger.error(f"Error in log_output for {name}: {e}")
                
            import threading
            threading.Thread(target=log_output, args=(process.stdout, False), daemon=True).start()
            threading.Thread(target=log_output, args=(process.stderr, True), daemon=True).start()
            
            self.processes[name] = process
            self.logger.info(f"{name} started with PID {process.pid}")
            
            # 프로세스 상태 확인
            if process.poll() is None:
                self.monitor.update_status(name, "running")
                time.sleep(1)
            else:
                self.logger.warning(f"{name} failed to start")
                self.monitor.update_status(name, "failed")
                
        except Exception as e:
            self.logger.error(f"Failed to start {name}: {str(e)}", exc_info=True)
            self.monitor.update_status(name, f"error: {str(e)}")
        
    def stop_all(self):
        """모든 프로세스 중지"""
        for name, process in self.processes.items():
            if process.poll() is not None:  # 이미 종료된 프로세스는 건너뜀
                continue
                
            self.logger.info(f"Stopping {name}...")
            try:
                # Windows의 경우 CTRL_BREAK_EVENT 사용
                if sys.platform == 'win32':
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    process.terminate()
                
                # 최대 10초 동안 정상 종료 대기
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"{name} did not respond to terminate signal, killing...")
                    try:
                        if sys.platform == 'win32':
                            # Windows에서 강제 종료
                            subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                        capture_output=True)
                        else:
                            process.kill()
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.logger.error(f"Failed to kill {name} (PID: {process.pid})")
                        continue
                
                self.monitor.update_status(name, "stopped")
                self.logger.info(f"{name} stopped successfully")

            except Exception as e:
                self.logger.error(f"Error stopping {name}: {str(e)}")
                self.monitor.update_status(name, f"stop error: {str(e)}")

        self.logger.info("All processes stopped")

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
        launcher.logger.info("Shutting down all services...")
        launcher.stop_all()
    except Exception as e:
        launcher.logger.error(f"An error occurred: {str(e)}")
        launcher.stop_all()

if __name__ == "__main__":
    main()