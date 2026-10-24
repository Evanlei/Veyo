export const percent = (value: number, decimals = 1) => `${(value * 100).toFixed(decimals)}%`;
export const relative = (value: number) => `${value.toFixed(2)}×`;
export const delta = (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(1)} pp`;
export const date = (value: string) => new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(new Date(value));
export const timestamp = (value: string) => new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
export const titleFromFile = (filename: string) => filename.replace(/\.[^.]+$/, '').replace(/[-_]+/g, ' ').trim().slice(0, 100) || 'Untitled creative';
