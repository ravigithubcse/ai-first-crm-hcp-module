/*
 * =============================================================================
 * AI-First CRM HCP Module - Log Interaction Page
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.1.0
 * Description : Main interaction logging screen -- structured form and AI
 *                chat assistant shown side by side, writing to the same
 *                record. Logging (or editing) an interaction from chat
 *                auto-fills the form on the left in real time so the rep
 *                can see, correct, and save what the AI captured.
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Send,
  Mic,
  Bot,
  User,
  Loader2,
  Sparkles,
  Plus,
  X,
  Search,
  ChevronDown,
  Smile,
  Meh,
  Frown,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { RootState } from '@/store';
import type { AppDispatch } from '@/store';
import { sendChatMessage, clearChat } from '@/store/chatSlice';
import { createInteraction, updateInteraction, fetchRecentInteractions } from '@/store/interactionSlice';
import { fetchHCPs } from '@/store/hcpSlice';
import { showToast } from '@/store/uiSlice';
import { hcpApi } from '@/services/api';
import type { HCP } from '@/types';

/** Tool names (agent "intent") that carry a saved/updated interaction we
 * should reflect back onto the structured form. */
const AUTOFILL_INTENTS = new Set(['log_interaction', 'edit_interaction']);

/** The subset of log_interaction_tool / edit_interaction_tool's JSON
 * result that the form reads back to auto-fill itself. */
interface LoggedInteractionResult {
  success?: boolean;
  interaction?: {
    id: number;
    interaction_type?: string;
    date?: string;
    time?: string | null;
    attendees?: string[];
    topics_discussed?: string | null;
    materials_shared?: string[];
    samples_distributed?: string[];
    sentiment?: string;
    outcomes?: string | null;
    next_steps?: string | null;
  };
  hcp?: HCP;
  follow_up_suggestions?: string[];
}

