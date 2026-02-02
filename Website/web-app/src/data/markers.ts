export interface MarkerData {
  id: string; // Pano ID
  lat: number;
  lng: number;
  type: string; // 'OBSTACLE' | 'SURFACE DAMAGE' | 'BOTH' | 'None'
  severity: 'WARNING' | 'CRITICAL' | 'SAFE';
  description: string;
  image: string; // Path to local image in public folder
  panoId: string;
  heading: number;
  date: string; // e.g., 2024-11
  dateNote: string;
  raw?: {
    total_blocked_pct: string;
    obstacle_pct: string;
    damage_pct: string;
  };
}

export type MarkerType = 'OBSTACLE' | 'SURFACE DAMAGE' | 'BOTH';
export type MarkerSeverity = 'WARNING' | 'CRITICAL';
