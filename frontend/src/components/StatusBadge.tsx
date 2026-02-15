import { Badge } from "./ui/badge";

const statusConfig: Record<
  string,
  { variant: "default" | "success" | "warning" | "destructive" | "secondary"; label: string }
> = {
  running: { variant: "default", label: "Running" },
  completed: { variant: "success", label: "Completed" },
  cancelled: { variant: "secondary", label: "Cancelled" },
  failed: { variant: "destructive", label: "Failed" },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || {
    variant: "secondary" as const,
    label: status,
  };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
