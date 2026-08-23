/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E40AF',
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#1E40AF',
          600: '#1E3A8A',
          700: '#1E3078',
          800: '#1B2D6B',
          900: '#172554',
        },
        secondary: {
          DEFAULT: '#059669',
          50: '#ECFDF5',
          100: '#D1FAE5',
          400: '#34D399',
          500: '#059669',
          600: '#047857',
        },
        accent: {
          DEFAULT: '#F97316',
          50: '#FFF7ED',
          100: '#FFEDD5',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
        },
        success: '#16A34A',
        warning: '#D97706',
        danger: '#DC2626',
      },
      fontFamily: {
        sans: ['Inter', 'Manrope', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
  ],
}
