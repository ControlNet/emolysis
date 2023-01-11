import { useDataPathStore } from "@/stores/dataPathStore";
import * as d3 from "d3";

type FaceCsv = Array<{
    frame: string,
    x1: string,
    x2: string,
    y1: string,
    y2: string,
    box_prob: string,
    emotion: string,
    emotion0: string,
    emotion1: string,
    emotion2: string,
    emotion3: string,
    emotion4: string,
    emotion5: string,
    emotion6: string,
    emotion7: string,
    emotion8: string,
    valence: string,
    arousal: string,
}>

type FaceData = Map<number, Array<FaceRow>>

export interface FaceRow {
    frame: number
    x1: number
    x2: number
    y1: number
    y2: number
    boxProb: number
    valence: number
    arousal: number
    emotionProb: Array<number>
}

export interface VisualRow {
    frame: number
    valence: number
    arousal: number
    emotionProb: Array<number>
}

const faceData: FaceData = new Map();

async function loadFaceData(): Promise<void> {
    const dataPathStore = useDataPathStore()
    const d = await d3.csv(dataPathStore.faceDataPath) as FaceCsv
    d.forEach(row => {
        const currentFrame = parseInt(row.frame)
        const faceRow = {
            frame: currentFrame,
            x1: parseInt(row.x1),
            x2: parseInt(row.x2),
            y1: parseInt(row.y1),
            y2: parseInt(row.y2),
            boxProb: parseFloat(row.box_prob),
            valence: parseInt(row.valence),
            arousal: parseInt(row.arousal),
            emotion: parseInt(row.emotion),
            emotionProb: [row.emotion0, row.emotion1, row.emotion2, row.emotion3, row.emotion4, row.emotion5, row.emotion6, row.emotion7, row.emotion8].map(parseFloat)
        }
        if (faceData.has(currentFrame)) {
            faceData.get(currentFrame)!.push(faceRow)
        } else {
            faceData.set(currentFrame, [faceRow])
        }
    })
}

export async function getFaceData(): Promise<FaceData> {
    if (faceData.size === 0) {
        await loadFaceData()
    }
    return faceData
}

export function getFaceDataByFrame(frame: number): Array<FaceRow> {
    return faceData.get(frame) ?? []
}
