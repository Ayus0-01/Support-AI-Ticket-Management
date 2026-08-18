import Dashboard, { NavPage } from "./Dashboard";

interface AgentDashboardProps {
  onNavigate: (page: string) => void;
  initialPage?: NavPage;
}

export default function AgentDashboard({
  onNavigate,
  initialPage,
}: AgentDashboardProps) {
  return (
    <Dashboard
      onNavigate={onNavigate}
      initialPage={initialPage}
    />
  );
}