/*
 * =============================================================================
 * AI-First CRM HCP Module - Redux Store
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Redux store configuration with all slices
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { configureStore } from '@reduxjs/toolkit';
import hcpReducer from './hcpSlice';
import interactionReducer from './interactionSlice';
import chatReducer from './chatSlice';
import uiReducer from './uiSlice';

export const store = configureStore({
  reducer: {
    hcps: hcpReducer,
    interactions: interactionReducer,
    chat: chatReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['chat/addMessage', 'chat/setMessages'],
        ignoredPaths: ['chat.messages'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;