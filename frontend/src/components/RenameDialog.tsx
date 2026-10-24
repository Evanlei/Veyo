import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Modal } from './Modal';
import { Button } from './Button';

export function RenameDialog({ projectId, initial, onClose, onSaved }: { projectId: string; initial: string; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(initial);
  const mutation = useMutation({ mutationFn: () => api.update(projectId, { name }), onSuccess: onSaved });
  return <Modal title="Name your creative." onClose={onClose}><form onSubmit={event => { event.preventDefault(); mutation.mutate(); }}><label className="field-label" htmlFor="project-name">Creative name</label><input id="project-name" value={name} onChange={event => setName(event.target.value)} required maxLength={100} autoFocus />{mutation.error && <p className="inline-error" role="alert">{mutation.error.message}</p>}<div className="modal-actions"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary" type="submit" disabled={!name.trim()} busy={mutation.isPending}>Save name</Button></div></form></Modal>;
}
