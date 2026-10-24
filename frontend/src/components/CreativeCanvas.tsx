import { useState } from 'react';
import type { PointerEvent } from 'react';
import { Crosshair, ImageOff, LoaderCircle } from 'lucide-react';
import { usePrivateImage } from '../hooks/usePrivateImage';
import { boxStyle, pixelBox, validBox } from '../lib/geometry';
import type { Asset, Box, Run, Target } from '../types';

export const TARGET_COLORS = ['#3b4ee8', '#c46c39', '#568164', '#9b5fa4', '#438797', '#a2872e', '#b65568', '#746eae'];
export type CanvasMode = 'original' | 'heatmap' | 'targets';

interface Props { asset: Asset; targets: Target[]; run?: Run; mode: CanvasMode; opacity: number; selected?: string; onSelect?: (id: string) => void; onDraw?: (box: Box) => void; showCompeting?: boolean }
export function CreativeCanvas({ asset, targets, run, mode, opacity, selected, onSelect, onDraw, showCompeting }: Props) {
  const image = usePrivateImage(`/assets/${asset.id}/image`);
  const heatmap = usePrivateImage(mode === 'heatmap' && run ? `/runs/${run.id}/heatmap.png` : undefined);
  const [start, setStart] = useState<[number, number]>(); const [drag, setDrag] = useState<Box>();
  const point = (event: PointerEvent<HTMLDivElement>): [number, number] => { const rect = event.currentTarget.getBoundingClientRect(); return [Math.max(0, Math.min(1, (event.clientX-rect.left)/rect.width)), Math.max(0, Math.min(1, (event.clientY-rect.top)/rect.height))]; };
  return <div className={`creative-stage ${mode === 'targets' ? 'drawing-mode' : ''}`}>
    {!image ? <div className="canvas-loading" role="status"><LoaderCircle className="spin" size={25} /><span>Loading creative…</span></div> : image.error ? <div className="canvas-loading"><ImageOff /><span>Couldn’t load this creative.</span></div> : <div className="creative-image-shell" style={{ width: Math.min(760, asset.width*530/asset.height), aspectRatio: `${asset.width}/${asset.height}` }} onPointerDown={event => {
      if (mode !== 'targets' || !onDraw || event.button !== 0 || (event.target as HTMLElement).closest('button')) return;
      event.preventDefault(); const p = point(event); setStart(p); setDrag(undefined); event.currentTarget.setPointerCapture(event.pointerId);
    }} onPointerMove={event => { if (start) setDrag(pixelBox(start, point(event), asset.width, asset.height)); }} onPointerUp={event => { if (!start) return; const box = pixelBox(start, point(event), asset.width, asset.height); setStart(undefined); setDrag(undefined); if (validBox(box)) onDraw?.(box); }} onPointerCancel={() => { setStart(undefined); setDrag(undefined); }}>
      <img className="canonical-image" src={image.url} alt={asset.label} draggable={false} />
      {mode === 'heatmap' && heatmap?.url && <img className="heatmap-image" src={heatmap.url} style={{ opacity }} alt="Predicted attention heatmap" draggable={false} />}
      {mode === 'heatmap' && heatmap?.error && <span className="canvas-error" role="alert">Heatmap unavailable. Try reopening this analysis.</span>}
      {(mode === 'targets' || mode === 'heatmap') && targets.map((target, index) => <button key={target.id} className={`target-box ${selected === target.id ? 'selected' : ''}`} style={{ ...boxStyle(target.box, asset.width, asset.height), borderColor: TARGET_COLORS[index % TARGET_COLORS.length], color: TARGET_COLORS[index % TARGET_COLORS.length] }} aria-label={`Select ${target.label} target`} onPointerDown={e => e.stopPropagation()} onClick={() => onSelect?.(target.id)}><span className="target-box-label" style={{ background: TARGET_COLORS[index % TARGET_COLORS.length] }}>{index+1}<span>{target.label}</span></span></button>)}
      {showCompeting && run?.competing_regions?.map((region, index) => <div key={index} className="competing-box" style={boxStyle(region.box, asset.width, asset.height)}><span>{index+1}</span></div>)}
      {drag && <div className="target-box draft-box" style={boxStyle(drag, asset.width, asset.height)} />}
    </div>}
    {mode === 'targets' && <span className="canvas-mode-badge"><Crosshair size={12} /> Draw a target</span>}
  </div>;
}
