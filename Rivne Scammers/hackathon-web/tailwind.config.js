/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      keyframes: {
        blob: {
          '0%': { transform: 'translate(0px,0px) scale(1)' },
          '25%': { transform: 'translate(40px,-30px) scale(1.15)' },
          '50%': { transform: 'translate(-20px,20px) scale(0.95)' },
          '75%': { transform: 'translate(-50px,10px) scale(1.05)' },
          '100%': { transform: 'translate(0px,0px) scale(1)' },
        },
        gradientFlow: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        marqueeRL: {
          '0%': { transform: 'translateX(-50%)' },
          '100%': { transform: 'translateX(0)' },
        },
        marqueeLTR: {
          '0%': { transform: 'translateX(-50%)' },
          '100%': { transform: 'translateX(0)' },
        },
      },
      animation: {
        blob: 'blob 18s linear infinite',
        blobSlow: 'blob 28s linear infinite',
        gradient: 'gradientFlow 6s ease-in-out infinite',
        marquee: 'marquee 25s linear infinite',
        'marquee-slow': 'marquee 45s linear infinite',
        'marquee-rl-slow': 'marqueeRL 45s linear infinite',
        'marquee-ltr-slow': 'marqueeLTR 45s linear infinite',
      },
    },
  },
  plugins: [],
}
