let socket: WebSocket | undefined = undefined;

export function getSocket() {
    if (socket === undefined || socket.readyState === WebSocket.CLOSED) {
        socket = new WebSocket(`ws://${import.meta.env.VITE_API_URL}/`)
    }
    return socket;
}

export function closeSocket() {
    if (socket !== undefined) {
        socket.close();
        socket = undefined;
    }
}
