import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import type { CrawlStats } from "../types/api";

interface StatsViewProps {
  stats: CrawlStats | null;
}

const STATUS_COLORS: Record<string, string> = {
  completed: "#22c55e",
  pending: "#eab308",
  in_progress: "#6366f1",
  failed: "#ef4444",
};

export function StatsView({ stats }: StatsViewProps) {
  if (!stats) {
    return <p className="text-gray-500 text-center py-16">Loading statistics...</p>;
  }

  const pieData = [
    { name: "Completed", value: stats.status_counts.completed, color: STATUS_COLORS.completed },
    { name: "Pending", value: stats.status_counts.pending, color: STATUS_COLORS.pending },
    { name: "In Progress", value: stats.status_counts.in_progress, color: STATUS_COLORS.in_progress },
    { name: "Failed", value: stats.status_counts.failed, color: STATUS_COLORS.failed },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-6">
      {/* Metric cards row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-blue-600">{stats.total_urls}</p>
            <p className="text-sm text-gray-500 mt-1">Total URLs</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-indigo-600">{stats.unique_domains}</p>
            <p className="text-sm text-gray-500 mt-1">Unique Domains</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-gray-900">{stats.max_depth_reached}</p>
            <p className="text-sm text-gray-500 mt-1">Max Depth Reached</p>
          </CardContent>
        </Card>
      </div>

      {/* Status distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Status Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
