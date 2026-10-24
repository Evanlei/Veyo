import { describe, expect, it } from 'vitest';
import { boxStyle, pixelBox, validBox } from './geometry';

describe('canonical target geometry', () => {
  it('maps reversed drags to the same integer region', () => {
    expect(pixelBox([.8, .9], [.1, .2], 1000, 500)).toEqual([100, 100, 800, 450]);
  });
  it('clamps pointer positions to the image', () => {
    expect(pixelBox([-.1, -.2], [1.2, 1.1], 100, 80)).toEqual([0, 0, 100, 80]);
  });
  it('keeps display boxes proportional to the canonical grid', () => {
    expect(boxStyle([10, 20, 60, 80], 100, 100)).toEqual({ left: '10%', top: '20%', width: '50%', height: '60%' });
    expect(validBox([1, 1, 2, 2])).toBe(false);
  });
});
