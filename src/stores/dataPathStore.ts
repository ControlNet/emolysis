import { defineStore } from 'pinia'
import { getFaceData } from "@/preprocess/faces";
import { getAudioData } from "@/preprocess/audio";
import { getTextData } from "@/preprocess/text";

export const useDataPathStore = defineStore({
    id: 'dataPath',
    state: () => ({
        dataDir: "",
    }),
    getters: {
        videoPath: state => `${state.dataDir}/video.mp4`,
        faceDataPath: state => `${state.dataDir}/faces.csv`,
        audioDataPath: state => `${state.dataDir}/audio.csv`,
        textDataPath: state => `${state.dataDir}/text.csv`,
    },
    actions: {
        async setDataDir(dir: string) {
            this.dataDir = dir
            await Promise.all([
                getFaceData(),
                getAudioData(),
                getTextData()
            ])
        }
    }
})
