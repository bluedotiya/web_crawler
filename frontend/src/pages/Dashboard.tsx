import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { listCrawls, createCrawl } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { StatusBadge } from "../components/StatusBadge";
import { ProgressBar } from "../components/ProgressBar";

export default function Dashboard() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [depth, setDepth] = useState(2);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const { data } = useQuery({
    queryKey: ["crawls", "recent"],
    queryFn: () => listCrawls({ limit: 5 }),
    refetchInterval: 5000,
  });

  const { data: runningData } = useQuery({
    queryKey: ["crawls", "running-count"],
    queryFn: () => listCrawls({ status: "running", limit: 1 }),
    refetchInterval: 5000,
  });

  const { data: completedData } = useQuery({
    queryKey: ["crawls", "completed-count"],
    queryFn: () => listCrawls({ status: "completed", limit: 1 }),
    refetchInterval: 5000,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setSubmitting(true);
    setError("");
    try {
      const result = await createCrawl(url, depth);
      navigate(`/crawls/${result.crawl_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start crawl");
    } finally {
      setSubmitting(false);
    }
  };

  const runningCount = runningData?.total ?? 0;
  const completedCount = completedData?.total ?? 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Monitor and manage your web crawls</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Crawls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{data?.total ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Running
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">{runningCount}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{completedCount}</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick submit */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Crawl</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-end gap-4">
            <div className="w-full sm:flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL
              </label>
              <Input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>
            <div className="flex items-end gap-4 w-full sm:w-auto">
              <div className="w-24">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Depth
                </label>
                <Input
                  type="number"
                  min={1}
                  max={5}
                  value={depth}
                  onChange={(e) => setDepth(Number(e.target.value))}
                />
              </div>
              <Button type="submit" disabled={submitting}>
                {submitting ? "Starting..." : "Start Crawl"}
              </Button>
            </div>
          </form>
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </CardContent>
      </Card>

      {/* Recent crawls */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Crawls</CardTitle>
          <Link to="/crawls">
            <Button variant="ghost" size="sm">
              View all
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {data?.crawls.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No crawls yet. Start one above!
            </p>
          ) : (
            <div className="space-y-4">
              {data?.crawls.map((crawl) => (
                <Link
                  key={crawl.crawl_id}
                  to={`/crawls/${crawl.crawl_id}`}
                  className="block p-4 rounded-lg border border-gray-100 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 truncate max-w-md">
                      {crawl.root_url.toLowerCase()}
                    </span>
                    <StatusBadge status={crawl.status} />
                  </div>
                  <ProgressBar
                    completed={crawl.completed}
                    total={crawl.total}
                    failed={crawl.failed}
                  />
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
