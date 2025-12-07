/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Coastal New England color palette
        marsh: {
          50: '#f6f7f4',
          100: '#e8ebe3',
          200: '#d4daca',
          300: '#b5c0a6',
          400: '#94a37f',
          500: '#768762',
          600: '#5d6b4d',
          700: '#4a5540',
          800: '#3d4636',
          900: '#343b2f',
        },
        sea: {
          50: '#f2f7f9',
          100: '#ddeaf0',
          200: '#bfd6e3',
          300: '#92b8cf',
          400: '#5e93b4',
          500: '#447799',
          600: '#3a6180',
          700: '#335069',
          800: '#2f4558',
          900: '#2b3b4b',
        },
        sand: {
          50: '#faf9f7',
          100: '#f3f1ec',
          200: '#e6e1d6',
          300: '#d5ccba',
          400: '#c1b49a',
          500: '#b0a080',
          600: '#9f8c6a',
          700: '#857359',
          800: '#6d5e4b',
          900: '#5a4e40',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', '"Times New Roman"', 'Times', 'serif'],
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '65ch',
            color: '#374151',
            p: {
              marginTop: '1.25em',
              marginBottom: '1.25em',
            },
          },
        },
      },
    },
  },
  plugins: [],
}
