import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, ArrowUpRight, Archive, Check, Download, Info, Layers2, LoaderCircle, Pencil, Save, SlidersHorizontal } from 'lucide-react';
import { api } from '../lib/api';
import { Button } from '../components/Button';
import { CreativeCanvas } from '../components/CreativeCanvas';
import type { CanvasMode } from '../components/CreativeCanvas';
import { TargetEditor } from '../components/TargetEditor';
import { AttentionMetrics } from '../components/AttentionMetrics';
import { Insights } from '../components/Insights';
import { AnalysisHistory } from '../components/AnalysisHistory';
import { RevisionStrip } from '../components/RevisionStrip';
import { UploadDialog } from '../components/UploadDialog';
import { AdjustmentDialog } from '../components/AdjustmentDialog';
import { ExportDialog } from '../components/ExportDialog';
import { RenameDialog } from '../components/RenameDialog';
import { ErrorState, Loading } from '../components/States';
import { useToast } from '../components/Toast';
import type { Asset, Box, Project, Target } from '../types';

export function Workspace() {
  const { projectId = '' } = useParams(); const [params] = useSearchParams();
  const query = useQuery({ queryKey: ['project', projectId], queryFn: () => api.project(projectId) });
  if (query.isPending) return <Loading label="Opening your creative…" />;
  if (query.isError) return <ErrorState message={query.error.message} retry={() => query.refetch()} />;
  const asset = query.data.assets.find(a => a.id === params.get('asset')) || query.data.assets.at(-1);
  if (!asset) return <ErrorState message="This project has no creative images." />;
  return <WorkspaceContent key={`${projectId}:${asset.id}`} project={query.data} asset={asset} />;
}

