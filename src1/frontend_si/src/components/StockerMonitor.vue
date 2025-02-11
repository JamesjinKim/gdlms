<template>
    <div class="stocker-monitor">
      <div class="connection-status">
        연결 상태: 
        <span :class="{'connected': isConnected, 'disconnected': !isConnected}">
          {{ connectionStatus }}
        </span>
      </div>
      
      <div v-if="alarm" class="alarm-section">
        <h3>알람</h3>
        <div class="alarm-message">
          {{ alarm }}
        </div>
      </div>

      <div v-if="currentData" class="data-display">
        <h2>Stocker 데이터</h2>
        
        <div class="plc-data">
          <h3>PLC 데이터</h3>
          <pre>{{ JSON.stringify(currentData.plc_data, null, 2) }}</pre>
        </div>
  
        <div class="bit-data">
          <h3>비트 데이터</h3>
          <pre>{{ JSON.stringify(currentData.bit_data, null, 2) }}</pre>
        </div>
      </div>

    </div>
  </template>
  
  <script>
    export default {
      name: 'StockerMonitor',
      data() {
        return {
          socket: null,
          isConnected: false,
          connectionStatus: '연결 대기중...',
          currentData: null,
          alarm: null,
          heartbeatInterval: null,
          reconnectAttempts: 0
        }
      },
      mounted() {
        window.addEventListener('online', this.handleNetworkChange)
        window.addEventListener('offline', this.handleNetworkChange)
        this.connectWebSocket()
      },
      methods: {
        handleNetworkChange(event) {
          console.log('네트워크 상태 변경:', event.type)
          if (event.type === 'online') {
            this.connectWebSocket()
          }
        },

        startHeartbeat() {
          this.heartbeatInterval = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
              this.socket.send('ping')
            }
          }, 30000)
        },

        cleanupWebSocket() {
          if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval)
          }
          if (this.socket) {
            this.socket.onclose = null
            this.socket.onerror = null
            this.socket.onmessage = null
            this.socket.close()
            this.socket = null
          }
        },

        connectWebSocket() {
          if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
            console.log('기존 연결 종료!')
            this.cleanupWebSocket()
          }

          console.log('WebSocket 연결 시도...')
          
          try {
            this.socket = new WebSocket('ws://127.0.0.1:5100/ws/stocker')
            console.log('초기 WebSocket 상태:', this.socket.readyState)
            
            this.socket.onopen = () => {
              console.log('WebSocket 연결 성공, 상태:', this.socket.readyState)
              this.isConnected = true
              this.connectionStatus = '연결됨'
              this.reconnectAttempts = 0
              this.startHeartbeat()
            }

            this.socket.onmessage = (event) => {
              try {
                const data = JSON.parse(event.data)
                
                // 서버에서 보내는 연결 상태 확인 메시지 처리 (옵션)
                if (data.type === 'server_status') {
                  if (data.status === 'disconnecting') {
                    console.log('서버에서 연결 종료 신호')
                    this.cleanupWebSocket()
                    return
                  }
                }

                if (!data || !data.plc_data) {
                  console.error('잘못된 데이터 형식:', data)
                  return
                }

                if (JSON.stringify(this.currentData) !== JSON.stringify(data)) {
                  this.currentData = data
                }

                const alarmCode = data.plc_data.status?.alarm_code
                if (alarmCode > 0) {
                  this.alarm = data.plc_data.status.alarm_message
                } else {
                  this.alarm = null
                }
              } catch (error) {
                console.error('데이터 파싱 오류:', error)
                console.log('받은 데이터:', event.data)
              }
            }

            this.socket.onclose = (event) => {
              console.log('WebSocket 닫힘. 코드:', event.code, '이유:', event.reason)
              this.isConnected = false
              this.connectionStatus = '연결 끊김'

              // 서버 측 강제 종료 감지
              if (event.code === 1006) {  // 비정상 종료
                console.error('서버 측 연결 종료 감지')
                this.alarm = '서버 연결이 종료되었습니다.'
              }
              
              if (this.reconnectAttempts < 5) {
                this.reconnectAttempts++
                const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000)
                console.log(`재연결 시도 ${this.reconnectAttempts}/5, ${delay}ms 후 시도`)
                setTimeout(() => {
                  this.connectWebSocket()
                }, delay)
              } else {
                this.connectionStatus = '재연결 실패'
                this.alarm = '서버와의 연결을 복구할 수 없습니다.'
              }
            }

            this.socket.onerror = (error) => {
              console.error('WebSocket 오류:', error)
              this.isConnected = false
              this.connectionStatus = '연결 오류'
              this.alarm = '서버 연결 중 오류가 발생했습니다.'
            }
          } catch (error) {
            console.error('WebSocket 초기화 오류:', error)
            this.connectionStatus = '연결 초기화 실패'
            this.alarm = '웹소켓 연결을 초기화할 수 없습니다.'
          }
        }
      },
      beforeUnmount() {
        window.removeEventListener('online', this.handleNetworkChange)
        window.removeEventListener('offline', this.handleNetworkChange)
        this.cleanupWebSocket()
      }
    }
  </script>
  
  <style scoped>
  .stocker-monitor {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .connection-status {
    margin-bottom: 15px;
    font-weight: bold;
  }
  
  .connected {
    color: green;
  }
  
  .disconnected {
    color: red;
  }
  
  .data-display {
    background-color: #f4f4f4;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 15px;
  }
  
  .alarm-section {
    background-color: #ffdddd;
    border: 1px solid #ff0000;
    padding: 10px;
    border-radius: 5px;
  }
  
  pre {
    background-color: #e7e7e7;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
  }
  </style>