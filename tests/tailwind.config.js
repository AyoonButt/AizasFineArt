/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/src/js/react/**/*.{js,jsx}',
    './static/dist/js/*.js',
    // Reduced scanning to essential directories only
  ],
  theme: {
    extend: {
      colors: {
        // Complete Sea Glass & Rosewood 6-Color Palette
        primary: {
          DEFAULT: '#9C6B68', // Vintage Rosewood (original)
          50: '#faf9f9',
          100: '#f4f1f1',
          200: '#e9e1e1',
          300: '#d6c9c8',
          400: '#b59490',
          500: '#9C6B68', // Base Vintage Rosewood
          600: '#8a5f5c',
          700: '#73504e',
          800: '#5f4341',
          900: '#4f3836',
          10: 'rgba(156, 107, 104, 0.1)',
          20: 'rgba(156, 107, 104, 0.2)',
        },
        secondary: {
          DEFAULT: '#C5D6D2', // Sea Glass
          50: '#f9fafa',
          100: '#f2f5f4',
          200: '#e5ebe9',
          300: '#d1dbd8',
          400: '#b8c8c4',
          500: '#C5D6D2', // Base Sea Glass
          600: '#a6b8b3',
          700: '#8b9c97',
          800: '#73827e',
          900: '#5e6b67',
          10: 'rgba(197, 214, 210, 0.1)',
          20: 'rgba(197, 214, 210, 0.2)',
        },
        // Full Palette Colors
        'pale-blush': {
          DEFAULT: '#F6ECEA',
          50: '#fefcfb',
          100: '#fdf7f5',
          200: '#F6ECEA', // Base
          300: '#f0e1dc',
          400: '#e8d3cc',
          500: '#dec0b6',
          600: '#d0a899',
          700: '#bc8c78',
          800: '#9d735e',
          900: '#7f5c49',
        },
        'mauve-plum': {
          DEFAULT: '#A38194', // Mauve Plum (original)
          50: '#faf9fa',
          100: '#f4f1f3',
          200: '#e8e1e6',
          300: '#d5c9d1',
          400: '#bea9b5',
          500: '#A38194', // Base Mauve Plum
          600: '#8e6d81',
          700: '#775a6c',
          800: '#634b59',
          900: '#523e49',
        },
        'mist-blue': {
          DEFAULT: '#DCE3E8',
          50: '#fcfdfd',
          100: '#f8fafb',
          200: '#f1f5f7',
          300: '#e6ecf0',
          400: '#DCE3E8', // Base
          500: '#c8d4db',
          600: '#b0c0ca',
          700: '#92a5b2',
          800: '#788a96',
          900: '#63737d',
        },
        'deep-ash': {
          DEFAULT: '#2F2F2F',
          50: '#f7f7f7',
          100: '#e3e3e3',
          200: '#c8c8c8',
          300: '#a4a4a4',
          400: '#818181',
          500: '#666666',
          600: '#515151',
          700: '#434343',
          800: '#383838',
          900: '#2F2F2F', // Base
        },
        // Semantic aliases
        surface: '#FEFCFA', // Warm White
        muted: '#DCE3E8', // Mist Blue for borders/subtle elements
        // Strategic text colors using palette colors
        'text-secondary': '#9C6B68', // Vintage rosewood for warm accent text (original)
        'text-muted': '#2F2F2F', // Deep ash for high contrast body text
      },
      fontFamily: {
        // Sea Glass & Rosewood Typography
        'logo': ['Nadeko', 'serif'], // Logo font
        'heading': ['Colton', 'serif'], // Headings
        'body': ['Karla', 'sans-serif'], // Body text
        'decorative': ['Baar Sophia', 'serif'], // Decorative accents
      },
      fontSize: {
        'display': ['4rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'h1': ['3rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        'h2': ['2.25rem', { lineHeight: '1.3' }],
        'h3': ['1.875rem', { lineHeight: '1.4' }],
        'h4': ['1.5rem', { lineHeight: '1.4' }],
        'h5': ['1.25rem', { lineHeight: '1.5' }],
        'h6': ['1.125rem', { lineHeight: '1.5' }],
        'body-lg': ['1.125rem', { lineHeight: '1.7' }],
        'body': ['1rem', { lineHeight: '1.7' }],
        'body-sm': ['0.875rem', { lineHeight: '1.6' }],
        'caption': ['0.75rem', { lineHeight: '1.5' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      maxWidth: {
        '8xl': '90rem',
        '9xl': '100rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-in-right': 'slideInRight 0.5s ease-out',
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backdropBlur: {
        'xs': '2px',
      },
      boxShadow: {
        'soft': '0 4px 20px rgba(0, 0, 0, 0.08)',
        'medium': '0 8px 30px rgba(0, 0, 0, 0.12)',
        'strong': '0 15px 40px rgba(0, 0, 0, 0.15)',
        'inner-soft': 'inset 0 2px 4px rgba(0, 0, 0, 0.06)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-subtle': 'linear-gradient(135deg, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
};