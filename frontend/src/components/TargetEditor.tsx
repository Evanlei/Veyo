import { Plus, Trash2, Crosshair, ChevronDown } from 'lucide-react';
import { Button } from './Button';
import { TARGET_COLORS } from './CreativeCanvas';
import { percent } from '../lib/format';
import type { Asset, Target } from '../types';

interface Props { asset: Asset; targets: Target[]; selected?: string; onSelect: (id: string) => void; onChange: (targets: Target[]) => void; onAdd: () => void }
export function TargetEditor({ asset, targets, selected, onSelect, onChange, onAdd }: Props) {
  const update = (id: string, patch: Partial<Target>) => onChange(targets.map(t => t.id === id ? { ...t, ...patch } : t));
  return <div className="target-editor"><div className="rail-section-heading"><h3>What should stand out?</h3><span className="count-badge">{targets.length}/8</span></div><p className="small muted">Draw around an element, or add a target and enter its bounds.</p>
    {targets.length === 0 && <div className="target-empty"><Crosshair size={26} strokeWidth={1.4} /><p>Your product? The headline?<br />Give the model a little context.</p></div>}
    <div className="target-list">{targets.map((target, index) => <div key={target.id} className={`target-edit-card ${selected === target.id ? 'expanded' : ''}`}>
      <button className="target-edit-heading" onClick={() => onSelect(target.id)} aria-expanded={selected === target.id}><span className="target-number" style={{ color: TARGET_COLORS[index], background: `${TARGET_COLORS[index]}12` }}>{String(index+1).padStart(2, '0')}</span><strong>{target.label}</strong><span className="target-role">{target.role}</span><ChevronDown size={14} /></button>
      {selected === target.id && <div className="target-edit-fields"><label className="field-label" htmlFor={`label-${target.id}`}>Label</label><input id={`label-${target.id}`} value={target.label} maxLength={80} onChange={e => update(target.id, { label: e.target.value })} /><div className="two-fields"><label>Element<select value={target.role} onChange={e => update(target.id, { role: e.target.value as Target['role'] })}><option value="product">Product</option><option value="headline">Headline</option><option value="logo">Logo / brand</option><option value="cta">Call to action</option><option value="other">Other</option></select></label><label>Priority<select value={target.priority} onChange={e => update(target.id, { priority: Number(e.target.value) })}><option value={3}>Primary</option><option value={2}>Secondary</option><option value={1}>Supporting</option></select></label></div>
        <div className="coordinate-fields">{(['Left', 'Top', 'Right', 'Bottom'] as const).map((label, i) => <label key={label}>{label}<input type="number" min={i < 2 ? 0 : 1} max={i % 2 === 0 ? asset.width : asset.height} value={target.box[i]} onChange={e => { const box = [...target.box] as Target['box']; box[i] = Math.round(Number(e.target.value)); update(target.id, { box }); }} /></label>)}</div><div className="target-edit-footer"><span>{percent((target.box[2]-target.box[0])*(target.box[3]-target.box[1])/(asset.width*asset.height))} of image</span><button className="text-danger" onClick={() => onChange(targets.filter(t => t.id !== target.id))}><Trash2 size={13} /> Remove</button></div>
      </div>}
    </div>)}</div><Button className="full-width" disabled={targets.length >= 8} onClick={onAdd} icon={<Plus size={15} />}>Add a target</Button>
  </div>;
}