export default function LogInteraction() {
  const dispatch = useDispatch<AppDispatch>();
  const { messages, isProcessing } = useSelector((state: RootState) => state.chat);
  const [chatInput, setChatInput] = useState('');

  // Form state
  const [selectedHCP, setSelectedHCP] = useState<HCP | null>(null);
  const [hcpSearch, setHcpSearch] = useState('');
  const [hcpResults, setHcpResults] = useState<HCP[]>([]);
  const [showHcpDropdown, setShowHcpDropdown] = useState(false);
  const [interactionType, setInteractionType] = useState('Meeting');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [time, setTime] = useState(new Date().toTimeString().slice(0, 5));
  const [attendees, setAttendees] = useState('');
  const [topics, setTopics] = useState('');
  const [materials, setMaterials] = useState('');
  const [samples, setSamples] = useState('');
  const [sentiment, setSentiment] = useState('neutral');
  const [outcomes, setOutcomes] = useState('');
  const [nextSteps, setNextSteps] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Set once the AI chat has saved (or edited) an interaction, so the
  // "Log Interaction" button on the left updates that same record instead
  // of creating a duplicate. Cleared by "Clear" or once a fresh chat-driven
  // log starts a new record.
  const [autofilledInteractionId, setAutofilledInteractionId] = useState<number | null>(null);
  const lastAppliedMessageId = useRef<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    dispatch(fetchHCPs({ page: 1, pageSize: 100 }));
  }, [dispatch]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // HCP search
  useEffect(() => {
    if (hcpSearch.length > 1) {
      hcpApi.search(hcpSearch).then((res) => {
        setHcpResults(res.data);
        setShowHcpDropdown(true);
      });
    } else {
      setHcpResults([]);
      setShowHcpDropdown(false);
    }
  }, [hcpSearch]);

  // --- Chat -> form autofill -------------------------------------------
  // Whenever the assistant successfully logs or edits an interaction, pull
  // the saved record back out of the tool result and populate every
  // matching field on the left, so what happened in chat is immediately
  // visible (and editable) in the structured form.
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (!last || last.role !== 'assistant') return;
    if (last.id === lastAppliedMessageId.current) return;

    const intent = last.metadata?.intent;
    const toolResult = last.metadata?.toolResult as LoggedInteractionResult | undefined;
    if (!intent || !AUTOFILL_INTENTS.has(intent) || !toolResult || toolResult.success === false) return;

    const { interaction, hcp } = toolResult;
    if (!interaction) return;

    lastAppliedMessageId.current = last.id;

    if (hcp) setSelectedHCP(hcp);
    setHcpSearch('');
    setShowHcpDropdown(false);
    setInteractionType(interaction.interaction_type || 'Meeting');
    if (interaction.date) setDate(String(interaction.date).slice(0, 10));
    if (interaction.time) setTime(interaction.time);
    setAttendees((interaction.attendees || []).join(', '));
    setTopics(interaction.topics_discussed || '');
    setMaterials((interaction.materials_shared || []).join(', '));
    setSamples((interaction.samples_distributed || []).join(', '));
    setSentiment((interaction.sentiment || 'neutral').toLowerCase());
    setOutcomes(interaction.outcomes || '');
    setNextSteps(
      interaction.next_steps || (toolResult.follow_up_suggestions || []).join('; ')
    );
    setAutofilledInteractionId(interaction.id ?? null);

    dispatch(fetchRecentInteractions(10));
    dispatch(
      showToast({
        type: 'success',
        message:
          intent === 'edit_interaction'
            ? 'Interaction updated from chat -- review the form on the left.'
            : 'Logged from chat -- form auto-filled below, review and save if anything needs a tweak.',
      })
    );
  }, [messages, dispatch]);

  const resetForm = () => {
    setSelectedHCP(null);
    setHcpSearch('');
    setTopics('');
    setMaterials('');
    setSamples('');
    setOutcomes('');
    setNextSteps('');
    setAttendees('');
    setSentiment('neutral');
    setAutofilledInteractionId(null);
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isProcessing) return;
    dispatch(sendChatMessage(chatInput) as any);
    setChatInput('');
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHCP) {
      dispatch(showToast({ type: 'error', message: 'Please select an HCP' }));
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        hcp_id: selectedHCP.id,
        interaction_type: interactionType,
        date: new Date(date).toISOString(),
        time,
        attendees: attendees.split(',').map((a) => a.trim()).filter(Boolean),
        topics_discussed: topics,
        materials_shared: materials.split(',').map((m) => m.trim()).filter(Boolean),
        samples_distributed: samples.split(',').map((s) => s.trim()).filter(Boolean),
        sentiment,
        outcomes,
        next_steps: nextSteps,
      };

      if (autofilledInteractionId) {
        // This record was already created by the chat agent -- update it
        // rather than creating a duplicate.
        await dispatch(updateInteraction({ id: autofilledInteractionId, data: payload }) as any);
        dispatch(showToast({ type: 'success', message: 'Interaction updated!' }));
      } else {
        await dispatch(createInteraction(payload) as any);
        dispatch(showToast({ type: 'success', message: 'Interaction logged successfully!' }));
      }

      dispatch(fetchRecentInteractions(10));
      resetForm();
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to log interaction' }));
    } finally {
      setIsSubmitting(false);
    }
  };

  const sentimentOptions = [
    { value: 'positive', label: 'Positive', icon: Smile, color: 'text-green-600 border-green-300 bg-green-50' },
    { value: 'neutral', label: 'Neutral', icon: Meh, color: 'text-amber-600 border-amber-300 bg-amber-50' },
    { value: 'negative', label: 'Negative', icon: Frown, color: 'text-red-600 border-red-300 bg-red-50' },
  ];

  const interactionTypes = ['Meeting', 'Call', 'Email', 'Virtual Meeting', 'Conference', 'Other'];

  return (
    <div className="h-full">
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6 items-start">
        {/* ------------------------------------------------------------ */}
        {/* Structured form -- always visible, auto-fills from chat      */}
        {/* ------------------------------------------------------------ */}
        <form onSubmit={handleFormSubmit} className="space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              Log HCP Interaction
            </h1>
            {autofilledInteractionId && (
              <Badge variant="outline" className="text-xs border-blue-300 text-blue-600">
                Editing interaction #{autofilledInteractionId} (logged via chat)
              </Badge>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Interaction Details */}
            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Interaction Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* HCP Selection */}
                  <div className="relative">
                    <Label htmlFor="hcp">HCP Name *</Label>
                    <div className="relative mt-1.5">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <Input
                        id="hcp"
                        value={selectedHCP ? selectedHCP.full_name : hcpSearch}
                        onChange={(e) => {
                          setHcpSearch(e.target.value);
                          if (selectedHCP) setSelectedHCP(null);
                        }}
                        placeholder="Search or select HCP..."
                        className="pl-9"
                        required
                      />
                      {selectedHCP && (
                        <button
                          type="button"
                          onClick={() => { setSelectedHCP(null); setHcpSearch(''); }}
                          className="absolute right-3 top-1/2 -translate-y-1/2"
                        >
                          <X className="w-4 h-4 text-gray-400" />
                        </button>
                      )}
                    </div>
                    {showHcpDropdown && hcpResults.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                        {hcpResults.map((hcp) => (
                          <button
                            key={hcp.id}
                            type="button"
                            onClick={() => {
                              setSelectedHCP(hcp);
                              setHcpSearch('');
                              setShowHcpDropdown(false);
                            }}
                            className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                          >
                            <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-sm font-semibold text-blue-600">
                              {hcp.full_name.charAt(0)}
                            </div>
                            <div>
                              <p className="text-sm font-medium">{hcp.full_name}</p>
                              <p className="text-xs text-gray-500">{hcp.specialty || 'No specialty'}</p>
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Interaction Type & Date/Time */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Interaction Type</Label>
                      <div className="relative mt-1.5">
                        <select
                          value={interactionType}
                          onChange={(e) => setInteractionType(e.target.value)}
                          className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
                        >
                          {interactionTypes.map((t) => (
                            <option key={t} value={t}>{t}</option>
                          ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                      </div>
                    </div>
                    <div>
                      <Label>Date</Label>
                      <Input
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Time</Label>
                    <Input
                      type="time"
                      value={time}
                      onChange={(e) => setTime(e.target.value)}
                      className="mt-1.5 w-32"
                    />
                  </div>

                  {/* Attendees */}
                  <div>
                    <Label htmlFor="attendees">Attendees</Label>
                    <Input
                      id="attendees"
                      value={attendees}
                      onChange={(e) => setAttendees(e.target.value)}
                      placeholder="Enter names, separated by commas"
                      className="mt-1.5"
                    />
                  </div>

                  {/* Topics Discussed */}
                  <div>
                    <Label htmlFor="topics">Topics Discussed</Label>
                    <Textarea
                      id="topics"
                      value={topics}
                      onChange={(e) => setTopics(e.target.value)}
                      placeholder="Enter key discussion points..."
                      className="mt-1.5 min-h-[100px]"
                    />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              {/* Materials & Samples */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Materials & Samples</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="materials">Materials Shared</Label>
                    <Textarea
                      id="materials"
                      value={materials}
                      onChange={(e) => setMaterials(e.target.value)}
                      placeholder="List materials shared, separated by commas"
                      className="mt-1.5"
                    />
                  </div>
                  <div>
                    <Label htmlFor="samples">Samples Distributed</Label>
                    <Textarea
                      id="samples"
                      value={samples}
                      onChange={(e) => setSamples(e.target.value)}
                      placeholder="List samples distributed, separated by commas"
                      className="mt-1.5"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Sentiment */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Observed HCP Sentiment</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-3">
                    {sentimentOptions.map((opt) => {
                      const Icon = opt.icon;
                      return (
                        <button
                          key={opt.value}
                          type="button"
                          onClick={() => setSentiment(opt.value)}
                          className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all
                            ${sentiment === opt.value
                              ? opt.color
                              : 'border-gray-200 text-gray-500 hover:border-gray-300'
                            }`}
                        >
                          <Icon className="w-5 h-5" />
                          <span className="text-sm font-medium">{opt.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Outcomes & Follow-up */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Outcomes & Follow-up</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="outcomes">Key Outcomes</Label>
                    <Textarea
                      id="outcomes"
                      value={outcomes}
                      onChange={(e) => setOutcomes(e.target.value)}
                      placeholder="Key outcomes or agreements..."
                      className="mt-1.5"
                    />
                  </div>
                  <div>
                    <Label htmlFor="nextSteps">Follow-up Actions</Label>
                    <Textarea
                      id="nextSteps"
                      value={nextSteps}
                      onChange={(e) => setNextSteps(e.target.value)}
                      placeholder="Enter next steps or tasks..."
                      className="mt-1.5"
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={resetForm}>
              <X className="w-4 h-4 mr-2" />
              Clear
            </Button>
            <Button type="submit" disabled={isSubmitting} className="bg-blue-600 hover:bg-blue-700">
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Plus className="w-4 h-4 mr-2" />
              )}
              {autofilledInteractionId ? 'Update Interaction' : 'Log Interaction'}
            </Button>
          </div>
        </form>

        {/* ------------------------------------------------------------ */}
        {/* AI Assistant -- always visible alongside the form             */}
        {/* ------------------------------------------------------------ */}
        <Card className="h-[calc(100vh-140px)] xl:sticky xl:top-6 flex flex-col">
          <CardHeader className="pb-3 border-b">
            <CardTitle className="text-base flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-600" />
              AI Assistant
              <Badge variant="secondary" className="text-xs">Powered by Groq</Badge>
            </CardTitle>
            <p className="text-xs text-gray-400">Log interaction via chat</p>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0 min-h-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-blue-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 text-sm ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                    {msg.metadata?.intent && msg.role === 'assistant' && (
                      <div className="mt-2 pt-2 border-t border-gray-200/50">
                        <Badge variant="outline" className="text-xs">
                          Intent: {msg.metadata.intent}
                        </Badge>
                      </div>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                </div>
              ))}
              {isProcessing && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <form onSubmit={handleChatSubmit} className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  className="flex-shrink-0"
                  title="Voice input (coming soon)"
                >
                  <Mic className="w-4 h-4" />
                </Button>
                <Input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Describe interaction..."
                  className="flex-1"
                  disabled={isProcessing}
                />
                <Button
                  type="submit"
                  disabled={isProcessing || !chatInput.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
              <div className="flex justify-between mt-2">
                <p className="text-xs text-gray-400">
                  Try: &quot;Met Dr. Smith, discussed Product X efficacy, positive sentiment&quot;
                </p>
                <button
                  type="button"
                  onClick={() => dispatch(clearChat())}
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  Clear chat
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
