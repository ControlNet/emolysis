<script setup lang="ts">

import { computed, onBeforeMount, onMounted, ref } from "vue";
import FaceBlock from "@/components/FaceBlock.vue";
import { type FaceRow, getFaceDataByFrame, type VisualRow } from "@/preprocess/faces";
import * as _ from "lodash";
import { useDataPathStore } from "@/stores/dataPathStore";
import { useVideoStore } from "@/stores/videoStore";
import { config } from "@/config";
import AffectivePlot from "@/components/AffectivePlot.vue";
import { useRoute } from "vue-router";
import { useFaceCheckedStore } from "@/stores/faceCheckedStore";
import { getAudioDataByFrame } from "@/preprocess/audio";
import { getTextDataByFrame } from "@/preprocess/text";
import FooterBlock from "@/components/FooterBlock.vue";

const visualChecked = ref(true);
const audioChecked = ref(true);
const textChecked = ref(true);

const currentFrame = ref(-1)
const faceRows = computed(() => {
    return _.sortBy(getFaceDataByFrame(currentFrame.value).filter(row => row.boxProb > config.boxProbThreshold), (d: FaceRow) => d.x1)
})

const audioRow = computed(() => {
    return getAudioDataByFrame(currentFrame.value)
})

const textRow = computed(() => {
    return getTextDataByFrame(currentFrame.value)
})

const faceCheckedStore = useFaceCheckedStore()
const dataPathStore = useDataPathStore()
const videoStore = useVideoStore()

const analysisEnable = computed(() => faceRows.value.length > 0)

const overallDataRow = computed(() => {
    // visual
    let checkedFaceNumber = 0
    const visualRow: VisualRow = {
        frame: currentFrame.value,
        arousal: 0,
        valence: 0,
        emotionProb: Array(9).fill(0),
    }

    if (visualChecked.value && faceRows.value.length > 0) {
        for (let faceIndex = 0; faceIndex < faceRows.value.length; faceIndex++) {
            if (faceCheckedStore.faceChecked[faceIndex]) {
                visualRow.arousal += faceRows.value[faceIndex].arousal
                visualRow.valence += faceRows.value[faceIndex].valence
                for (let i = 0; i < 9; i++) {
                    visualRow.emotionProb[i] += faceRows.value[faceIndex].emotionProb[i]
                }
                checkedFaceNumber += 1
            }
        }

        if (checkedFaceNumber > 0) {
            visualRow.arousal /= checkedFaceNumber
            visualRow.valence /= checkedFaceNumber
            for (let i = 0; i < 9; i++) {
                visualRow.emotionProb[i] /= checkedFaceNumber
            }
        }
    }

    // overall
    let numModalities = 0
    const overallRow = {
        frame: currentFrame.value,
        arousal: 0,
        valence: 0,
        emotionProb: Array(9).fill(0) as number[],
    }

    if (faceRows.value.length == 0) {
        return overallRow
    }

    if (visualChecked.value && faceRows.value.length > 0 && checkedFaceNumber > 0) {
        overallRow.arousal += visualRow.arousal
        overallRow.valence += visualRow.valence
        for (let i = 0; i < 9; i++) {
            overallRow.emotionProb[i] += visualRow.emotionProb[i]
        }
        numModalities += 1
    }

    if (audioChecked.value && audioRow.value !== undefined) {
        overallRow.arousal += audioRow.value.arousal
        overallRow.valence += audioRow.value.valence
        for (let i = 0; i < 9; i++) {
            overallRow.emotionProb[i] += audioRow.value.emotionProb[i]
        }
        numModalities += 1
    }

    if (textChecked.value && textRow.value !== undefined) {
        overallRow.arousal += textRow.value.arousal
        overallRow.valence += textRow.value.valence
        for (let i = 0; i < 9; i++) {
            overallRow.emotionProb[i] += textRow.value.emotionProb[i]
        }
        numModalities += 1
    }

    if (numModalities > 0) {
        overallRow.arousal /= numModalities
        overallRow.valence /= numModalities
        for (let i = 0; i < 9; i++) {
            overallRow.emotionProb[i] /= numModalities
        }
    }

    return overallRow
})

const emotionProb = computed(() => overallDataRow.value.emotionProb)
const arousal = computed(() => overallDataRow.value.arousal)
const valence = computed(() => overallDataRow.value.valence)

const audioEmotionProb = computed(() => audioRow.value?.emotionProb ?? Array(9).fill(0))
const audioArousal = computed(() => audioRow.value?.arousal ?? 0)
const audioValence = computed(() => audioRow.value?.valence ?? 0)

const textEmotionProb = computed(() => textRow.value?.emotionProb ?? Array(9).fill(0))
const textArousal = computed(() => textRow.value?.arousal ?? 0)
const textValence = computed(() => textRow.value?.valence ?? 0)

