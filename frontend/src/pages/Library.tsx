import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowUpRight, Plus, Search, SlidersHorizontal, Grid2X2, FolderOpen, Sparkles } from 'lucide-react';
import { api } from '../lib/api';
import { Button } from '../components/Button';
import { ProjectCard } from '../components/ProjectCard';
import { UploadDialog } from '../components/UploadDialog';
import { EmptyState, ErrorState, Loading } from '../components/States';
import { useToast } from '../components/Toast';
import type { Project } from '../types';

const samples = [{ id: 'forma', name: 'Forma — Everyday essentials', category: 'SKINCARE · PRODUCT FOCUS', color: '#e8edde' }, { id: 'fieldwork', name: 'Fieldwork — A better morning', category: 'COFFEE · BRAND & HEADLINE', color: '#ece0d2' }, { id: 'pace', name: 'Pace — Find your own rhythm', category: 'SPORT · MESSAGE & CTA', color: '#e2e7f1' }];

export function Library() {
  const navigate = useNavigate(); const queryClient = useQueryClient(); const toast = useToast();
  const [uploading, setUploading] = useState(false); const [search, setSearch] = useState(''); const [filter, setFilter] = useState('all'); const [archived, setArchived] = useState(false);
  const query = useQuery({ queryKey: ['projects'], queryFn: api.projects });
  const sample = useMutation({ mutationFn: api.sample, onSuccess: project => { queryClient.invalidateQueries({ queryKey: ['projects'] }); navigate(`/creative/${project.id}`); }, onError: error => toast(error.message, true) });
  const projects = query.data || []; const active = projects.filter(p => !p.archived);
  const visible = projects.filter(p => p.archived === archived && p.name.toLowerCase().includes(search.toLowerCase()) && (filter === 'all' || (filter === 'analyzed' ? p.analysis_count > 0 : p.analysis_count === 0)));
  return <div className="page library-page">
    <div className="page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> YOUR CREATIVE WORKSPACE</div><h1>See what stands out.</h1><p className="page-description">A little evidence. A clearer creative decision.</p></div><Button variant="primary" icon={<Plus size={17} />} onClick={() => setUploading(true)}>New creative</Button></div>
    <div className="library-summary"><span><strong>{active.length.toString().padStart(2, '0')}</strong> creatives in your library</span><span><strong>{active.reduce((sum, p) => sum+p.analysis_count, 0).toString().padStart(2, '0')}</strong> analyses to learn from</span><span className="summary-note"><span className="tiny-dot" /> Your work stays in your workspace</span></div>
    <section aria-labelledby="library-title"><div className="section-toolbar"><div className="section-title"><h2 id="library-title">{archived ? 'Archived creatives' : 'Your creatives'}</h2><span className="count-badge">{visible.length}</span></div><div className="library-controls"><label className="search-field"><Search size={16} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Find a creative…" aria-label="Search creatives" /></label><label className="filter-field"><SlidersHorizontal size={15} /><select aria-label="Filter by analysis status" value={filter} onChange={e => setFilter(e.target.value)}><option value="all">All creatives</option><option value="analyzed">Analyzed</option><option value="new">Needs analysis</option></select></label><button className={`icon-button ${archived ? 'active' : ''}`} aria-label={archived ? 'Show active creatives' : 'Show archived creatives'} aria-pressed={archived} onClick={() => setArchived(!archived)}><FolderOpen size={18} /></button><span className="view-indicator"><Grid2X2 size={16} /></span></div></div>
      {query.isPending ? <Loading /> : query.isError ? <ErrorState message={query.error.message} retry={() => query.refetch()} /> : visible.length ? <div className="project-grid">{visible.map(project => <ProjectCard key={project.id} project={project} />)}</div> : <div className="empty-library"><EmptyState icon={<Grid2X2 size={28} strokeWidth={1.3} />} title={search || filter !== 'all' ? 'No creatives match that view.' : archived ? 'Nothing archived yet.' : 'Your next idea belongs here.'}><p>{search || filter !== 'all' ? 'Try another search or filter.' : 'Upload a creative or explore one of the examples below.'}</p>{!archived && <Button onClick={() => setUploading(true)} icon={<Plus size={15} />}>Add your first creative</Button>}</EmptyState></div>}
    </section>
    <section className="samples-section" aria-labelledby="samples-title"><div className="section-toolbar"><div><div className="eyebrow"><Sparkles size={12} /> A PLACE TO START</div><h2 id="samples-title">Curious? Take a closer look.</h2></div><p className="muted">Three example creatives. Your own fresh analysis.</p></div><div className="sample-grid">{samples.map(item => <button key={item.id} className="sample-card" onClick={() => sample.mutate(item.id)} disabled={sample.isPending}><div className="sample-art" style={{ background: item.color }}><img src={`/samples/${item.id}.png`} alt={`${item.name} sample advertisement`} /></div><div className="sample-copy"><span className="eyebrow">{item.category}</span><h3>{item.name}</h3><span className="text-link">{sample.isPending && sample.variables === item.id ? 'Opening…' : 'Explore creative'} <ArrowUpRight size={15} /></span></div></button>)}</div></section>
    <div className="library-footer"><span className="brand-symbol small" /><p>Thoughtful creative, informed by attention.</p><span>Predictions are a starting point. Your judgment matters.</span></div>
    {uploading && <UploadDialog onClose={() => setUploading(false)} onCreated={value => { const project = value as Project; queryClient.invalidateQueries({ queryKey: ['projects'] }); navigate(`/creative/${project.id}`); }} />}
  </div>;
}
