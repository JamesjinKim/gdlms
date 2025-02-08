<template>
  <div id="app" class="monitoring-container">
    <div class="device-monitors">
      <div class="monitor stocker-monitor">
        <h2>Stocker Monitor</h2>
        <StockerMonitor />
      </div>
      <div class="monitor gas-cabinet-monitor">
        <h2>Gas Cabinet Monitor</h2>
        <GasCabinetMonitor />
      </div>
    </div>
  </div>
</template>

<script>
import StockerMonitor from './components/StockerMonitor.vue'
import GasCabinetMonitor from './components/GasCabinetMonitor.vue'

export default {
  name: 'App',
  components: {
    StockerMonitor,
    GasCabinetMonitor
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  padding: 20px;
}

.monitoring-container {
  max-width: 1600px;
  margin: 0 auto;
}

.device-monitors {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.monitor {
  flex: 1;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.monitor h2 {
  margin-bottom: 20px;
  color: #333;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.stocker-monitor, 
.gas-cabinet-monitor {
  max-width: 100%;
}

@media (max-width: 1200px) {
  .device-monitors {
    flex-direction: column;
  }
}
</style>