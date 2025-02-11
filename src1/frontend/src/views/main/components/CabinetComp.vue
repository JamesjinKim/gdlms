<template>
  <div class="cabinet-grid">
    <div
      class="cabinet-item"
      v-for="(item, index) in cabinetData"
      :key="item.id"
      :class="[
        getCabinetClass(index),
        `cabinet${item.id}`,
        {
          active:
            agvData.position === 'cabinet' && agvData.cabinetId == item.id,
        },
      ]"
    >
      <div class="content-box" @click="$emit('cabinetView', item.id)">
        <div class="cabinet-top">
          <span class="title">{{ item.id }}</span>
          <span class="cabinet-id">{{ item.type }}</span>
        </div>
        <div class="cabinet-body">
          <div class="cabinet-l">
            <ul class="list">
              <li class="title" :class="`state${item.a.state}`">A</li>
              <li class="row row2">
                <input
                  type="text"
                  readonly
                  placeholder="PT2A"
                  v-model="item.a.pt2a"
                />
                <input
                  type="text"
                  readonly
                  placeholder="PT1A"
                  v-model="item.a.pt1a"
                />
              </li>
              <li class="row">
                <input
                  type="text"
                  readonly
                  placeholder="WA"
                  v-model="item.a.wa"
                />
              </li>
              <li class="row row3">
                <input
                  type="text"
                  readonly
                  placeholder="[A]LINE HEATER"
                  v-model="item.a.lineHeater"
                />
                <input
                  type="text"
                  readonly
                  placeholder="[A]JACKET"
                  v-model="item.a.jacket"
                />
                <input
                  type="text"
                  readonly
                  placeholder="HEATER"
                  v-model="item.a.heater"
                />
              </li>
              <li class="row">
                <input
                  type="text"
                  readonly
                  placeholder="RESERVED"
                  v-model="item.a.reserved"
                />
              </li>
            </ul>
          </div>
          <div class="cabinet-r">
            <ul class="list">
              <li class="title" :class="`state${item.b.state}`">B</li>
              <li class="row row2">
                <input
                  type="text"
                  readonly
                  placeholder="PT2B"
                  v-model="item.b.pt2b"
                />
                <input
                  type="text"
                  readonly
                  placeholder="PT1B"
                  v-model="item.b.pt1b"
                />
              </li>
              <li class="row">
                <input
                  type="text"
                  readonly
                  placeholder="WB"
                  v-model="item.b.wb"
                />
              </li>
              <li class="row row3">
                <input
                  type="text"
                  readonly
                  placeholder="[A]LINE HEATER"
                  v-model="item.b.lineHeater"
                />
                <input
                  type="text"
                  readonly
                  placeholder="[A]JACKET"
                  v-model="item.b.jacket"
                />
                <input
                  type="text"
                  readonly
                  placeholder="HEATER"
                  v-model="item.b.heater"
                />
              </li>
              <li class="row">
                <input
                  type="text"
                  readonly
                  placeholder="RESERVED"
                  v-model="item.b.reserved"
                />
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div
        class="agv-wrap cabinet"
        :class="[agvData.cabinetPort, `state${agvData.state}`]"
        v-if="agvData.position === 'cabinet' && agvData.cabinetId == item.id"
        @click="$emit('agvView')"
      ></div>
    </div>
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

const { data: cabinetData } = toRefs(props);

const getCabinetClass = index => {
  const itemNumber = index + 1;
  if (itemNumber < 7) return;
  if ((itemNumber - 7) % 18 < 6) {
    return 'top';
  } else if ((itemNumber - 13) % 18 < 6) {
    return 'bottom';
  }
  return '';
};
</script>
