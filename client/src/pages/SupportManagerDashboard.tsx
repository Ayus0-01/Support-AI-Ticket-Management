import Dashboard, { NavPage } from "./Dashboard";

interface SupportManagerDashboardProps {
  onNavigate: (page: string) => void;
  initialPage?: NavPage;
}

export default function SupportManagerDashboard({
  onNavigate,
  initialPage,
}: SupportManagerDashboardProps) {
  return (
    <Dashboard
      onNavigate={onNavigate}
      initialPage={initialPage}
    />
  );
}
