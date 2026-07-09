/*
 * =============================================================================
 * AI-First CRM HCP Module - HCP Management Page
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : HCP list, search, and management interface
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Search,
  Plus,
  Trash2,
  Building2,
  MapPin,
  Phone,
  Mail,
  Loader2,
  X,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import type { RootState } from '@/store';
import type { AppDispatch } from '@/store';
import { fetchHCPs, createHCP, deleteHCP } from '@/store/hcpSlice';
import { showToast } from '@/store/uiSlice';

export default function HCPManagement() {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { items: hcps, loading, total } = useSelector((state: RootState) => state.hcps);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // New HCP form
  const [newHcp, setNewHcp] = useState<{
    full_name: string;
    email: string;
    phone: string;
    specialty: string;
    institution: string;
    location: string;
    tier: string;
    notes: string;
    npi_number: string;
    is_active: boolean;
  }>({
    full_name: '',
    email: '',
    phone: '',
    specialty: '',
    institution: '',
    location: '',
    tier: 'general',
    notes: '',
    npi_number: '',
    is_active: true,
  });

  useEffect(() => {
    dispatch(fetchHCPs({ page, pageSize: 20, search: search || undefined }) as any);
  }, [dispatch, page, search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newHcp.full_name.trim()) {
      dispatch(showToast({ type: 'error', message: 'Name is required' }));
      return;
    }
    setIsSubmitting(true);
    try {
      await dispatch(createHCP(newHcp) as any);
      setIsAddOpen(false);
      setNewHcp({
        full_name: '', email: '', phone: '', specialty: '',
        institution: '', location: '', tier: 'general', notes: '',
        npi_number: '', is_active: true,
      });
      dispatch(showToast({ type: 'success', message: 'HCP created successfully!' }));
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to create HCP' }));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this HCP?')) return;
    try {
      await dispatch(deleteHCP(id) as any);
      dispatch(showToast({ type: 'success', message: 'HCP deleted successfully' }));
    } catch {
      dispatch(showToast({ type: 'error', message: 'Failed to delete HCP' }));
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'kol': return 'bg-purple-100 text-purple-700';
      case 'influencer': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Healthcare Professionals</h2>
          <p className="text-gray-500 mt-1">Manage your HCP contacts ({total} total)</p>
        </div>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Add HCP
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Add New HCP</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label htmlFor="name">Full Name *</Label>
                <Input id="name" value={newHcp.full_name} onChange={(e) => setNewHcp({ ...newHcp, full_name: e.target.value })} required />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" value={newHcp.email} onChange={(e) => setNewHcp({ ...newHcp, email: e.target.value })} />
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" value={newHcp.phone} onChange={(e) => setNewHcp({ ...newHcp, phone: e.target.value })} />
                </div>
              </div>
              <div>
                <Label htmlFor="specialty">Specialty</Label>
                <Input id="specialty" value={newHcp.specialty} onChange={(e) => setNewHcp({ ...newHcp, specialty: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="institution">Institution</Label>
                <Input id="institution" value={newHcp.institution} onChange={(e) => setNewHcp({ ...newHcp, institution: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="location">Location</Label>
                <Input id="location" value={newHcp.location} onChange={(e) => setNewHcp({ ...newHcp, location: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="tier">Tier</Label>
                <select
                  id="tier"
                  value={newHcp.tier}
                  onChange={(e) => setNewHcp({ ...newHcp, tier: e.target.value })}
                  className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="general">General</option>
                  <option value="kol">Key Opinion Leader</option>
                  <option value="influencer">Influencer</option>
                </select>
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setIsAddOpen(false)}>
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting} className="bg-blue-600 hover:bg-blue-700">
                  {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Create HCP
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          placeholder="Search by name or institution..."
          className="pl-9"
        />
      </div>

      {/* HCP List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : hcps.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Users className="w-16 h-16 text-gray-300 mb-4" />
            <p className="text-gray-500 text-lg">No HCPs found</p>
            <p className="text-gray-400 text-sm mt-1">Add your first HCP to get started</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {hcps.map((hcp) => (
            <Card key={hcp.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-lg font-bold text-blue-600">
                      {hcp.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{hcp.full_name}</h3>
                      {hcp.specialty && (
                        <p className="text-sm text-gray-500">{hcp.specialty}</p>
                      )}
                    </div>
                  </div>
                  <Badge className={getTierColor(hcp.tier)}>{hcp.tier}</Badge>
                </div>

                <div className="mt-4 space-y-2">
                  {hcp.institution && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      {hcp.institution}
                    </div>
                  )}
                  {hcp.location && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      {hcp.location}
                    </div>
                  )}
                  {hcp.email && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Mail className="w-4 h-4 text-gray-400" />
                      {hcp.email}
                    </div>
                  )}
                  {hcp.phone && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Phone className="w-4 h-4 text-gray-400" />
                      {hcp.phone}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {hcp.interaction_count || 0} interactions
                  </span>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="w-8 h-8"
                      onClick={() => navigate(`/log-interaction?hcp=${hcp.id}`)}
                      title="Log interaction"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="w-8 h-8 text-gray-400 hover:text-red-600"
                      onClick={() => handleDelete(hcp.id)}
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
      {total > 20 && (
        <div className="flex justify-center gap-2 mt-6">
          <Button
            variant="outline"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="flex items-center px-4 text-sm text-gray-600">
            Page {page} of {Math.ceil(total / 20)}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= Math.ceil(total / 20)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}