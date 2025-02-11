<template>
  <div class="stocker-warp">
    <div class="content-box" @click="$emit('stockView')">
      <div class="stocker-top">
        <span class="title">Stocker</span>
        <span class="stocker-id">{{ stockerData.id }}</span>
      </div>
      <div class="stocker-body">
        <div class="stocker-l">
          <ul class="list">
            <li class="title" :class="`state${stockerData.a.state}`">A</li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="WF6"
                v-model="stockerData.a.wf6"
              />
            </li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="Able"
                v-model="stockerData.a.able"
              />
            </li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="RESERVED"
                v-model="stockerData.a.reserved1"
              />
            </li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="RESERVED"
                v-model="stockerData.a.reserved2"
              />
            </li>
          </ul>
        </div>
        <div class="stocker-r">
          <ul class="list">
            <li class="title" :class="`state${stockerData.b.state}`">B</li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="CFO"
                v-model="stockerData.b.cfo"
              />
            </li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="Unable"
                v-model="stockerData.b.unable"
              />
            </li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="RESERVED"
                v-model="stockerData.b.reserved1"
              />
            </li>
            <li class="row">
              <input
                type="text"
                readonly
                placeholder="RESERVED"
                v-model="stockerData.b.reserved1"
              />
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div
      class="agv-wrap stocker"
      :class="[agvData.stockerPort, `state${agvData.state}`]"
      v-if="agvData.position === 'stocker'"
      @click="$emit('agvView')"
    ></div>
  </div>
</template>

<script setup>
import { toRefs } from 'vue';

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
  agvData: {
    type: Object,
    default: () => ({}),
  },
});

const { data: stockerData } = toRefs(props);
</script>
