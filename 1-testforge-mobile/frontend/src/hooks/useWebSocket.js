import { useEffect, useRef, useCallback } from "react";
import { io } from "socket.io-client";

const WS_URL = process.env.REACT_APP_WS_URL || "";

export function useWebSocket(onSessionUpdate) {
  const socketRef = useRef(null);
  const cbRef = useRef(onSessionUpdate);
  cbRef.current = onSessionUpdate;

  useEffect(() => {
    //const socket = io(WS_URL, { transports: ["websocket"], reconnectionDelay: 2000 });
    const socket = io(WS_URL, { transports: ["websocket"], reconnectionDelay: 2000 });
    socketRef.current = socket;

    socket.on("session_update", (data) => cbRef.current(data));
    socket.on("connect_error", (err) => console.warn("WS error:", err.message));

    return () => socket.disconnect();
  }, []);

  const emit = useCallback((event, data) => {
    socketRef.current?.emit(event, data);
  }, []);

  return { emit };
}
