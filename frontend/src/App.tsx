import { Routes, Route, Link, useLocation } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import Dashboard from "./pages/Dashboard";
import CrawlList from "./pages/CrawlList";
import NewCrawl from "./pages/NewCrawl";
import CrawlDetail from "./pages/CrawlDetail";
import NotFound from "./pages/NotFound";

function NavLink({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) {
  const location = useLocation();
  const isActive =
    to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);

  return (
    <Link
      to={to}
      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        isActive
          ? "bg-blue-100 text-blue-700"
          : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
      }`}
    >
      {children}
    </Link>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-1">
              <Link to="/" className="text-xl font-bold text-blue-600 mr-6">
                Web Crawler
              </Link>
              <NavLink to="/">Dashboard</NavLink>
              <NavLink to="/crawls">Crawls</NavLink>
              <NavLink to="/new">New Crawl</NavLink>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/crawls" element={<CrawlList />} />
            <Route path="/new" element={<NewCrawl />} />
            <Route path="/crawls/:id" element={<CrawlDetail />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}
