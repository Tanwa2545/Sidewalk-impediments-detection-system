'use client';

// app/page.tsx
import dynamic from 'next/dynamic';
import { useState, useMemo } from 'react';
import Sidebar from '@/components/ui/Sidebar';
import Lightbox from '@/components/ui/Lightbox';
import { MarkerData } from '@/src/data/markers';
// Import JSON data directly. Next.js handles JSON imports.
// Note: verify structure. If it's an array, good.
import markersDataRaw from '@/src/data/markers.json';

// Dynamically import Map with no SSR
const Map = dynamic(() => import('@/components/Map/Map'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400">
      Loading Map...
    </div>
  )
});

export default function Home() {
  const [filters, setFilters] = useState({
    obstacle: true,
    damage: true,
    critical: true,
    warning: true,
  });

  const [lightboxImage, setLightboxImage] = useState<string | null>(null);

  const markers = markersDataRaw as unknown as MarkerData[];

  const filteredMarkers = useMemo(() => {
    return markers.filter(marker => {
      // Severity Filtering
      if (marker.severity === 'CRITICAL' && !filters.critical) return false;
      if (marker.severity === 'WARNING' && !filters.warning) return false;

      // Type Filtering
      if (marker.type === 'OBSTACLE' && !filters.obstacle) return false;
      if (marker.type === 'SURFACE DAMAGE' && !filters.damage) return false;

      // Helper for mixed types or slightly different strings
      const isObstacle = marker.type.includes('OBSTACLE');
      const isDamage = marker.type.includes('SURFACE DAMAGE') || marker.type.includes('damage');

      // If specific type check above didn't catch it (e.g. strict string mismatch), try loose
      if (marker.type !== 'OBSTACLE' && isObstacle && !filters.obstacle) return false;
      if (marker.type !== 'SURFACE DAMAGE' && isDamage && !filters.damage) return false;

      return true;
    });
  }, [markers, filters]);

  return (
    <main className="relative w-full h-screen overflow-hidden">
      <Sidebar filters={filters} setFilters={setFilters} />
      <div className="w-full h-full absolute inset-0 z-0">
        <Map markers={filteredMarkers} onImageClick={setLightboxImage} />
      </div>

      {lightboxImage && (
        <Lightbox src={lightboxImage} onClose={() => setLightboxImage(null)} />
      )}
    </main>
  );
}
