import Dashboard, { NavPage } from "./Dashboard";

interface UserDashboardProps {
  onNavigate: (page: string) => void;
  initialPage?: NavPage;
}

export default function UserDashboard({
  onNavigate,
  initialPage,
}: UserDashboardProps) {
  return (
    <Dashboard
      onNavigate={onNavigate}
      initialPage={initialPage}
    />
  );
}