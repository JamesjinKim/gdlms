<template>
    <div class="gas-cabinet-monitor">
      <div class="connection-status">
        연결 상태: 
        <span :class="{'connected': isConnected, 'disconnected': !isConnected}">
          {{ connectionStatus }}
        </span>
      </div>
  
      <div v-if="currentData" class="data-display">
        <h2>Gas Cabinet 데이터</h2>
        
        <div class="plc-data">
          <h3>PLC 데이터</h3>
          <pre>{{ JSON.stringify(currentData.plc_data, null, 2) }}</pre>
        </div>
  
        <div class="bit-data">
          <h3>비트 데이터</h3>
          <pre>{{ JSON.stringify(currentData.bit_data, null, 2) }}</pre>
        </div>
      </div>
  
      <div v-if="alarm" class="alarm-section">
        <h3>알람</h3>
        <div class="alarm-message">
          {{ alarm }}
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'GasCabinetMonitor',
    data() {
      return {
        socket: null,
        isConnected: false,
        connectionStatus: '연결 대기중...',
        currentData: null,
        alarm: null
      }
    },
    mounted() {
      this.connectWebSocket()
    },
    methods: {
      connectWebSocket() {
        // WebSocket 연결 (백엔드 WebSocket 주소)
        this.socket = new WebSocket('ws://localhost:5001/ws/gas')
  
        this.socket.onopen = () => {
          this.isConnected = true
          this.connectionStatus = '연결됨'
          console.log('WebSocket 연결 성공')
        }
  
        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.currentData = data
  
            // 알람 처리
            const alarmCode = data.plc_data.status.alarm_code
            if (alarmCode > 0) {
              this.alarm = data.plc_data.status.alarm_message
            } else {
              this.alarm = null
            }
          } catch (error) {
            console.error('데이터 파싱 오류:', error)
          }
        }
  
        this.socket.onclose = () => {
          this.isConnected = false
          this.connectionStatus = '연결 끊김'
          console.log('WebSocket 연결 종료')
          
          // 자동 재연결 로직
          setTimeout(() => {
            this.connectWebSocket()
          }, 3000)
        }
  
        this.socket.onerror = (error) => {
          console.error('WebSocket 오류:', error)
          this.isConnected = false
          this.connectionStatus = '연결 오류'
        }
      }
    },
    beforeUnmount() {
      // 컴포넌트 언마운트 시 WebSocket 연결 종료
      if (this.socket) {
        this.socket.close()
      }
    }
  }
  </script>
  
  <style scoped>
  .gas-cabinet-monitor {
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