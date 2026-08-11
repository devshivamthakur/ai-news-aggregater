interface StatCardProps {
  icon: React.ReactNode;
  iconBg: string;
  value: number | string;
  label: string;
}

export default function StatCard({ icon, iconBg, value, label }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 ${iconBg} rounded-lg flex items-center justify-center`}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{label}</p>
        </div>
      </div>
    </div>
  );
}
