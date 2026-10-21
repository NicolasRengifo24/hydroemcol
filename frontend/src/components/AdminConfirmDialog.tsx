import { useEffect, useRef } from "react";
import { AlertTriangle, X } from "lucide-react";

type AdminConfirmDialogProps = {
  title: string;
  description: string;
  confirmLabel: string;
  open: boolean;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function AdminConfirmDialog({
  title,
  description,
  confirmLabel,
  open,
  danger = false,
  onConfirm,
  onCancel,
}: AdminConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    cancelRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div className="admin-dialog-backdrop" role="presentation" onMouseDown={onCancel}>
      <section
        className="admin-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="admin-dialog-title"
        aria-describedby="admin-dialog-description"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button className="admin-dialog__close" type="button" onClick={onCancel} aria-label="Cerrar">
          <X size={18} aria-hidden="true" />
        </button>
        <div className={`admin-dialog__icon${danger ? " admin-dialog__icon--danger" : ""}`}>
          <AlertTriangle size={22} aria-hidden="true" />
        </div>
        <h2 id="admin-dialog-title">{title}</h2>
        <p id="admin-dialog-description">{description}</p>
        <div className="admin-dialog__actions">
          <button ref={cancelRef} className="admin-button admin-button--secondary" type="button" onClick={onCancel}>
            Volver
          </button>
          <button className={`admin-button${danger ? " admin-button--danger" : ""}`} type="button" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