function WorkspaceContent({ project, asset }: { project: Project; asset: Asset }) {
  const queryClient = useQueryClient(); const navigate = useNavigate(); const [, setParams] = useSearchParams(); const toast = useToast();
  const runs = project.runs.filter(run => run.asset_id === asset.id); const latest = runs.find(run => run.status === 'completed');
  const [targets, setTargets] = useState<Target[]>(asset.targets); const [dirty, setDirty] = useState(false);
  const [runId, setRunId] = useState(latest?.id); const run = runs.find(r => r.id === runId);
  const [mode, setMode] = useState<CanvasMode>(latest ? 'heatmap' : 'targets');
  const [selected, setSelected] = useState<string | undefined>(asset.targets[0]?.id);
  const [opacity, setOpacity] = useState(.65); const [showCompeting, setShowCompeting] = useState(false);
  const [dialog, setDialog] = useState<'upload' | 'adjust' | 'export' | 'rename'>();
  const refresh = async () => { await Promise.all([queryClient.invalidateQueries({ queryKey: ['project', project.id] }), queryClient.invalidateQueries({ queryKey: ['projects'] })]); };
  useEffect(() => { if (!dirty) return; const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ''; }; window.addEventListener('beforeunload', warn); return () => window.removeEventListener('beforeunload', warn); }, [dirty]);
  const save = useMutation({ mutationFn: () => api.targets(asset.id, targets), onSuccess: async () => { setDirty(false); toast('Targets saved.'); await refresh(); }, onError: error => toast(error.message, true) });
  const analyze = useMutation({ mutationFn: async () => { await api.targets(asset.id, targets); setDirty(false); return api.analyze(asset.id); }, onSuccess: async result => { await refresh(); setRunId(result.id); setMode('heatmap'); toast('Analysis complete. Take a closer look.'); }, onError: async error => { toast(error.message, true); await refresh(); } });
  const archive = useMutation({ mutationFn: () => api.update(project.id, { archived: !project.archived }), onSuccess: async () => { await refresh(); toast(project.archived ? 'Creative restored to your library.' : 'Creative archived. You can restore it from the library.'); navigate('/'); }, onError: error => toast(error.message, true) });
  const busy = save.isPending || analyze.isPending;
  const changeTargets = (next: Target[]) => { setTargets(next); setDirty(true); setMode('targets'); };
  const draw = (box: Box) => { if (targets.length >= 8) { toast('Use up to eight targets per creative.'); return; } const id = crypto.randomUUID(); changeTargets([...targets, { id, label: `Target ${targets.length+1}`, role: 'product', box, priority: 1 }]); setSelected(id); };
  const selectAsset = (id: string) => { if (dirty && !window.confirm('Leave this version and discard unsaved target changes?')) return; setParams({ asset: id }); };
  const created = async (value: Asset | Project) => { const revision = value as Asset; setDialog(undefined); await refresh(); setParams({ asset: revision.id }); toast('Revision added. Review its targets before analyzing.'); };
  const displayTargets = mode === 'heatmap' && run ? run.targets : targets;
  return <div className="page workspace-page">
    <div className="breadcrumb"><Link to="/"><ArrowLeft size={13} /> Creative library</Link><span>/</span><span>{project.name}</span></div>
    <div className="page-heading workspace-heading"><div><div className="eyebrow">CREATIVE REVIEW <span> / </span> {asset.label.toUpperCase()}</div><h1>{project.name}<button className="icon-button" onClick={() => setDialog('rename')} aria-label="Rename creative"><Pencil size={16} /></button></h1></div><div className="heading-actions"><Button icon={<Archive size={15} />} busy={archive.isPending} onClick={() => archive.mutate()}>{project.archived ? 'Restore' : 'Archive'}</Button><Button icon={<Download size={15} />} onClick={() => setDialog('export')}>Export</Button></div></div>
    <div className="workspace-grid"><div className="workspace-main"><section className="canvas-panel"><div className="canvas-toolbar"><div className="segmented-control" aria-label="Creative view">{(['original', 'heatmap', 'targets'] as const).map(view => <button key={view} className={mode === view ? 'active' : ''} disabled={view === 'heatmap' && !run} aria-pressed={mode === view} onClick={() => setMode(view)}>{view === 'original' ? 'Original' : view === 'heatmap' ? 'Heatmap' : 'Targets'}</button>)}</div><span className="canvas-dimensions">{asset.width} × {asset.height}</span></div>
      <div className="canvas-container"><CreativeCanvas asset={asset} targets={displayTargets} run={run} mode={mode} opacity={opacity} selected={selected} onSelect={setSelected} onDraw={busy ? undefined : draw} showCompeting={mode === 'heatmap' && showCompeting} />{analyze.isPending && <div className="analysis-scrim" role="status"><span className="analysis-orbit"><LoaderCircle size={28} className="spin" /></span><strong>Finding what stands out…</strong><p>Running a real attention prediction.<br />The first analysis may take a minute.</p></div>}</div>
      <div className="canvas-footer">{mode === 'heatmap' ? <><div className="heatmap-legend"><span>Less</span><span className="heatmap-gradient" /><span>More predicted attention</span></div><label className="opacity-control">Overlay<input aria-label="Heatmap opacity" type="range" min="0" max="1" step="0.05" value={opacity} onChange={e => setOpacity(Number(e.target.value))} /></label></> : <p><Info size={13} />{mode === 'targets' ? 'Drag around an element. Targets use the same pixels as the prediction.' : 'Your creative, without overlays.'}</p>}</div></section>
      {asset.provenance.resized && <p className="small muted resize-note">Prepared from {asset.provenance.source_width} × {asset.provenance.source_height} to {asset.width} × {asset.height} for analysis.</p>}
      <div className="creative-actions"><Button icon={<SlidersHorizontal size={15} />} onClick={() => setDialog('adjust')} disabled={busy}>Try an adjustment</Button><Link className="button button-ghost" to={`/compare/${project.id}`}><Layers2 size={15} />Compare versions<ArrowUpRight size={14} /></Link></div>
      <RevisionStrip assets={project.assets} runs={project.runs} selectedId={asset.id} onSelect={selectAsset} onUpload={() => setDialog('upload')} />
      <AnalysisHistory runs={runs} selectedId={runId} onSelect={id => { setRunId(id); setMode('heatmap'); }} />
    </div><aside className="evidence-rail">
      {mode === 'heatmap' && run ? <AttentionMetrics run={run} selected={selected} onSelect={setSelected} /> : <fieldset className="unstyled-fieldset" disabled={busy}><TargetEditor asset={asset} targets={targets} selected={selected} onSelect={setSelected} onChange={changeTargets} onAdd={() => draw([Math.round(asset.width*.25), Math.round(asset.height*.25), Math.round(asset.width*.75), Math.round(asset.height*.75)])} /></fieldset>}
      <div className="analysis-controls">{(dirty || !asset.confirmed) && <div className="annotation-status"><span className="tiny-dot" />{dirty ? 'Unsaved target changes' : 'Review and confirm these targets'}</div>}{dirty && <Button className="full-width" icon={<Save size={15} />} busy={save.isPending} onClick={() => save.mutate()}>Save targets</Button>}<Button className="full-width" variant="primary" icon={<ArrowUpRight size={16} />} busy={analyze.isPending} disabled={targets.length === 0 || busy || targets.some(t => !t.label.trim())} onClick={() => analyze.mutate()}>{analyze.isPending ? 'Analyzing creative' : run ? 'Run analysis again' : 'Run analysis'}</Button><p className="analysis-save-note"><Check size={12} /> Results save automatically</p></div>
      {run && mode === 'heatmap' && <Insights run={run} showCompeting={showCompeting} onToggleCompeting={() => setShowCompeting(!showCompeting)} />}
      <div className="interpretation-note"><span className="eyebrow">PERSPECTIVE, NOT A PROMISE</span><p>Predicted attention helps you compare ideas. It doesn’t predict clicks, sales, or measured human attention.</p>{run?.model && <details><summary>About this prediction</summary><p>{run.model.model} · {run.model.device.toUpperCase()} · uniform spatial prior<br />{run.cached ? 'Reused the saved prediction for this image.' : `${run.seconds}s analysis.`}<br />Source {run.model.source_commit?.slice(0, 8)}</p></details>}</div>
    </aside></div>
    {dialog === 'upload' && <UploadDialog projectId={project.id} parentId={asset.id} onClose={() => setDialog(undefined)} onCreated={created} />}
    {dialog === 'adjust' && <AdjustmentDialog asset={asset} onClose={() => setDialog(undefined)} onCreated={created} />}
    {dialog === 'export' && <ExportDialog projectId={project.id} asset={asset} run={run} onClose={() => setDialog(undefined)} />}
    {dialog === 'rename' && <RenameDialog projectId={project.id} initial={project.name} onClose={() => setDialog(undefined)} onSaved={async () => { setDialog(undefined); await refresh(); }} />}
  </div>;
}
