import { useEffect, useState } from 'react';

/**
 * Hook to detect virtual keyboard height using the VisualViewport API
 * Returns the keyboard height in pixels (0 when keyboard is closed)
 */
export function useKeyboardHeight() {
  const [kbHeight, setKbHeight] = useState(0);

  useEffect(() => {
    const vp = window.visualViewport;
    if (!vp) {
      // Fallback: no visualViewport support
      console.warn('VisualViewport API not supported');
      return;
    }

    const handler = () => {
      // Calculate keyboard height based on viewport offset
      const height = Math.max(0, vp.offsetTop || 0);
      setKbHeight(height);
    };

    // Listen for viewport changes (keyboard open/close)
    vp.addEventListener('resize', handler);
    vp.addEventListener('scroll', handler);
    
    // Initial calculation
    handler();

    return () => {
      vp.removeEventListener('resize', handler);
      vp.removeEventListener('scroll', handler);
    };
  }, []);

  return kbHeight;
}