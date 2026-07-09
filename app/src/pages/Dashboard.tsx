/*
 * =============================================================================
 * AI-First CRM HCP Module - Dashboard Page
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Main dashboard with key metrics and recent activity
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  ClipboardList,
  CalendarCheck,
  TrendingUp,
  Activity,
  ArrowRight,
  MessageSquare,
  Clock,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { RootState } from '@/store';
import { fetchRecentInteractions } from '@/store/interactionSlice';
import { fetchHCPs } from '@/store/hcpSlice';
import type { AppDispatch } from '@/store';

export default function Dashboard() {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { recent, items: interactions } = useSelector((state: RootState) => state.interactions);
  const { items: hcps, total: hcpTotal } = useSelector((state: RootState) => state.hcps);

  useEffect(() => {
    dispatch(fetchRecentInteractions(5));
    dispatch(fetchHCPs({ page: 1, pageSize: 5 }));
  }, [dispatch]);

  const stats = [
    {
      title: 'Total HCPs',
      value: hcpTotal,
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      path: '/hcps',
    },
    {
      title: 'Interactions',
      value: interactions.length,
      icon: ClipboardList,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      path: '/interactions',
    },
    {
      title: 'Pending Follow-ups',
      value: 0,
      icon: CalendarCheck,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      path: '/follow-ups',
    },
    {
      title: 'Engagement Rate',
      value: '87%',
      icon: TrendingUp,
      color: 'text-violet-600',
      bg: 'bg-violet-50',
      path: '/interactions',
    },
  ];

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-700';
      case 'negative': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Welcome back!</h2>
        <p className="text-gray-500 mt-1">Here&apos;s what&apos;s happening with your HCP engagements today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card
              key={stat.title}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate(stat.path)}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Log */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Recent Interactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recent.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <ClipboardList className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No interactions yet. Start by logging your first interaction!</p>
                <Button
                  className="mt-4"
                  onClick={() => navigate('/log-interaction')}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Log Interaction
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {recent.map((interaction) => (
                  <div
                    key={interaction.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => navigate('/interactions')}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
                        <MessageSquare className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {interaction.interaction_type}
                        </p>
                        <p className="text-xs text-gray-500">
                          {interaction.topics_discussed
                            ? interaction.topics_discussed.substring(0, 60) + '...'
                            : 'No topics recorded'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getSentimentColor(interaction.sentiment)}>
                        {interaction.sentiment}
                      </Badge>
                      <span className="text-xs text-gray-400">
                        {interaction.date
                          ? new Date(interaction.date).toLocaleDateString()
                          : ''}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent HCPs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              Recent HCPs
            </CardTitle>
          </CardHeader>
          <CardContent>
            {hcps.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No HCPs added yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {hcps.slice(0, 5).map((hcp) => (
                  <div
                    key={hcp.id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate('/hcps')}
                  >
                    <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center text-sm font-semibold text-gray-600">
                      {hcp.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{hcp.full_name}</p>
                      <p className="text-xs text-gray-500 truncate">{hcp.specialty || 'No specialty'}</p>
                    </div>
                    <div className="flex items-center text-xs text-gray-400">
                      <Clock className="w-3 h-3 mr-1" />
                      {hcp.interaction_count || 0}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}