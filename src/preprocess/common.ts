export interface DataRow {
    frame: number
    valence: number
    arousal: number
    emotionProb: Array<number>
}

export type Data = Map<number, DataRow>
