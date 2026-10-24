import { describe, expect, it } from 'vitest';
import { delta, percent, relative, titleFromFile } from './format';

describe('honest presentation of model metrics', () => {
  it('distinguishes probability shares, relative attention, and percentage-point changes', () => {
    expect(percent(.380069)).toBe('38.0%');
    expect(relative(.866)).toBe('0.87×');
    expect(delta(-2.51)).toBe('-2.5 pp');
    expect(delta(2.51)).toBe('+2.5 pp');
  });
  it('creates readable bounded creative names', () => {
    expect(titleFromFile('summer_skincare-v2.jpeg')).toBe('summer skincare v2');
    expect(titleFromFile('.png')).toBe('Untitled creative');
    expect(titleFromFile('x'.repeat(200)+'.png')).toHaveLength(100);
  });
});