const route = useRoute()

onBeforeMount(async () => {
    switch (route.params.mode) {
        case "remote":
            await dataPathStore.setDataDir(`http://${import.meta.env.VITE_API_URL}/data/${route.params.videoId}`)
            break
        case "local":
            await dataPathStore.setDataDir(`/data/${route.params.videoId}`)
            break
        default:
            document.location.href = "/"
    }
    config.fps = route.params.videoId === "M01004HK7" ? 25 : 30
})


onMounted(async () => {
    const video = document.getElementById("video") as HTMLVideoElement;
    currentFrame.value = 0
    setInterval(() => {
        const nextFrame = Math.round(video.currentTime * config.fps);
        if (nextFrame === currentFrame.value) {
            return
        }
        currentFrame.value = nextFrame
    }, 20)
})

function onVideoSeeked() {
    videoStore.onVideoSeeked()
}

function onVisualCheckedChange() {
    faceCheckedStore.setVisualChecked(visualChecked.value)
}

</script>

<template>
    <div class="m-5 select-none">
        <h1 class="text-5xl font-bold" style="text-align: center">Emolysis</h1>
        <br>

        <div class="flex">
            <div class="grow" />
            <div class="flex flex-row max-h-screen">
                <div>
                    <video controls
                           id="video" @seeked="onVideoSeeked" @seeking="onVideoSeeking" width="640" height="360"
                           style="border-radius: 1rem">
                        <source :src="dataPathStore.videoPath" type="video/mp4">
                    </video>

                    <div class="card w-auto h-auto bg-base-300 my-3 shadow-xl" style="min-height: 240px!important;">
                        <div class="card-body">
                            <h2 class="card-title">Overall Result</h2>
                            <AffectivePlot
                                v-if="analysisEnable"
                                :emotion-prob="emotionProb"
                                :index="100"
                                :length="config.overallBarLength"
                                :svgWidth="config.overallBarLength"
                                :valence="valence"
                                :arousal="arousal"
                            />
                        </div>
                    </div>
                </div>
                <div id="visual-card" class="card card-checked mx-3 mb-3 shadow-xl"
                     :class="{'card-checked': visualChecked, 'card-unchecked': !visualChecked}"
                     style="width: 550px!important; min-width: 550px!important;">
                    <div class="card-body">
                        <div class="flex">
                            <h2 class="card-title flex-none">Visual Modality</h2>
                            <div class="grow" />
                            <div class="card-actions flex-none">
                                <input type="checkbox" checked="checked" class="checkbox checkbox-primary"
                                       v-model="visualChecked" @change="onVisualCheckedChange" />
                            </div>
                        </div>
                        <FaceBlock :face-rows="faceRows" />
                    </div>
                </div>
                <div class="flex flex-col">
                    <div id="audio-card" class="card card-checked shadow-xl grow"
                     :class="{'card-checked': audioChecked, 'card-unchecked': !audioChecked}"
                         style="width: 350px!important; min-width: 350px!important;">
                        <div class="card-body">
                            <div class="flex">
                                <h2 class="card-title flex-none">Audio Modality</h2>
                                <div class="grow w-1" />
                                <div class="card-actions flex-none">
                                    <input type="checkbox" checked="checked" class="checkbox checkbox-primary"
                                           v-model="audioChecked"/>
                                </div>
                            </div>
                            <AffectivePlot
                                v-if="analysisEnable"
                                :emotion-prob="audioEmotionProb"
                                :index="101"
                                :length="config.faceInfoBarLength"
                                :svgWidth="config.overallBarLength"
                                :valence="audioValence"
                                :arousal="audioArousal"
                            />
                        </div>
                    </div>
                    <div id="text-card" class="card card-checked my-3 shadow-xl grow"
                     :class="{'card-checked': textChecked, 'card-unchecked': !textChecked}"
                         style="width: 350px!important; min-width: 350px!important;">
                        <div class="card-body">
                            <div class="flex">
                                <h2 class="card-title flex-none">Text Modality</h2>
                                <div class="grow w-1" />
                                <div class="card-actions flex-none">
                                    <input type="checkbox" checked="checked" class="checkbox checkbox-primary"
                                           v-model="textChecked" />
                                </div>
                            </div>
                            <AffectivePlot
                                v-if="analysisEnable"
                                :emotion-prob="textEmotionProb"
                                :index="102"
                                :length="config.faceInfoBarLength"
                                :svgWidth="config.overallBarLength"
                                :valence="textValence"
                                :arousal="textArousal"
                            />
                        </div>
                    </div>
                </div>
            </div>
            <div class="grow" />
        </div>
    </div>
    <FooterBlock />
</template>
