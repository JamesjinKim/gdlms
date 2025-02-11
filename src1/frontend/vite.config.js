import { fileURLToPath, URL } from 'node:url';
// import Components from "unplugin-vue-components/vite";

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
// import visualizer from 'rollup-plugin-visualizer';

export default defineConfig({
  // build: {
  //   outDir: '../testing/dist',
  // },
  server: {
    port: '8888',
    overlay: false,
  },
  base: './',
  // mode: 'development',
  plugins: [
    vue(),
    // visualizer({ open: true }),
    // Components({
    //   dirs: ["src/components/app"],
    //   dts: true,
    // }),
  ],
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
  },
  css: {
    devSourcemap: true,
  },
  productionSourceMap: false,
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue')) {
              return 'vendor-vue';
            }
            if (id.includes('ag-grid')) {
              return 'vendor-agGrid';
            }
            if (id.includes('apexcharts')) {
              return 'vendor-apexcharts';
            }
            return 'vendor';
          }
        },
      },
    },
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia'],
    exclude: ['some-heavy-library'],
  },
});
