/*
 * =============================================================================
 * AI-First CRM HCP Module - Frontend Type Definitions
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : TypeScript type definitions for the CRM application
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

/** Healthcare Professional entity */
export interface HCP {
  id: number;
  full_name: string;
  email: string | null;
  phone: string | null;
  specialty: string | null;
  institution: string | null;
  location: string | null;
  npi_number: string | null;
  tier: string;
  notes: string | null;
  is_active: boolean;
  interaction_count: number;
  created_at: string | null;
  updated_at: string | null;
}

/** Interaction entity */
export interface Interaction {
  id: number;
  hcp_id: number;
  interaction_type: string;
  date: string;
  time: string | null;
  attendees: string[];
  topics_discussed: string | null;
  materials_shared: string[];
  samples_distributed: string[];
  sentiment: string;
  summary: string | null;
  key_insights: string[];
  follow_up_actions: string[];
  outcomes: string | null;
  next_steps: string | null;
  voice_note_transcript: string | null;
  logged_by: string | null;
  source: string;
  confidence_score: number | null;
  created_at: string | null;
  updated_at: string | null;
}

/** Follow-up entity */
export interface FollowUp {
  id: number;
  interaction_id: number;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: string;
  status: string;
  assigned_to: string | null;
  action_type: string | null;
  ai_suggested: boolean;
  created_at: string | null;
  updated_at: string | null;
  completed_at: string | null;
}

/** Chat message for AI assistant */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    intent?: string;
    toolResult?: Record<string, unknown>;
  };
}

/** Paginated API response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/** AI Agent tool result */
export interface AgentToolResult {
  success: boolean;
  message: string;
  result?: Record<string, unknown>;
  error?: string;
}

/** Application state */
export interface AppState {
  hcps: HCPState;
  interactions: InteractionState;
  chat: ChatState;
  ui: UIState;
}

/** HCP state */
export interface HCPState {
  items: HCP[];
  selectedHCP: HCP | null;
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
}

/** Interaction state */
export interface InteractionState {
  items: Interaction[];
  selectedInteraction: Interaction | null;
  loading: boolean;
  error: string | null;
  recent: Interaction[];
}

/** Chat state */
export interface ChatState {
  messages: ChatMessage[];
  isProcessing: boolean;
  error: string | null;
}

/** UI state */
export interface UIState {
  sidebarOpen: boolean;
  activeTab: string;
  toast: ToastMessage | null;
}

/** Toast notification */
export interface ToastMessage {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}