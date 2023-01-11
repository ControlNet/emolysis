type OverallBaseCsvRow = {
    file_id: string,
    start: string,
    end: string,
}

type OverallArousalCsvRow = OverallBaseCsvRow & {
    arousal_continuous: string,
}

type OverallValenceCsvRow = OverallBaseCsvRow & {
    valence_continuous: string,
}

type OverallEmotionCsvRow = OverallBaseCsvRow & {
    emotion: string,
    llr: string,
}

type OverallCsv<T extends OverallBaseCsvRow> = Array<T>

export interface OverallRow {
    frame: number,
    valence: number
    arousal: number
    emotionProb: Array<number>
}

type OverallData = Map<number, OverallRow>
const overallData: OverallData = new Map();

// async function processArousalData() {
//     const dataPathStore = useDataPathStore()
//     const d = await d3.dsv("\t", dataPathStore.arousalDataPath) as OverallCsv<OverallArousalCsvRow>
//     return smoothArrayBy(_.sortBy(_.flatMap(d, row => {
//         const start = parseInt(row.start) * config.fps
//         const end = parseInt(row.end) * config.fps
//         const arousal = parseFloat(row.arousal_continuous)
//         return _.range(start, end).map(frame => {
//             return {
//                 frame,
//                 arousal
//             }
//         })
//     }), row => row.frame), 300, "arousal")
// }
//
// async function processValenceData() {
//     const dataPathStore = useDataPathStore()
//     const d = await d3.dsv("\t", dataPathStore.valenceDataPath) as OverallCsv<OverallValenceCsvRow>
//     return smoothArrayBy(_.sortBy(_.flatMap(d, row => {
//         const start = parseInt(row.start) * config.fps
//         const end = parseInt(row.end) * config.fps
//         const valence = parseFloat(row.valence_continuous)
//         return _.range(start, end).map(frame => {
//             return {
//                 frame,
//                 valence
//             }
//         })
//     }), row => row.frame), 300, "valence")
// }
//
// async function processEmotionData() {
//     const dataPathStore = useDataPathStore()
//     const d = await d3.dsv("\t", dataPathStore.emotionDataPath) as OverallCsv<OverallEmotionCsvRow>
//     return smoothArrayBy(_.sortBy(_.flatMap(d, row => {
//         const start = parseInt(row.start) * config.fps
//         const end = parseInt(row.end) * config.fps
//         const emotion = row.emotion === "none" ? "neutral" : row.emotion
//         const emotion_llr = parseFloat(row.llr)
//         return _.range(start, end).map(frame => {
//             return {
//                 frame,
//                 emotion,
//                 emotion_prob: llr2prob(emotion_llr)
//             }
//         })
//     }), row => row.frame), 300, "emotion_prob")
// }
//
//
// async function loadOverallData() {
//     const [emotionData, valenceData, arousalData] = await Promise.all(
//         [processEmotionData(), processValenceData(), processArousalData()]
//     );
//
//     for (let i = 0; i < emotionData.length; i++) {
//         if (arousalData[i].frame !== valenceData[i].frame || arousalData[i].frame !== emotionData[i].frame) {
//             throw new Error("Frame mismatch")
//         }
//
//         const arousal = arousalData[i].arousal
//         const valence = valenceData[i].valence
//         const emotion = emotionData[i].emotion
//         const emotionProb = emotionData[i].emotion_prob
//         overallData.set(i, {
//             frame: i,
//             arousal,
//             valence,
//             emotion,
//             emotionProb
//         })
//     }
// }
//
// export async function getOverallData(): Promise<OverallData> {
//     if (overallData.size === 0) {
//         await loadOverallData()
//     }
//     return overallData
// }
