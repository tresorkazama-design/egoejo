const RECONNECT_BASE_DELAY = 1500;
const MAX_RECONNECT_DELAY = 15000;

export function createWebSocket(url, { onMessage, onOpen, onClose, protocols } = {}) {
  let socket = null;
  let retryCount = 0;
  let shouldReconnect = true;

  const connect = () => {
    const ws = new WebSocket(url, protocols);
    socket = ws;

    ws.onopen = (event) => {
      retryCount = 0;
      onOpen?.(event, ws);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data, ws);
      } catch (err) {
        console.error("[Realtime] unable to parse message", err);
      }
    };

    ws.onclose = (event) => {
      onClose?.(event, ws);
      if (!shouldReconnect) return;
      const timeout = Math.min(RECONNECT_BASE_DELAY * Math.pow(2, retryCount), MAX_RECONNECT_DELAY);
      retryCount += 1;
      setTimeout(() => connect(), timeout);
    };

    ws.onerror = () => {
      ws.close();
    };
  };

  connect();

  return {
    get instance() {
      return socket;
    },
    close() {
      shouldReconnect = false;
      socket?.close();
    },
    send(payload) {
      if (!socket || socket.readyState !== WebSocket.OPEN) return false;
      socket.send(JSON.stringify(payload));
      return true;
    },
  };
}

export function withFocusThrottling(callback) {
  let pending = false;
  return (...args) => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      callback(...args);
    });
  };
}
