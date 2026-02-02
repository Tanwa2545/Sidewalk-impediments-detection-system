'use client';

// Map.tsx
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MarkerData } from '@/src/data/markers';
import MarkerPopup from './MarkerPopup';
import DistrictMask from './DistrictMask';

// Fix Leaflet Default Icon in Next.js
// Leaflet's default icon paths are often broken in bundlers without config.
// We will use custom DivIcons anyway, but good to know.

interface MapProps {
  markers: MarkerData[];
  onImageClick?: (imageUrl: string) => void;
}

// Function to create custom icons
const createCustomIcon = (type: string, severity: 'WARNING' | 'CRITICAL' | 'SAFE') => {
  // Colors
  const colorClass = severity === 'CRITICAL' ? 'bg-red-500' : severity === 'WARNING' ? 'bg-yellow-400' : 'bg-green-500';
  const shadowColor = severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.5)' : severity === 'WARNING' ? 'rgba(250, 204, 21, 0.5)' : 'rgba(34, 197, 94, 0.5)';

  // Icon content (using FontAwesome-like logic or just emoji/svg string for simplicity within DivIcon html)
  // For 'Obstacle' maybe a Block/Cone icon? For 'Damage' a crack?
  // User mentioned they will provide pictures later. For now, let's use generic shapes or emoji.
  // Or Lucide icons rendered to SVG string. 
  // Simplified: A colored pin with an inner icon.

  const iconHtml = `
    <div class="relative group">
      <div class="w-8 h-8 ${colorClass} rounded-full border-2 border-white shadow-lg flex items-center justify-center transform transition-transform duration-200 hover:scale-110" style="box-shadow: 0 4px 6px ${shadowColor}">
        <div class="w-2 h-2 bg-white rounded-full"></div>
      </div>
      <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-white rotate-45 transform origin-center border-r border-b border-gray-200"></div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-map-marker', // we'll ensure this class has no default styles interfere
    html: iconHtml,
    iconSize: [32, 32],
    iconAnchor: [16, 32], // Pointing at bottom center
    popupAnchor: [0, -32],
  });
};

const MapController = ({ markers }: { markers: MarkerData[] }) => {
  const map = useMap();

  useEffect(() => {
    if (markers.length > 0) {
      const group = new L.FeatureGroup(
        markers.map((m) => L.marker([m.lat, m.lng]))
      );
      map.fitBounds(group.getBounds().pad(0.1));
    }
  }, [map, markers]);

  return null;
};

export default function Map({ markers, onImageClick }: MapProps) {
  // Bangkok Center Fallback
  const defaultCenter: [number, number] = [13.7563, 100.5018];

  return (
    <MapContainer
      center={defaultCenter}
      zoom={12}
      className="w-full h-full z-0"
      zoomControl={false} // We can add custom position
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Zoom Control at bottom right usually looks better with overlay sidebars */}
      <DistrictMask />


      {markers.map((marker, idx) => (
        <Marker
          key={marker.id || idx}
          position={[marker.lat, marker.lng]}
          icon={createCustomIcon(marker.type, marker.severity)}
        >
          <Popup className="custom-popup">
            <MarkerPopup marker={marker} onImageClick={onImageClick} />
          </Popup>
        </Marker>
      ))}

      <MapController markers={markers} />
    </MapContainer>
  );
}
