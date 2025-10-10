type InvestorDashboardProps = {
  title?: string;
};

export default function InvestorDashboard({ title = "📊 Investor Dashboard" }: InvestorDashboardProps) {
  return <h1>{title}</h1>;
}
