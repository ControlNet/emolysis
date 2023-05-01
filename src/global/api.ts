export const getRemoteUploadApi = () => `/api/upload`
export const getRemoteDataPath = (videoId: string) => `/api/data/${videoId}`;
export const getRemoteDataFps = (videoId: string) => `/api/fps/${videoId}`;
export const getLocalDataPath = (videoId: string) => `/data/${videoId}`
