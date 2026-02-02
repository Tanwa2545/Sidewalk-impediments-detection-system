'use client';

import React from 'react';
import { ExternalLink, Calendar, AlertCircle } from 'lucide-react';
import { MarkerData } from '@/src/data/markers'; // Adjust import if needed

interface MarkerPopupProps {
  marker: MarkerData;
  onImageClick?: (imageUrl: string) => void;
}

export default function MarkerPopup({ marker, onImageClick }: MarkerPopupProps) {
  // Google Street View Link Construction
  // https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=Lat,Lng&pano=PanoID&heading=Heading
  // OR just coordinates if PanoID is tricky, but we have PanoID!
  // Fallback to simple maps link: https://www.google.com/maps/search/?api=1&query=Lat,Lng

  // Street view link is best for "fixing" context.
  const googleMapsLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${marker.lat},${marker.lng}&pano=${marker.panoId}&heading=${marker.heading}&pitch=-15`;

  return (
    <div className="w-64 p-1">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-gray-800 text-sm">{marker.type}</h3>
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${marker.severity === 'CRITICAL' ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'
          }`}>
          {marker.severity}
        </span>
      </div>

      {/* Image Thumbnail */}
      <div
        className="relative w-full h-32 bg-gray-100 rounded-lg overflow-hidden mb-3 border border-gray-200 group cursor-zoom-in"
        onClick={() => onImageClick?.(marker.image)}
      >
        {/* We use standard img for Leaflet popups usually, Next/Image can be tricky inside Leaflet portals */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={marker.image}
          alt={marker.type}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
      </div>

      {/* Details */}
      <div className="space-y-3 text-sm text-gray-700"> {/* Increased font size */}
        <p className="line-clamp-3 leading-relaxed">{marker.description}</p>

        {/* Date Note */}
        {marker.dateNote && (
          <div className="flex items-start bg-orange-50 p-2 rounded-md border border-orange-100 text-orange-800">
            <Calendar size={14} className="mt-0.5 mr-2 shrink-0" />
            <span className="text-xs leading-snug font-medium">{marker.dateNote}</span>
          </div>
        )}

        {/* Link */}
        <a
          href={googleMapsLink}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center w-full py-2.5 mt-3 bg-blue-600 hover:bg-blue-700 !text-white text-sm font-semibold rounded-lg transition-colors shadow-sm"
        >
          Open Street View <ExternalLink size={14} className="ml-2 text-white" />
        </a>
      </div>
    </div>
  );
}
