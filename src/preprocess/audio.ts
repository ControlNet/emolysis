import { useDataPathStore } from "@/stores/dataPathStore";
import * as d3 from "d3";
import { config } from "@/config";
import _ from "lodash";
import type { DataRow } from "@/preprocess/common";

type AudioCsv = Array<{
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

type AudioData = Map<number, AudioRow>

export interface AudioRow extends DataRow {}

const audioData: AudioData = new Map();

async function loadAudioData(): Promise<void> {
    const dataPathStore = useDataPathStore()
    const d = await d3.csv(dataPathStore.audioDataPath) as AudioCsv

    d.forEach(row => {
        const start = parseInt(row.start) * config.fps
        const end = parseInt(row.end) * config.fps
        const valence = _.round(parseFloat(row.valence))
        const arousal = _.round(parseFloat(row.arousal))
        const emotionProb = [row.emotion0, row.emotion1, row.emotion2, row.emotion3, row.emotion4, row.emotion5, row.emotion6, row.emotion7, row.emotion8].map(parseFloat)

        _.range(start, end).forEach(frame => {
            audioData.set(frame, {
                frame,
                valence,
                arousal,
                emotionProb
            })
        })
    })
}

export async function getAudioData(): Promise<AudioData> {
    if (audioData.size === 0) {
        await loadAudioData()
    }
    return audioData
}

export function getAudioDataByFrame(frame: number): AudioRow | undefined {
    return audioData.get(frame)
}