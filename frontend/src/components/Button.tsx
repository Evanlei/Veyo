import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { LoaderCircle } from 'lucide-react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> { variant?: 'primary' | 'secondary' | 'ghost' | 'danger'; busy?: boolean; icon?: ReactNode }
export function Button({ variant = 'secondary', busy = false, icon, children, className = '', disabled, ...props }: Props) {
  return <button {...props} className={`button button-${variant} ${className}`} disabled={disabled || busy} aria-busy={busy}>
    {busy ? <LoaderCircle size={16} className="spin" /> : icon}{children}
  </button>;
}
