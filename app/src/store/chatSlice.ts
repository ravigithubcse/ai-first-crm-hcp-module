/*
 * =============================================================================
 * AI-First CRM HCP Module - Chat Redux Slice
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Redux slice for AI Chat state management
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import { agentApi } from '@/services/api';
import type { ChatMessage, ChatState, AgentToolResult } from '@/types';
import { v4 as uuidv4 } from 'uuid';

const initialState: ChatState = {
  messages: [
    {
      id: uuidv4(),
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant for HCP CRM. I can help you:\n\n- Log interactions ("Met with Dr. Smith...")\n- View interaction history\n- Generate call reports\n- Schedule follow-ups\n- Edit interactions\n\nHow can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ],
  isProcessing: false,
  error: null,
};

export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message: string, { dispatch }) => {
    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    dispatch(addMessage(userMsg));

    const response = await agentApi.chat(message);
    return response.data as { intent: string; message: string; result: Record<string, unknown> };
  }
);

export const executeToolDirect = createAsyncThunk(
  'chat/executeTool',
  async (params: { toolName: string; parameters: Record<string, unknown> }) => {
    const response = await agentApi.executeTool(params.toolName, params.parameters);
    return response.data as AgentToolResult;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    setMessages: (state, action: PayloadAction<ChatMessage[]>) => {
      state.messages = action.payload;
    },
    clearChat: (state) => {
      state.messages = initialState.messages;
      state.error = null;
    },
    clearChatError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.isProcessing = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.isProcessing = false;
        const assistantMsg: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: action.payload.message,
          timestamp: new Date().toISOString(),
          metadata: {
            intent: action.payload.intent,
            toolResult: action.payload.result,
          },
        };
        state.messages.push(assistantMsg);
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.isProcessing = false;
        state.error = action.error.message || 'Failed to process message';
        const errorMsg: ChatMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: 'I apologize, but I encountered an error processing your request. Please try again.',
          timestamp: new Date().toISOString(),
        };
        state.messages.push(errorMsg);
      });
  },
});

export const { addMessage, setMessages, clearChat, clearChatError } = chatSlice.actions;
export default chatSlice.reducer;