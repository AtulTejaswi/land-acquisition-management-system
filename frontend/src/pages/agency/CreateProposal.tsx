import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { useCreateProject } from '../../hooks/useProjects';
import { useToast } from '../../components/toast/ToastProvider';

const CATEGORIES = [
  'Highway', 'Railway', 'Irrigation', 'Industrial Corridor',
  'Renewable Energy', 'Smart City', 'Airport', 'Defence', 'Welfare',
];

const PRIORITIES = ['low', 'medium', 'high', 'critical'];

export default function CreateProposal() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const createProject = useCreateProject();

  const [form, setForm] = useState({
    name: '',
    description: '',
    category_name: '',
    state_id: '',
    district_id: '',
    estimated_budget: '',
    estimated_land_required_hectares: '',
    priority: 'medium',
    start_date: '',
    target_completion_date: '',
  });

  const { data: states } = useQuery({
    queryKey: ['states'],
    queryFn: async () => {
      const { data } = await api.get('/dashboard/national');
      return data?.state_progress || [];
    },
  });

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.category_name) {
      toast('Please fill in project name and category', 'warning');
      return;
    }
    try {
      const result = await createProject.mutateAsync({
        name: form.name,
        description: form.description,
        category_name: form.category_name,
        estimated_budget: Number(form.estimated_budget) || 0,
        estimated_land_required_hectares: Number(form.estimated_land_required_hectares) || 0,
        priority: form.priority as any,
        start_date: form.start_date || undefined,
        target_completion_date: form.target_completion_date || undefined,
      });
      toast('Project proposal created successfully!', 'success');
      navigate(`/agency/projects`);
    } catch (err: any) {
      toast(err?.response?.data?.detail || 'Failed to create project', 'error');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-slate-900">➕ Create Project Proposal</h1>
        <p className="text-slate-500 text-sm">Submit a new land acquisition project proposal</p>
      </motion.div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label htmlFor="proposal-name" className="text-sm font-medium text-slate-700">Project Name *</label>
              <Input
                id="proposal-name"
                className="mt-1"
                placeholder="e.g. NH-44 Widening — Nagpur to Betul"
                value={form.name}
                onChange={(e) => handleChange('name', e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="proposal-desc" className="text-sm font-medium text-slate-700">Description</label>
              <textarea
                id="proposal-desc"
                className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm"
                rows={3}
                placeholder="Brief description of the project..."
                value={form.description}
                onChange={(e) => handleChange('description', e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Category *</label>
                <Select value={form.category_name} onValueChange={(v) => handleChange('category_name', v)}>
                  <option value="">Select category</option>
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Priority</label>
                <Select value={form.priority} onValueChange={(v) => handleChange('priority', v)}>
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                  ))}
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="proposal-budget" className="text-sm font-medium text-slate-700">Estimated Budget (₹)</label>
                <Input
                  id="proposal-budget"
                  className="mt-1"
                  type="number"
                  placeholder="e.g. 50000000"
                  value={form.estimated_budget}
                  onChange={(e) => handleChange('estimated_budget', e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="proposal-land" className="text-sm font-medium text-slate-700">Land Required (hectares)</label>
                <Input
                  id="proposal-land"
                  className="mt-1"
                  type="number"
                  step="0.001"
                  placeholder="e.g. 150.500"
                  value={form.estimated_land_required_hectares}
                  onChange={(e) => handleChange('estimated_land_required_hectares', e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="proposal-start" className="text-sm font-medium text-slate-700">Start Date</label>
                <Input
                  id="proposal-start"
                  className="mt-1"
                  type="date"
                  value={form.start_date}
                  onChange={(e) => handleChange('start_date', e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="proposal-end" className="text-sm font-medium text-slate-700">Target Completion Date</label>
                <Input
                  id="proposal-end"
                  className="mt-1"
                  type="date"
                  value={form.target_completion_date}
                  onChange={(e) => handleChange('target_completion_date', e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3 mt-6">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>Cancel</Button>
          <Button type="submit" disabled={createProject.isPending}>
            {createProject.isPending ? 'Creating...' : 'Submit Proposal'}
          </Button>
        </div>
      </form>
    </div>
  );
}
