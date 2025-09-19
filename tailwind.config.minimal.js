/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/base.html',
    './templates/orders/order_detail_tracking.html',
    './static/dist/js/main.bundle.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};