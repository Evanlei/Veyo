import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { ReactNode } from "react";
import { Check, X } from "lucide-react";

const ToastContext = createContext<(message: string, error?: boolean) => void>(
  () => {},
);
export const useToast = () => useContext(ToastContext);
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<{
    message: string;
    error: boolean;
    id: number;
  }>();
  const show = useCallback(
    (message: string, error = false) =>
      setToast({ message, error, id: Date.now() }),
    [],
  );
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(
      () => setToast(undefined),
      toast.error ? 9000 : 4500,
    );
    return () => clearTimeout(timer);
  }, [toast]);
  return (
    <ToastContext.Provider value={show}>
      {children}
      <div className="toast-region" aria-live="polite">
        {toast && (
          <div className={`toast ${toast.error ? "toast-error" : ""}`}>
            {toast.error ? <X size={18} /> : <Check size={18} />}
            <span>{toast.message}</span>
            <button
              aria-label="Dismiss notification"
              onClick={() => setToast(undefined)}
            >
              <X size={16} />
            </button>
          </div>
        )}
      </div>
    </ToastContext.Provider>
  );
}
