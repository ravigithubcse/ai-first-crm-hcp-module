/*
 * =============================================================================
 * AI-First CRM HCP Module - Follow-Ups Page
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
# Description : Follow-up management with AI scheduling
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import {
  CalendarCheck,
  Loader2,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { followUpApi } from '@/services/api';
import { showToast } from '@/store/uiSlice';
import type { AppDispatch } from '@/store';

interface FollowUp {
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
  completed_at: string | null;
}

export default function FollowUps() {
  const dispatch = useDispatch<AppDispatch>();
  const [followUps, setFollowUps] = useState<FollowUp[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [aiDialog, setAiDialog] = useState(false);
  const [aiForm, setAiForm] = useState({
    interaction_id: '',
    title: '',
    description: '',
    due_date: '',
    priority: 'medium',
    assigned_to: '',
    action_type: 'meeting',
  });
  const [isScheduling, setIsScheduling] = useState(false);

  useEffect(() => {
    loadFollowUps();
  }, [statusFilter]);

  const loadFollowUps = async () => {
    setLoading(true);
    try {
      const response = await followUpApi.list({
        page: 1,
        pageSize: 100,
        status: statusFilter || undefined,
      });
      setFollowUps(response.data.items);
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to load follow-ups' }));
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (id: number) => {
    try {
      await followUpApi.complete(id);
      dispatch(showToast({ type: 'success', message: 'Follow-up completed!' }));
      loadFollowUps();
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to complete' }));
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this follow-up?')) return;
    try {
      await followUpApi.delete(id);
      dispatch(showToast({ type: 'success', message: 'Follow-up deleted' }));
      loadFollowUps();
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to delete' }));
    }
  };

  const handleAiSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsScheduling(true);
    try {
      await followUpApi.aiSchedule({
        interaction_id: parseInt(aiForm.interaction_id),
        title: aiForm.title,
        description: aiForm.description || undefined,
        due_date: aiForm.due_date || undefined,
        priority: aiForm.priority,
        assigned_to: aiForm.assigned_to || undefined,
        action_type: aiForm.action_type,
      });
      dispatch(showToast({ type: 'success', message: 'AI-powered follow-up scheduled!' }));
      setAiDialog(false);
      setAiForm({
        interaction_id: '', title: '', description: '', due_date: '',
        priority: 'medium', assigned_to: '', action_type: 'meeting',
      });
      loadFollowUps();
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to schedule' }));
    } finally {
      setIsScheduling(false);
    }
  };

  const getPriorityColor = (p: string) => {
    switch (p) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-amber-100 text-amber-700';
      default: return 'bg-green-100 text-green-700';
    }
  };

  const getStatusIcon = (s: string) => {
    switch (s) {
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case 'overdue': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-amber-600" />;
    }
  };

  const pendingCount = followUps.filter((f) => f.status === 'pending').length;
  const completedCount = followUps.filter((f) => f.status === 'completed').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Follow-Ups</h2>
          <p className="text-gray-500 mt-1">
            {pendingCount} pending, {completedCount} completed
          </p>
        </div>
        <Dialog open={aiDialog} onOpenChange={setAiDialog}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Sparkles className="w-4 h-4 mr-2" />
              AI Schedule
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-600" />
                AI-Powered Follow-Up Scheduling
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAiSchedule} className="space-y-4">
              <div>
                <Label htmlFor="int-id">Interaction ID *</Label>
                <Input
                  id="int-id"
                  type="number"
                  value={aiForm.interaction_id}
                  onChange={(e) => setAiForm({ ...aiForm, interaction_id: e.target.value })}
                  placeholder="Enter interaction ID"
                  required
                />
              </div>
              <div>
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={aiForm.title}
                  onChange={(e) => setAiForm({ ...aiForm, title: e.target.value })}
                  placeholder="Follow-up title"
                  required
                />
              </div>
              <div>
                <Label htmlFor="desc">Description</Label>
                <Input
                  id="desc"
                  value={aiForm.description}
                  onChange={(e) => setAiForm({ ...aiForm, description: e.target.value })}
                  placeholder="Optional description"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="due">Due Date</Label>
                  <Input
                    id="due"
                    type="date"
                    value={aiForm.due_date}
                    onChange={(e) => setAiForm({ ...aiForm, due_date: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="prio">Priority</Label>
                  <select
                    id="prio"
                    value={aiForm.priority}
                    onChange={(e) => setAiForm({ ...aiForm, priority: e.target.value })}
                    className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="assigned">Assigned To</Label>
                  <Input
                    id="assigned"
                    value={aiForm.assigned_to}
                    onChange={(e) => setAiForm({ ...aiForm, assigned_to: e.target.value })}
                    placeholder="Field Rep Name"
                  />
                </div>
                <div>
                  <Label htmlFor="action">Action Type</Label>
                  <select
                    id="action"
                    value={aiForm.action_type}
                    onChange={(e) => setAiForm({ ...aiForm, action_type: e.target.value })}
                    className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white"
                  >
                    <option value="meeting">Meeting</option>
                    <option value="call">Call</option>
                    <option value="email">Email</option>
                    <option value="send_material">Send Material</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setAiDialog(false)}>
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
                <Button type="submit" disabled={isScheduling} className="bg-blue-600 hover:bg-blue-700">
                  {isScheduling && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  <Sparkles className="w-4 h-4 mr-2" />
                  Schedule with AI
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {['', 'pending', 'completed', 'overdue'].map((s) => (
          <Button
            key={s || 'all'}
            variant={statusFilter === s ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter(s)}
          >
            {s ? s.charAt(0).toUpperCase() + s.slice(1) : 'All'}
          </Button>
        ))}
      </div>

      {/* Follow-ups List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : followUps.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <CalendarCheck className="w-16 h-16 text-gray-300 mb-4" />
            <p className="text-gray-500 text-lg">No follow-ups found</p>
            <p className="text-gray-400 text-sm mt-1">Schedule your first follow-up</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {followUps.map((fu) => (
            <Card key={fu.id} className={fu.status === 'completed' ? 'opacity-70' : ''}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(fu.status)}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">{fu.title}</h3>
                      <p className="text-xs text-gray-500">
                        Interaction #{fu.interaction_id}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {fu.ai_suggested && (
                      <Badge variant="secondary" className="text-xs">
                        <Sparkles className="w-3 h-3 mr-1" />
                        AI
                      </Badge>
                    )}
                    <Badge className={getPriorityColor(fu.priority)}>{fu.priority}</Badge>
                  </div>
                </div>

                {fu.description && (
                  <p className="text-sm text-gray-600 mt-3">{fu.description}</p>
                )}

                <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                  {fu.due_date && (
                    <span>Due: {new Date(fu.due_date).toLocaleDateString()}</span>
                  )}
                  {fu.assigned_to && <span>Assigned: {fu.assigned_to}</span>}
                  {fu.action_type && (
                    <Badge variant="outline" className="text-xs">{fu.action_type}</Badge>
                  )}
                </div>

                {fu.status === 'pending' && (
                  <div className="flex gap-2 mt-3 pt-3 border-t">
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-green-600 border-green-300 hover:bg-green-50"
                      onClick={() => handleComplete(fu.id)}
                    >
                      <CheckCircle2 className="w-4 h-4 mr-1" />
                      Complete
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-gray-400 hover:text-red-600"
                      onClick={() => handleDelete(fu.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}