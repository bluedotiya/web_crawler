import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

export default function NotFound() {
  return (
    <div className="text-center py-16 space-y-4">
      <h1 className="text-4xl font-bold text-gray-900">404</h1>
      <p className="text-gray-500">Page not found</p>
      <Link to="/">
        <Button variant="outline">Go to Dashboard</Button>
      </Link>
    </div>
  );
}
