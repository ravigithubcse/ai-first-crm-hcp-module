/*
 * =============================================================================
 * AI-First CRM HCP Module - Layout Component
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Main application layout with sidebar navigation
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  MessageSquare,
  CalendarCheck,
  Menu,
  X,
  Activity,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import type { RootState } from '@/store';
import { toggleSidebar, setActiveTab } from '@/store/uiSlice';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { id: 'hcps', label: 'HCPs', icon: Users, path: '/hcps' },
  { id: 'log', label: 'Log Interaction', icon: MessageSquare, path: '/log-interaction' },
  { id: 'interactions', label: 'Interactions', icon: ClipboardList, path: '/interactions' },
  { id: 'follow-ups', label: 'Follow-Ups', icon: CalendarCheck, path: '/follow-ups' },
];

export default function Layout() {
  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();
  const { sidebarOpen } = useSelector((state: RootState) => state.ui);

  const handleNavClick = (item: typeof navItems[0]) => {
    dispatch(setActiveTab(item.id));
    navigate(item.path);
    if (window.innerWidth < 768) {
      dispatch(toggleSidebar());
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => dispatch(toggleSidebar())}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-16'}
        `}
      >
        {/* Header */}
        <div className={`flex items-center h-16 border-b border-gray-200 px-4 ${!sidebarOpen && 'md:justify-center md:px-2'}`}>
          {sidebarOpen ? (
            <>
              <Activity className="w-7 h-7 text-blue-600 mr-3" />
              <div className="flex-1 min-w-0">
                <h1 className="text-sm font-bold text-gray-900 truncate">AI-CRM HCP</h1>
                <p className="text-xs text-gray-500 truncate">Field Rep Tool</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={() => dispatch(toggleSidebar())}
              >
                <X className="w-5 h-5" />
              </Button>
            </>
          ) : (
            <Activity className="w-7 h-7 text-blue-600" />
          )}
        </div>

        {/* Navigation */}
        <nav className="p-2 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                  transition-colors duration-150
                  ${isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                  ${!sidebarOpen && 'md:justify-center md:px-2'}
                `}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
                {sidebarOpen && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        {sidebarOpen && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
            <p className="text-xs text-gray-400 text-center">
              AI-First CRM HCP v1.0.0
            </p>
            <p className="text-xs text-gray-400 text-center mt-0.5">
              &copy; 2026 Ravi Kumar
            </p>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4">
          <Button
            variant="ghost"
            size="icon"
            className="mr-4"
            onClick={() => dispatch(toggleSidebar())}
          >
            <Menu className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-gray-900">
              {navItems.find((n) => n.path === location.pathname)?.label || 'Dashboard'}
            </h2>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}