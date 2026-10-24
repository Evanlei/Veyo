import type { Box } from '../types';

export function pixelBox(start: [number, number], end: [number, number], width: number, height: number): Box {
  const x = (v: number) => Math.max(0, Math.min(width, Math.round(v * width)));
  const y = (v: number) => Math.max(0, Math.min(height, Math.round(v * height)));
  return [x(Math.min(start[0], end[0])), y(Math.min(start[1], end[1])), x(Math.max(start[0], end[0])), y(Math.max(start[1], end[1]))];
}

export function boxStyle(box: Box, width: number, height: number) {
  return { left: `${box[0] / width * 100}%`, top: `${box[1] / height * 100}%`, width: `${(box[2]-box[0]) / width * 100}%`, height: `${(box[3]-box[1]) / height * 100}%` };
}

export const validBox = (box: Box) => box[2] - box[0] >= 3 && box[3] - box[1] >= 3;
