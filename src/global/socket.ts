let socket: WebSocket | undefined = undefined;

export function getSocket() {
    if (socket === undefined || socket.readyState === WebSocket.CLOSED) {
        socket = new WebSocket(`ws://${window.location.host}/ws/`)
    }
    return socket;
}

export function closeSocket() {
    if (socket !== undefined) {
        socket.close();
        socket = undefined;
    }
}
