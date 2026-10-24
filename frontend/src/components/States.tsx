import type { ReactNode } from "react";
import { AlertCircle, ArrowRight, LoaderCircle } from "lucide-react";
import { Button } from "./Button";

export function Loading({
  label = "Opening your workspace…",
}: {
  label?: string;
}) {
  return (
    <div className="state-block" role="status">
      <LoaderCircle className="spin" size={24} />
      <p>{label}</p>
    </div>
  );
}
export function ErrorState({
  message,
  retry,
}: {
  message: string;
  retry?: () => void;
}) {
  return (
    <div className="state-block error-state" role="alert">
      <AlertCircle size={26} />
      <h2>We couldn’t finish that.</h2>
      <p>{message}</p>
      {retry && (
        <Button onClick={retry} icon={<ArrowRight size={16} />}>
          Try again
        </Button>
      )}
    </div>
  );
}
export function EmptyState({
  icon,
  title,
  children,
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="state-block">
      {icon}
      <h3>{title}</h3>
      {children}
    </div>
  );
}
