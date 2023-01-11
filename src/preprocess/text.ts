import { useDataPathStore } from "@/stores/dataPathStore";
import * as d3 from "d3";
import { config } from "@/config";
import _ from "lodash";

type TextCsv = Array<{
    start: string,
    end: string,
    valence: string,
    arousal: string,
    emotion0: string,
    emotion1: string,
    emotion2: string,
    emotion3: string,
    emotion4: string,
    emotion5: string,
    emotion6: string,
    emotion7: string,
    emotion8: string
}>

type TextData = Map<number, TextRow>

export interface TextRow {
    frame: number
    valence: number
    arousal: number
    emotionProb: Array<number>
}

const textData: TextData = new Map();

async function loadTextData(): Promise<void> {
    const dataPathStore = useDataPathStore()
    const d = await d3.csv(dataPathStore.textDataPath) as TextCsv

    d.forEach(row => {
        const start = parseInt(row.start) * config.fps
        const end = parseInt(row.end) * config.fps
        const valence = _.round(parseFloat(row.valence))
        const arousal = _.round(parseFloat(row.arousal))
        const emotionProb = [row.emotion0, row.emotion1, row.emotion2, row.emotion3, row.emotion4, row.emotion5, row.emotion6, row.emotion7, row.emotion8].map(parseFloat)

        _.range(start, end).forEach(frame => {
            textData.set(frame, {
                frame,
                valence,
                arousal,
                emotionProb
            })
        })
    })
}

export async function getTextData(): Promise<TextData> {
    if (textData.size === 0) {
        await loadTextData()
    }
    return textData
}

export function getTextDataByFrame(frame: number): TextRow | undefined {
    return textData.get(frame)
}