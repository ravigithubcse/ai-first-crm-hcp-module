/*
 * =============================================================================
 * AI-First CRM HCP Module - Interaction Redux Slice
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Redux slice for Interaction state management
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import { interactionApi } from '@/services/api';
import type { Interaction, InteractionState, PaginatedResponse } from '@/types';

const initialState: InteractionState = {
  items: [],
  selectedInteraction: null,
  loading: false,
  error: null,
  recent: [],
};

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchInteractions',
  async (params: { page?: number; pageSize?: number; hcpId?: number; interactionType?: string } = {}) => {
    const response = await interactionApi.list(params);
    return response.data as PaginatedResponse<Interaction>;
  }
);

export const fetchInteractionById = createAsyncThunk(
  'interactions/fetchInteractionById',
  async (id: number) => {
    const response = await interactionApi.getById(id);
    return response.data as Interaction;
  }
);

export const fetchHCPInteractions = createAsyncThunk(
  'interactions/fetchHCPInteractions',
  async (hcpId: number) => {
    const response = await interactionApi.getByHCP(hcpId);
    return response.data.items as Interaction[];
  }
);

export const fetchRecentInteractions = createAsyncThunk(
  'interactions/fetchRecent',
  async (limit: number = 10) => {
    const response = await interactionApi.getRecent(limit);
    return response.data.items as Interaction[];
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/createInteraction',
  async (data: {
    hcp_id: number;
    interaction_type: string;
    date: string;
    time?: string;
    attendees?: string[];
    topics_discussed?: string;
    materials_shared?: string[];
    samples_distributed?: string[];
    sentiment?: string;
    outcomes?: string;
    next_steps?: string;
    logged_by?: string;
  }) => {
    const response = await interactionApi.create(data);
    return response.data as Interaction;
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/updateInteraction',
  async ({ id, data }: { id: number; data: Partial<Interaction> }) => {
    const response = await interactionApi.update(id, data);
    return response.data as Interaction;
  }
);

export const deleteInteraction = createAsyncThunk(
  'interactions/deleteInteraction',
  async (id: number) => {
    await interactionApi.delete(id);
    return id;
  }
);

const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    setSelectedInteraction: (state, action: PayloadAction<Interaction | null>) => {
      state.selectedInteraction = action.payload;
    },
    clearInteractionError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch interactions';
      })
      .addCase(fetchInteractionById.fulfilled, (state, action) => {
        state.selectedInteraction = action.payload;
      })
      .addCase(fetchHCPInteractions.fulfilled, (state, action) => {
        state.items = action.payload;
      })
      .addCase(fetchRecentInteractions.fulfilled, (state, action) => {
        state.recent = action.payload;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
        state.recent.unshift(action.payload);
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const index = state.items.findIndex((i) => i.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        if (state.selectedInteraction?.id === action.payload.id) {
          state.selectedInteraction = action.payload;
        }
      })
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.items = state.items.filter((i) => i.id !== action.payload);
        state.recent = state.recent.filter((i) => i.id !== action.payload);
        if (state.selectedInteraction?.id === action.payload) {
          state.selectedInteraction = null;
        }
      });
  },
});

export const { setSelectedInteraction, clearInteractionError } = interactionSlice.actions;
export default interactionSlice.reducer;