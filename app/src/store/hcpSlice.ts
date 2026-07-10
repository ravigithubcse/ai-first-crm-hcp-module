/*
 * =============================================================================
 * AI-First CRM HCP Module - HCP Redux Slice
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Redux slice for HCP state management
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import { hcpApi } from '@/services/api';
import type { HCP, HCPState, PaginatedResponse } from '@/types';

const initialState: HCPState = {
  items: [],
  selectedHCP: null,
  loading: false,
  error: null,
  total: 0,
  page: 1,
};

export const fetchHCPs = createAsyncThunk(
  'hcps/fetchHCPs',
  async (params: { page?: number; pageSize?: number; search?: string; specialty?: string } = {}) => {
    const response = await hcpApi.list(params);
    return response.data as PaginatedResponse<HCP>;
  }
);

export const fetchHCPById = createAsyncThunk(
  'hcps/fetchHCPById',
  async (id: number) => {
    const response = await hcpApi.getById(id);
    return response.data as HCP;
  }
);

export const searchHCPs = createAsyncThunk(
  'hcps/searchHCPs',
  async (name: string) => {
    const response = await hcpApi.search(name);
    return response.data as HCP[];
  }
);

export const createHCP = createAsyncThunk(
  'hcps/createHCP',
  async (data: Omit<HCP, 'id' | 'created_at' | 'updated_at' | 'interaction_count'>) => {
    const response = await hcpApi.create(data);
    return response.data as HCP;
  }
);

export const updateHCP = createAsyncThunk(
  'hcps/updateHCP',
  async ({ id, data }: { id: number; data: Partial<HCP> }) => {
    const response = await hcpApi.update(id, data);
    return response.data as HCP;
  }
);

export const deleteHCP = createAsyncThunk(
  'hcps/deleteHCP',
  async (id: number) => {
    await hcpApi.delete(id);
    return id;
  }
);

const hcpSlice = createSlice({
  name: 'hcps',
  initialState,
  reducers: {
    setSelectedHCP: (state, action: PayloadAction<HCP | null>) => {
      state.selectedHCP = action.payload;
    },
    clearHCPError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch HCPs';
      })
      .addCase(fetchHCPById.fulfilled, (state, action) => {
        state.selectedHCP = action.payload;
      })
      .addCase(searchHCPs.fulfilled, (state, action) => {
        state.items = action.payload;
      })
      .addCase(createHCP.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
        state.total += 1;
      })
      .addCase(updateHCP.fulfilled, (state, action) => {
        const index = state.items.findIndex((h) => h.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        if (state.selectedHCP?.id === action.payload.id) {
          state.selectedHCP = action.payload;
        }
      })
      .addCase(deleteHCP.fulfilled, (state, action) => {
        state.items = state.items.filter((h) => h.id !== action.payload);
        state.total -= 1;
        if (state.selectedHCP?.id === action.payload) {
          state.selectedHCP = null;
        }
      });
  },
});

export const { setSelectedHCP, clearHCPError } = hcpSlice.actions;
export default hcpSlice.reducer;