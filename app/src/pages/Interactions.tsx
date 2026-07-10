/*
 * =============================================================================
 * AI-First CRM HCP Module - Interactions Page
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
# Description : Interaction history listing with filters and AI features
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  ClipboardList,
  Loader2,
  Search,
  FileText,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { RootState } from '@/store';
import type { AppDispatch } from '@/store';
import { fetchInteractions, deleteInteraction, setSelectedInteraction } from '@/store/interactionSlice';
import { showToast } from '@/store/uiSlice';
import { interactionApi } from '@/services/api';

export default function Interactions() {
  const dispatch = useDispatch<AppDispatch>();
  const { items: interactions, loading, selectedInteraction } = useSelector((state: RootState) => state.interactions);
  const [page, setPage] = useState(1);
  const [hcpFilter, setHcpFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [reportDialog, setReportDialog] = useState(false);
  const [reportContent, setReportContent] = useState('');
  const [detailDialog, setDetailDialog] = useState(false);

  useEffect(() => {
    dispatch(fetchInteractions({
      page,
      pageSize: 20,
      hcpId: hcpFilter ? parseInt(hcpFilter) : undefined,
      interactionType: typeFilter || undefined,
    }) as any);
  }, [dispatch, page, hcpFilter, typeFilter]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this interaction?')) return;
    try {
      await dispatch(deleteInteraction(id) as any);
      dispatch(showToast({ type: 'success', message: 'Interaction deleted' }));
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to delete' }));
    }
  };

  const handleGenerateReport = async (interactionId: number) => {
    try {
      const response = await interactionApi.generateReport(interactionId);
      setReportContent(response.data.report);
      setReportDialog(true);
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to generate report' }));
    }
  };

  const getSentimentColor = (s: string) => {
    switch (s) {
      case 'positive': return 'bg-green-100 text-green-700 border-green-200';
      case 'negative': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };



  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Interaction History</h2>
        <p className="text-gray-500 mt-1">View and manage all HCP interactions</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Filter by HCP ID..."
            value={hcpFilter}
            onChange={(e) => { setHcpFilter(e.target.value); setPage(1); }}
            className="pl-9"
            type="number"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="h-10 px-3 py-2 border border-gray-300 rounded-md text-sm bg-white"
        >
          <option value="">All Types</option>
          <option value="Meeting">Meeting</option>
          <option value="Call">Call</option>
          <option value="Email">Email</option>
          <option value="Virtual Meeting">Virtual Meeting</option>
          <option value="Conference">Conference</option>
        </select>
        {(hcpFilter || typeFilter) && (
          <Button variant="outline" size="sm" onClick={() => { setHcpFilter(''); setTypeFilter(''); }}>
            <X className="w-4 h-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Interactions List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : interactions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <ClipboardList className="w-16 h-16 text-gray-300 mb-4" />
            <p className="text-gray-500 text-lg">No interactions found</p>
            <p className="text-gray-400 text-sm mt-1">Log your first interaction to see it here</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {interactions.map((interaction) => (
            <Card
              key={interaction.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => {
                dispatch(setSelectedInteraction(interaction));
                setDetailDialog(true);
              }}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge variant="outline">{interaction.interaction_type}</Badge>
                      <Badge className={getSentimentColor(interaction.sentiment)}>
                        {interaction.sentiment}
                      </Badge>
                      {interaction.source === 'chat' && (
                        <Badge variant="secondary" className="text-xs">
                          <Sparkles className="w-3 h-3 mr-1" />
                          AI
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      {interaction.topics_discussed
                        ? interaction.topics_discussed.substring(0, 120) + '...'
                        : 'No topics recorded'}
                    </p>
                    {interaction.summary && (
                      <div className="mt-2 p-2 bg-blue-50 rounded-md">
                        <p className="text-xs text-blue-700 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          {interaction.summary}
                        </p>
                      </div>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span>HCP ID: {interaction.hcp_id}</span>
                      <span>
                        {interaction.date
                          ? new Date(interaction.date).toLocaleDateString()
                          : ''}
                      </span>
                      {interaction.attendees && interaction.attendees.length > 0 && (
                        <span>Attendees: {interaction.attendees.join(', ')}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="w-8 h-8"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleGenerateReport(interaction.id);
                      }}
                      title="Generate report"
                    >
                      <FileText className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="w-8 h-8 text-gray-400 hover:text-red-600"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(interaction.id);
                      }}
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      <div className="flex justify-center gap-2">
        <Button variant="outline" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
          Previous
        </Button>
        <span className="flex items-center px-4 text-sm text-gray-600">Page {page}</span>
        <Button variant="outline" onClick={() => setPage((p) => p + 1)} disabled={interactions.length < 20}>
          Next
        </Button>
      </div>

      {/* Report Dialog */}
      <Dialog open={reportDialog} onOpenChange={setReportDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Call Report
            </DialogTitle>
          </DialogHeader>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
              {reportContent}
            </pre>
          </div>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={detailDialog} onOpenChange={setDetailDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Interaction Details</DialogTitle>
          </DialogHeader>
          {selectedInteraction && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Type:</span>
                  <Badge variant="outline" className="ml-2">{selectedInteraction.interaction_type}</Badge>
                </div>
                <div>
                  <span className="text-gray-500">Sentiment:</span>
                  <Badge className={`ml-2 ${getSentimentColor(selectedInteraction.sentiment)}`}>
                    {selectedInteraction.sentiment}
                  </Badge>
                </div>
                <div>
                  <span className="text-gray-500">Date:</span>
                  <span className="ml-2">{selectedInteraction.date ? new Date(selectedInteraction.date).toLocaleDateString() : 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Source:</span>
                  <span className="ml-2 capitalize">{selectedInteraction.source}</span>
                </div>
              </div>
              {selectedInteraction.topics_discussed && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Topics Discussed:</span>
                  <p className="text-sm text-gray-600 mt-1">{selectedInteraction.topics_discussed}</p>
                </div>
              )}
              {selectedInteraction.summary && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-blue-700 flex items-center gap-1">
                    <Sparkles className="w-4 h-4" />
                    AI Summary
                  </span>
                  <p className="text-sm text-blue-600 mt-1">{selectedInteraction.summary}</p>
                </div>
              )}
              {selectedInteraction.outcomes && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Outcomes:</span>
                  <p className="text-sm text-gray-600 mt-1">{selectedInteraction.outcomes}</p>
                </div>
              )}
              {selectedInteraction.key_insights && selectedInteraction.key_insights.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Key Insights:</span>
                  <ul className="text-sm text-gray-600 mt-1 list-disc list-inside">
                    {selectedInteraction.key_insights.map((insight, i) => (
                      <li key={i}>{insight}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedInteraction.follow_up_actions && selectedInteraction.follow_up_actions.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Suggested Follow-ups:</span>
                  <ul className="text-sm text-gray-600 mt-1 list-disc list-inside">
                    {selectedInteraction.follow_up_actions.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}