import { useEffect, useRef, useState, useCallback } from "react";
import type { CrawlProgress } from "../types/api";

const MAX_RETRIES = 5;
const MAX_DELAY = 30000;

export function useWebSocket(crawlId: string | undefined) {
  const [progress, setProgress] = useState<CrawlProgress | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef(0);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!crawlId) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/api/v1/crawls/${crawlId}/ws`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      retryCountRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as CrawlProgress;
        setProgress(data);
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;

      if (retryCountRef.current < MAX_RETRIES && crawlId) {
        const delay = Math.min(1000 * 2 ** retryCountRef.current, MAX_DELAY);
        retryCountRef.current += 1;
        retryTimeoutRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [crawlId]);

  useEffect(() => {
    retryCountRef.current = 0;
    connect();
    return () => {
      if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { progress, connected };
}
