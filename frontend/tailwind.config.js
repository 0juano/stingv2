/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: {
          DEFAULT: 'var(--card)',
          foreground: 'var(--card-foreground)'
        },
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)'
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)'
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)'
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)'
        },
        destructive: {
          DEFAULT: 'var(--destructive)',
          foreground: 'var(--destructive-foreground)'
        },
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
      },
      fontFamily: {
        sans: ['Oxanium', 'sans-serif'],
        mono: ['Source Code Pro', 'monospace'],
      },
      borderRadius: {
        none: '0px',
      },
      keyframes: {
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-2px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(2px)' },
        }
      },
      animation: {
        shake: 'shake 0.3s ease-in-out',
      }
    },
  },
  plugins: [],
  safelist: [
    // Background colors with opacity
    'bg-[#0a0a0a]',
    'bg-[#1a1a1a]',
    'bg-[#1E1E1E]/70',
    'bg-[#222]',
    'bg-[#2a2a2a]',
    'hover:bg-[#222]',
    'hover:bg-[#2a2a2a]',
    'active:bg-[#2a2a2a]',
    
    // Text colors
    'text-orange-500',
    'text-orange-600', 
    'text-gray-300',
    'text-gray-400',
    'text-gray-500',
    'text-gray-700',
    'text-emerald-400',
    'text-xs',
    'text-sm',
    'text-base',
    'text-[11px]',
    
    // Border colors
    'border-orange-500',
    'border-gray-700',
    'border-gray-800',
    'hover:border-orange-500/50',
    'focus-visible:outline-orange-500',
    
    // Layout classes
    'grid',
    'grid-cols-2',
    'gap-y-1',
    'gap-4',
    'min-h-dvh',
    'max-h-8',
    'h-16',
    'pb-6',
    
    // Background specific
    'bg-orange-600',
    'hover:bg-orange-700',
    'disabled:bg-gray-700',
    
    // Animation
    'animate-shake',
    
    // Positioning and spacing
    'px-6',
    'pt-8',
    'pb-6',
    'space-y-2',
    'space-y-4',
    
    // Flex utilities
    'flex',
    'flex-col',
    'flex-1',
    'items-center',
    'justify-center',
    'justify-between',
    
    // Mobile specific
    'md:max-w-xs',
    'md:mx-auto',
    'md:px-0',
    'md:bg-transparent',
    'md:text-3xl',
    'md:hidden',
    'block',
    'hidden',
    'md:block',
    
    // Other utilities
    'rounded-lg',
    'transition-all',
    'duration-200',
    'transform',
    'hover:scale-[1.02]',
    'active:scale-[0.98]',
    'disabled:scale-100',
    'focus:outline-none',
    'focus-visible:outline',
    'focus-visible:outline-2',
    'focus-visible:outline-offset-2',
    'disabled:opacity-50',
    
    // Mobile result screen
    'absolute',
    '-top-8',
    'inset-x-0',
    'text-center',
    'relative',
    'border-t',
    'mt-4',
    'pt-4',
    'ml-1'
  ]
}