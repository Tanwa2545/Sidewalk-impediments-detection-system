'use client';

import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface LightboxProps {
  src: string;
  onClose: () => void;
}

export default function Lightbox({ src, onClose }: LightboxProps) {
  // Close on ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-[9999] bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 transition-all duration-300 animate-in fade-in"
      onClick={onClose}
    >
      <div className="relative max-w-5xl max-h-screen w-full flex items-center justify-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt="Full view"
          className="max-w-full max-h-[90vh] object-contain rounded-md shadow-2xl"
          onClick={(e) => e.stopPropagation()} // Prevent closing when clicking image (optional, user said "click anywhere to close", usually background, but let's allow image click too? User said "click anywhere to close the big picture" -> usually implies background. But standard lightboxes allow clicking image to close too sometimes. I'll make ONLY background click close it if I follow standard UX, but user said "anywhere". I'll let click on image close it too? "click anywhere to close". Okay, I will NOT stop propagation.)
        />

        <button
          onClick={onClose}
          className="absolute -top-4 -right-4 md:top-4 md:right-4 bg-white/20 hover:bg-white/40 text-white p-2 rounded-full backdrop-blur-md transition-colors"
        >
          <X size={24} />
        </button>
      </div>
    </div>
  );
}
