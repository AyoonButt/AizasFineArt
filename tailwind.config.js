/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/src/js/**/*.js',
    './static/src/js/**/*.jsx',
  ],
  theme: {
    extend: {
      // Extend with our custom color palette to avoid conflicts
      colors: {
        'vintage-rosewood': '#9C6B68',
        'sea-glass': '#C5D6D2', 
        'pale-blush': '#F6ECEA',
        'mauve-plum': '#A38194',
        'mist-blue': '#DCE3E8',
        'deep-ash': '#2F2F2F',
        'primary': {
          DEFAULT: '#9C6B68',
          50: '#f6f2f2',
          100: '#ede4e3',
          200: '#dccdcc',
          300: '#c4a8a6',
          400: '#a8827f',
          500: '#9C6B68',
          600: '#85585a',
          700: '#6e484a',
          800: '#5c3e40',
          900: '#4f3739',
          950: '#2a1c1d'
        },
        'secondary': {
          DEFAULT: '#C5D6D2',
          50: '#f7faf9',
          100: '#eff5f3',
          200: '#deeae7',
          300: '#C5D6D2',
          400: '#a0bfba',
          500: '#80a5a0',
          600: '#698a85',
          700: '#57716e',
          800: '#495c5a',
          900: '#3f4d4c',
          950: '#22292a'
        },
        'surface': '#ffffff',
        'muted': '#DCE3E8',
      },
      fontFamily: {
        'body': ['Karla', 'sans-serif'],
        'heading': ['Georgia', 'serif'],
        'logo': ['Georgia', 'serif'],
        'decorative': ['Georgia', 'serif'],
      },
      fontSize: {
        'caption': '0.875rem',
      },
      boxShadow: {
        'soft': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'medium': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'strong': '0 10px 15px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
  // Safelist our custom section border classes so they don't get purged
  safelist: [
    'section-border-top',
    'section-border-bottom', 
    'section-border-both',
    'section-border-primary',
    'section-border-secondary',
    'section-border-muted',
    'section-border-accent',
  ],
  // Keep preflight enabled but we'll override in design-system.css
};