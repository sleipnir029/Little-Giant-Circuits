import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  // serve learn_data/ from the project root as static assets
  publicDir: path.resolve(__dirname, '../..'),
  server: {
    fs: {
      allow: [path.resolve(__dirname, '../..')],
    },
  },
})
