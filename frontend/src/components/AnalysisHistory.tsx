import { Check, Clock3, AlertCircle, ArrowUpRight } from 'lucide-react';
import { percent, timestamp } from '../lib/format';
import type { Run } from '../types';

export function AnalysisHistory({ runs, selectedId, onSelect }: { runs: Run[]; selectedId?: string; onSelect: (id: string) => void }) {
  if (!runs.length) return null;
  return <section className="history-section"><div className="section-title"><Clock3 size={16} /><h3>Analysis history</h3><span className="count-badge">{runs.length}</span></div><div className="history-list">{runs.map((run, index) => <button key={run.id} className={`history-row ${selectedId === run.id ? 'active' : ''}`} disabled={run.status !== 'completed'} onClick={() => onSelect(run.id)}><span className={`run-status ${run.status}`}>{run.status === 'completed' ? <Check size={13} /> : run.status === 'failed' ? <AlertCircle size={13} /> : <Clock3 size={13} />}</span><div><strong>Analysis {runs.length-index}</strong><small>{timestamp(run.created_at)}{run.cached ? ' · cached prediction' : ''}</small></div><span>{run.metrics ? percent(run.metrics.attention_share) : run.status === 'failed' ? 'Failed' : 'In progress'}</span><ArrowUpRight size={14} /></button>)}</div></section>;
}
