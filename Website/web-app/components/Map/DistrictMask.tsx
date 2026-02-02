'use client';

import { useEffect, useState } from 'react';
import { Polygon, useMap } from 'react-leaflet';
import osmtogeojson from 'osmtogeojson';
import L from 'leaflet';

export default function DistrictMask() {
  const map = useMap();
  const [maskData, setMaskData] = useState<any[]>([]);

  useEffect(() => {
    const fetchDistricts = async () => {
      // Chatuchak, Lat Phrao, Phaya Thai
      // Admin Level 7 or 8. BKK district is Khet (admin_level=7).
      const query = `
        [out:json][timeout:25];
        (
          // Chatuchak
          relation["name:en"="Chatuchak"]["boundary"="administrative"];
          relation["name"="เขตจตุจักร"]["boundary"="administrative"];
          
          // Lat Phrao
          relation["name:en"="Lat Phrao"]["boundary"="administrative"];
          relation["name"="เขตลาดพร้าว"]["boundary"="administrative"];
          
          // Phaya Thai
          relation["name:en"="Phaya Thai"]["boundary"="administrative"];
          relation["name"="เขตพญาไท"]["boundary"="administrative"];
        );
        out geom;
      `;

      try {
        const response = await fetch('https://overpass-api.de/api/interpreter', {
          method: 'POST',
          body: query
        });

        const text = await response.text();
        let data;
        try {
          data = JSON.parse(text);
        } catch (e) {
          console.error("Overpass Error:", text.substring(0, 100)); // Log first 100 chars of error
          return;
        }

        if (data && data.elements) {
          console.log(`Overpass: Found ${data.elements.length} elements.`);
        }

        const geojson = osmtogeojson(data) as any;

        // Inverted Polygon Logic (Masking)
        // 1. Create a huge polygon covering the world
        // 2. Subtract the district polygons (holes)

        const worldCoords = [
          [90, -180],
          [90, 180],
          [-90, 180],
          [-90, -180]
        ];

        const districtCoords: any[] = [];

        geojson.features.forEach((feature: any) => {
          if (feature.geometry.type === 'Polygon') {
            // Leaflet expects LatLng structure, GeoJSON is LngLat.
            // We need to flip.
            const coords = feature.geometry.coordinates[0].map((c: any) => [c[1], c[0]]);
            districtCoords.push(coords);
          } else if (feature.geometry.type === 'MultiPolygon') {
            feature.geometry.coordinates.forEach((poly: any) => {
              const coords = poly[0].map((c: any) => [c[1], c[0]]);
              districtCoords.push(coords);
            });
          }
        });

        // The mask is [OuterRing, Hole1, Hole2, ...]
        console.log(`DistrictMask: Loaded ${districtCoords.length} districts.`);
        setMaskData([worldCoords, ...districtCoords]);

      } catch (err) {
        console.error("Failed to fetch district data", err);
      }
    };

    fetchDistricts();
  }, [map]);

  if (maskData.length === 0) return null;

  return (
    <Polygon
      positions={maskData}
      pathOptions={{
        color: 'transparent',
        fillColor: '#000',
        fillOpacity: 0.3, // Adjusted for brighter look
        stroke: false
      }}
    />
  );
}
