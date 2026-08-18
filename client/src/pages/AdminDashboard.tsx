import Dashboard, { NavPage } from "./Dashboard";

interface AdminDashboardProps {
  onNavigate: (page: string) => void;
  initialPage?: NavPage;
}

export default function AdminDashboard({
  onNavigate,
  initialPage,
}: AdminDashboardProps) {
  return (
    <Dashboard
      onNavigate={onNavigate}
      initialPage={initialPage}
    />
  );
}