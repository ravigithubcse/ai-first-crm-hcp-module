/*
 * =============================================================================
 * AI-First CRM HCP Module - API Service Layer
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Axios-based API service for backend communication
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import axios, { type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/** HCP API endpoints */
export const hcpApi = {
  list: (params?: { page?: number; pageSize?: number; search?: string; specialty?: string }) =>
    client.get('/hcps', { params }),

  getById: (id: number) => client.get(`/hcps/${id}`),

  create: (data: Record<string, unknown>) => client.post('/hcps', data),

  update: (id: number, data: Record<string, unknown>) =>
    client.put(`/hcps/${id}`, data),

  delete: (id: number) => client.delete(`/hcps/${id}`),

  search: (name: string) => client.get('/hcps/search/by-name', { params: { name } }),

  getSpecialties: () => client.get('/hcps/metadata/specialties'),

  getStats: () => client.get('/hcps/metadata/stats'),
};

/** Interaction API endpoints */
export const interactionApi = {
  list: (params?: { page?: number; pageSize?: number; hcpId?: number; interactionType?: string }) =>
    client.get('/interactions', { params }),

  getById: (id: number) => client.get(`/interactions/${id}`),

  create: (data: Record<string, unknown>) => client.post('/interactions', data),

  update: (id: number, data: Record<string, unknown>) =>
    client.put(`/interactions/${id}`, data),

  delete: (id: number) => client.delete(`/interactions/${id}`),

  getByHCP: (hcpId: number) => client.get(`/interactions/hcp/${hcpId}/history`),

  getRecent: (limit?: number) => client.get('/interactions/recent/all', { params: { limit } }),

  chatLog: (message: string, hcpId?: number) =>
    client.post('/interactions/chat/log', { message, hcp_id: hcpId }),

  generateReport: (interactionId: number, format?: string) =>
    client.post('/interactions/reports/call', {
      interaction_id: interactionId,
      report_format: format || 'structured',
    }),
};

/** Follow-up API endpoints */
export const followUpApi = {
  list: (params?: { page?: number; pageSize?: number; interactionId?: number; status?: string }) =>
    client.get('/follow-ups', { params }),

  getById: (id: number) => client.get(`/follow-ups/${id}`),

  create: (data: Record<string, unknown>) => client.post('/follow-ups', data),

  update: (id: number, data: Record<string, unknown>) =>
    client.put(`/follow-ups/${id}`, data),

  complete: (id: number) => client.post(`/follow-ups/${id}/complete`),

  delete: (id: number) => client.delete(`/follow-ups/${id}`),

  getByInteraction: (interactionId: number) =>
    client.get(`/follow-ups/interaction/${interactionId}`),

  getPending: (limit?: number) => client.get('/follow-ups/pending/all', { params: { limit } }),

  aiSchedule: (data: {
    interaction_id: number;
    title: string;
    description?: string;
    due_date?: string;
    priority?: string;
    assigned_to?: string;
    action_type?: string;
  }) => client.post('/follow-ups/schedule/ai', data),
};

/** AI Agent API endpoints */
export const agentApi = {
  chat: (message: string) =>
    client.post('/agent/chat', { message }),

  executeTool: (toolName: string, parameters: Record<string, unknown>) =>
    client.post('/agent/tools/execute', { tool_name: toolName, parameters }),

  listTools: () => client.get('/agent/tools'),
};

export default client;