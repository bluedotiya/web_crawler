import { useRef, useCallback, useMemo } from "react";
import ForceGraph2D, {
  type ForceGraphMethods,
  type NodeObject,
} from "react-force-graph-2d";
import type { GraphData } from "../types/api";

interface GraphViewProps {
  data: GraphData;
}

interface CrawlNode {
  label: string;
  depth: number;
  status: string;
  nodeType: string;
  val: number;
}

const STATUS_COLORS: Record<string, string> = {
  root: "#3b82f6",
  COMPLETED: "#22c55e",
  PENDING: "#eab308",
  "IN-PROGRESS": "#6366f1",
  FAILED: "#ef4444",
  CANCELLED: "#9ca3af",
};

export function GraphView({ data }: GraphViewProps) {
  const fgRef = useRef<ForceGraphMethods<NodeObject<CrawlNode>> | undefined>(
    undefined
  );

  const graphData = useMemo(() => {
    const nodes = data.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      depth: n.depth,
      status: n.status,
      nodeType: n.node_type,
      val: n.node_type === "ROOT" ? 3 : 1,
    }));

    const links = data.edges.map((e) => ({
      source: e.source,
      target: e.target,
    }));

    return { nodes, links };
  }, [data]);

  const activeStatuses = useMemo(() => {
    const statuses = new Set<string>();
    data.nodes.forEach((n) => {
      if (n.node_type === "ROOT") statuses.add("root");
      else if (n.status) statuses.add(n.status);
    });
    return Object.entries(STATUS_COLORS).filter(([s]) => statuses.has(s));
  }, [data]);

  const handleEngineStop = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
  }, []);

  const nodeColor = useCallback(
    (node: NodeObject<CrawlNode>) => {
      return STATUS_COLORS[node.status || ""] || "#9ca3af";
    },
    []
  );

  const nodeLabel = useCallback(
    (node: NodeObject<CrawlNode>) => {
      return `${node.label}\nDepth: ${node.depth}\nStatus: ${node.status}`;
    },
    []
  );

  if (data.nodes.length === 0) {
    return (
      <p className="text-gray-500 text-center py-16">
        No graph data available
      </p>
    );
  }

  return (
    <div
      className="relative border rounded-lg overflow-hidden bg-gray-900"
      style={{ height: 600 }}
    >
      <ForceGraph2D<NodeObject<CrawlNode>>
        ref={fgRef}
        graphData={graphData}
        nodeColor={nodeColor}
        nodeLabel={nodeLabel}
        nodeRelSize={6}
        linkColor={() => "rgba(255,255,255,0.15)"}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        backgroundColor="#111827"
        onEngineStop={handleEngineStop}
        cooldownTicks={100}
        width={undefined}
        height={600}
      />
      <div className="absolute bottom-4 left-4 flex gap-3 bg-gray-800/80 rounded-lg p-2">
        {activeStatuses.map(([status, color]) => (
          <div key={status} className="flex items-center gap-1">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-gray-300 capitalize">{status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
