'use client';

import React, { useState } from 'react';
import { Filter, AlertTriangle, Hammer, Info } from 'lucide-react';
import clsx from 'clsx'; // Make sure clsx is installed or use template literals

interface SidebarProps {
  filters: {
    obstacle: boolean;
    damage: boolean;
    critical: boolean;
    warning: boolean;
  };
  setFilters: React.Dispatch<React.SetStateAction<{
    obstacle: boolean;
    damage: boolean;
    critical: boolean;
    warning: boolean;
  }>>;
}

export default function Sidebar({ filters, setFilters }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div
      className={clsx(
        "absolute top-4 left-4 z-[1000] bg-white/90 backdrop-blur-md border border-white/20 shadow-xl rounded-xl overflow-hidden flex flex-col transition-all duration-300 ease-in-out",
        isOpen ? "w-72 p-4 space-y-4" : "w-[58px] p-2 h-[58px]" // 58px is approx height of the header button area
      )}
    >

      {/* Header */}
      <div className={clsx("flex items-center", isOpen ? "space-x-2 border-b border-gray-100 pb-2" : "justify-center border-none pb-0")}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={clsx(
            "p-2 rounded-lg text-white transition-colors hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300",
            "bg-blue-500"
          )}
          aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
        >
          <Filter size={20} />
        </button>
        {isOpen && (
          <h1 className="font-bold text-gray-800 text-lg whitespace-nowrap overflow-hidden text-ellipsis">Safety Map</h1>
        )}
      </div>

      {/* Content - only show if open */}
      <div className={clsx(
        "flex flex-col space-y-4 transition-opacity duration-200",
        isOpen ? "opacity-100 delay-100" : "opacity-0 hidden pointer-events-none"
      )}>
        {/* Severity Filters (Legend) */}
        <div className="space-y-2">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Severity</h2>

          <button
            onClick={() => setFilters(prev => ({ ...prev, critical: !prev.critical }))}
            className={clsx(
              "w-full flex items-center space-x-3 p-2 rounded-lg transition-colors border",
              filters.critical
                ? "bg-red-50 border-red-200"
                : "bg-transparent border-transparent hover:bg-gray-50 opacity-60"
            )}
          >
            <span className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></span>
            <span className={clsx("text-sm font-medium", filters.critical ? "text-gray-800" : "text-gray-400")}>Critical Issue</span>
            {filters.critical && <span className="ml-auto text-xs text-red-600 font-bold">ON</span>}
          </button>

          <button
            onClick={() => setFilters(prev => ({ ...prev, warning: !prev.warning }))}
            className={clsx(
              "w-full flex items-center space-x-3 p-2 rounded-lg transition-colors border",
              filters.warning
                ? "bg-yellow-50 border-yellow-200"
                : "bg-transparent border-transparent hover:bg-gray-50 opacity-60"
            )}
          >
            <span className="w-3 h-3 rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.6)]"></span>
            <span className={clsx("text-sm font-medium", filters.warning ? "text-gray-800" : "text-gray-400")}>Warning</span>
            {filters.warning && <span className="ml-auto text-xs text-yellow-600 font-bold">ON</span>}
          </button>
        </div>

        {/* Type Filters */}
        <div className="space-y-2">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Problem Type</h2>

          <button
            onClick={() => setFilters(prev => ({ ...prev, obstacle: !prev.obstacle }))}
            className={clsx(
              "w-full flex items-center justify-between p-3 rounded-xl border transition-all duration-200",
              filters.obstacle
                ? "bg-blue-50 border-blue-200 shadow-sm"
                : "bg-transparent border-gray-100 text-gray-400 hover:bg-gray-50"
            )}
          >
            <div className="flex items-center space-x-3">
              <div className={clsx("p-1.5 rounded-md", filters.obstacle ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-400")}>
                <AlertTriangle size={16} />
              </div>
              <span className={clsx("text-sm font-medium", filters.obstacle ? "text-gray-800" : "text-gray-400")}>Path Blocked</span>
            </div>
            <div className={clsx("w-4 h-4 rounded border flex items-center justify-center transition-colors", filters.obstacle ? "bg-blue-500 border-blue-500" : "border-gray-300")}>
              {filters.obstacle && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
            </div>
          </button>

          <button
            onClick={() => setFilters(prev => ({ ...prev, damage: !prev.damage }))}
            className={clsx(
              "w-full flex items-center justify-between p-3 rounded-xl border transition-all duration-200",
              filters.damage
                ? "bg-blue-50 border-blue-200 shadow-sm"
                : "bg-transparent border-gray-100 text-gray-400 hover:bg-gray-50"
            )}
          >
            <div className="flex items-center space-x-3">
              <div className={clsx("p-1.5 rounded-md", filters.damage ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-400")}>
                <Hammer size={16} />
              </div>
              <span className={clsx("text-sm font-medium", filters.damage ? "text-gray-800" : "text-gray-400")}>Surface Damage</span>
            </div>
            <div className={clsx("w-4 h-4 rounded border flex items-center justify-center transition-colors", filters.damage ? "bg-blue-500 border-blue-500" : "border-gray-300")}>
              {filters.damage && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
            </div>
          </button>
        </div>

        <div className="text-xs text-gray-400 px-1 pt-2 border-t border-gray-100">
          <p className="flex items-center"><Info size={12} className="mr-1" /> Click markers for details.</p>
        </div>
      </div>
    </div>
  );
}
