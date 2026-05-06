export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        bg:       '#060910',
        surface:  '#0d1117',
        card:     '#111827',
        border:   '#1e2d3d',
        cyan:     '#00d4ff',
        green:    '#00ff9d',
        red:      '#ff3864',
        orange:   '#ff6b35',
        yellow:   '#f59e0b',
        blue:     '#4cc9f0',
        violet:   '#7c3aed',
        muted:    '#4b6277',
        'muted-2': '#2d4356',
      },
      fontFamily: {
        display: ['Rajdhani', 'sans-serif'],
        mono:    ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans:    ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-cyan':   'pulse-cyan 2.5s ease-in-out infinite',
        'pulse-red':    'pulse-red 2s ease-in-out infinite',
        'scan-line':    'scan-line 4s linear infinite',
        'radar':        'radar 3s linear infinite',
        'flicker':      'flicker 0.15s ease-in-out 2',
        'slide-up':     'slide-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards',
        'slide-right':  'slide-right 0.4s cubic-bezier(0.16,1,0.3,1) forwards',
        'fade-in':      'fade-in 0.3s ease forwards',
        'counter':      'counter 1s ease-out forwards',
        'blink':        'blink 1s step-end infinite',
        'shimmer':      'shimmer 2s linear infinite',
      },
      keyframes: {
        'pulse-cyan': {
          '0%,100%': { boxShadow: '0 0 0 0 rgba(0,212,255,0.5), 0 0 15px rgba(0,212,255,0.1)' },
          '50%':     { boxShadow: '0 0 0 10px rgba(0,212,255,0), 0 0 30px rgba(0,212,255,0.2)' },
        },
        'pulse-red': {
          '0%,100%': { boxShadow: '0 0 0 0 rgba(255,56,100,0.5)' },
          '50%':     { boxShadow: '0 0 0 10px rgba(255,56,100,0)' },
        },
        'scan-line': {
          '0%':   { top: '-2px', opacity: '0' },
          '5%':   { opacity: '1' },
          '95%':  { opacity: '1' },
          '100%': { top: '100%', opacity: '0' },
        },
        'radar': {
          '0%':   { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'flicker': {
          '0%,100%': { opacity: '1' },
          '50%':     { opacity: '0.3' },
        },
        'slide-up': {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-right': {
          '0%':   { opacity: '0', transform: 'translateX(-16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'fade-in': {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'blink': {
          '0%,100%': { opacity: '1' },
          '50%':     { opacity: '0' },
        },
        'shimmer': {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)",
        'hex-pattern':  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='49'%3E%3Cpath d='M14 0 L28 8.1 L28 24.3 L14 32.4 L0 24.3 L0 8.1Z' fill='none' stroke='rgba(0,212,255,0.04)' stroke-width='1'/%3E%3C/svg%3E\")",
        'noise':        "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E\")",
      },
      boxShadow: {
        'glow-cyan':  '0 0 20px rgba(0,212,255,0.2), 0 0 60px rgba(0,212,255,0.05)',
        'glow-red':   '0 0 20px rgba(255,56,100,0.2), 0 0 60px rgba(255,56,100,0.05)',
        'glow-green': '0 0 20px rgba(0,255,157,0.2)',
        'card':       '0 4px 24px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.03) inset',
        'panel':      '0 8px 48px rgba(0,0,0,0.6)',
      },
    },
  },
  plugins: [],
}
