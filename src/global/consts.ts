export const EMOTIONS = [
    "fear", "anger", "joy", "sadness", "disgust", "surprise", "trust", "anticipation", "neutral"
]

export type MessageStatus =
    "uploaded"
    | "audio"
    | "audio done"
    | "text"
    | "text done"
    | "visual start"
    | "visual"
    | "visual done"
    | "done"
export type MessageProcessData = { current: number, total: number }
export type MessageResultData = { id: string, audio: string, visual: string, text: string }
export type MessageVideoData = { fps: number }

export interface Message<T extends (MessageProcessData | MessageVideoData | MessageResultData | {})> {
    status: MessageStatus,
    data: T
}