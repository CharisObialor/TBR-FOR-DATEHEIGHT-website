import { defineConfig, transformWithOxc, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
  plugins: [
    react(),

    // Transform .js files containing JSX using OXC with lang="jsx".
    // Runs before vite:oxc (which sets lang="js" for .js files, causing OXC to reject JSX).
    {
      name: 'vite:fix-jsx-js',
      enforce: 'pre',
      async transform(code, id) {
        if (!id.endsWith('.js') || id.includes('node_modules')) return
        if (!/<\w/.test(code)) return
        try {
          const result = await transformWithOxc(code, id, {
            lang: 'jsx',
            jsx: { runtime: 'automatic', importSource: 'react' },
            sourcemap: true,
          })
          return {
            code: result.code,
            map: result.map,
            moduleType: 'js',
          }
        } catch {
          return
        }
      },
    },

    // Prevent vite:oxc from re-processing .js files (double transform).
    // The react plugin sets jsxRefreshInclude to /\.[tj]sx?$/ which matches .js,
    // but OXC then fails because it sets lang="js" internally. This override
    // restricts the refresh filter to only .jsx/.tsx files.
    {
      name: 'vite:fix-oxc-config',
      enforce: 'post',
      config() {
        return {
          oxc: {
            jsxRefreshInclude: /\.(m?[jt]sx)$/,
          },
        }
      },
    },
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://site.tbrsolutions.ng',
        changeOrigin: true,
        secure: false,
      },
      '/uploads': {
        target: 'https://site.tbrsolutions.ng',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  define: {
    'process.env.REACT_APP_GOOGLE_CLIENT_ID': JSON.stringify(env.REACT_APP_GOOGLE_CLIENT_ID || ''),
    'process.env.REACT_APP_BACKEND_URL': JSON.stringify(env.REACT_APP_BACKEND_URL || ''),
  },
  }
})
