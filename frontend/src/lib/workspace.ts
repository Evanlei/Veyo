const STORAGE_KEY = 'veyo.workspace.v1';

export function workspaceKey(): string {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved && /^[a-f0-9]{64}$/.test(saved)) return saved;
  const key = Array.from(crypto.getRandomValues(new Uint8Array(32)), n => n.toString(16).padStart(2, '0')).join('');
  localStorage.setItem(STORAGE_KEY, key);
  return key;
}

export function importWorkspace(key: string): void {
  if (!/^[a-f0-9]{64}$/.test(key.trim())) throw new Error('Use the complete 64-character workspace key.');
  localStorage.setItem(STORAGE_KEY, key.trim());
}
