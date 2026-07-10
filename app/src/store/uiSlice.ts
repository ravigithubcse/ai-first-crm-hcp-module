/*
 * =============================================================================
 * AI-First CRM HCP Module - UI Redux Slice
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Redux slice for UI state management
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { UIState, ToastMessage } from '@/types';

const initialState: UIState = {
  sidebarOpen: true,
  activeTab: 'dashboard',
  toast: null,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload;
    },
    showToast: (state, action: PayloadAction<ToastMessage>) => {
      state.toast = action.payload;
    },
    clearToast: (state) => {
      state.toast = null;
    },
  },
});

export const { toggleSidebar, setSidebarOpen, setActiveTab, showToast, clearToast } = uiSlice.actions;
export default uiSlice.reducer;