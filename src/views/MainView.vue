<script setup lang="ts">

import html2canvas from "html2canvas"; // Import the html2canvas library
import { computed, onBeforeMount, onMounted, ref } from "vue";
import FaceBlock from "@/components/FaceBlock.vue";
import { type FaceRow, getFaceDataByFrame, type VisualRow } from "@/preprocess/faces";
import * as _ from "lodash";
import { useDataPathStore } from "@/stores/dataPathStore";
import { useVideoStore } from "@/stores/videoStore";
import { config } from "@/config";
import AffectiveBarPlot from "@/components/AffectiveBarPlot.vue";
import { useRoute } from "vue-router";
import { useFaceCheckedStore } from "@/stores/faceCheckedStore";
import { getAudioDataByFrame } from "@/preprocess/audio";
import { getTextDataByFrame } from "@/preprocess/text";
import FooterBlock from "@/components/FooterBlock.vue";
import axios from "axios";
import { getLocalDataPath, getRemoteDataFps, getRemoteDataPath } from "@/global/api";
import AffectiveLinePlot from "@/components/AffectiveLinePlot.vue";
import { useLineChartCheckedStore } from "@/stores/lineChartCheckedStore";

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
const lineChartCheckedStore = useLineChartCheckedStore()

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
            await dataPathStore.setDataDir(getRemoteDataPath(route.params.videoId as string))
            const response = await axios.get(getRemoteDataFps(route.params.videoId as string))
            config.fps = await response.data.fps
            break
        case "local":
            await dataPathStore.setDataDir(getLocalDataPath(route.params.videoId as string))
            break
        default:
            document.location.href = "/"
    }
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

// Function to capture a screenshot of the whole webpage
function capturePageScreenshot(privacy: boolean = false) {
    const element = document.getElementById("app");
    const video = document.getElementById("video") as HTMLVideoElement;

    console.log('Element:', element);

    if (element && video) {
        // Get video position and size
        const videoRect = video.getBoundingClientRect();

        // Calculate the actual position of the video on the page (including scroll offsets)
        const videoCoords = {
            x: videoRect.left + window.scrollX, // X-coordinate relative to the page
            y: videoRect.top + window.scrollY,  // Y-coordinate relative to the page
            width: videoRect.width,  // Width of the video
            height: videoRect.height // Height of the video
        };

        console.log('Video Coordinates:', videoCoords);

        // Use html2canvas to capture the entire screenshot area
        html2canvas(element).then((canvas) => {

            if (privacy) {
                const context = canvas.getContext("2d");

                if (context) {
                    const faceBoundingBoxes = faceRows.value.map(row => [row.x1, row.y1, row.x2, row.y2]);
                    // Iterate over face bounding boxes and apply blur to those regions in the video
                    faceBoundingBoxes.forEach(([x1, y1, x2, y2]) => {
                        // Scale the face coordinates to fit the actual size and position of the video on the page
                        const faceX = videoCoords.x + (x1 / video.videoWidth) * videoCoords.width;
                        const faceY = videoCoords.y + (y1 / video.videoHeight) * videoCoords.height;
                        const faceWidth = ((x2 - x1) / video.videoWidth) * videoCoords.width;
                        const faceHeight = ((y2 - y1) / video.videoHeight) * videoCoords.height;

                        // Create a temporary canvas for the face region
                        const tempCanvas = document.createElement("canvas");
                        const tempContext = tempCanvas.getContext("2d")!;

                        // Set the size of the temporary canvas
                        tempCanvas.width = faceWidth;
                        tempCanvas.height = faceHeight;

                        // Extract the face region from the main canvas
                        const faceImageData = context.getImageData(faceX, faceY, faceWidth, faceHeight);
                        tempContext.putImageData(faceImageData, 0, 0);

                        // Apply blur effect to the temporary canvas
                        tempContext.filter = "blur(10px)";
                        tempContext.drawImage(tempCanvas, 0, 0);

                        // Draw the blurred face region back on the main canvas
                        context.drawImage(tempCanvas, faceX, faceY, faceWidth, faceHeight);
                    });

                    const canvasElements = document.querySelectorAll("[id^='canvas-']");
                    canvasElements.forEach((canvasElement) => {
                        const canvasRect = canvasElement.getBoundingClientRect();

                        // Calculate actual canvas position on the page
                        const canvasCoords = {
                            x: canvasRect.left + window.scrollX,
                            y: canvasRect.top + window.scrollY,
                            width: canvasRect.width,
                            height: canvasRect.height
                        };

                        // Apply a blur effect to the entire canvas element area on the main canvas
                        const tempCanvas = document.createElement("canvas");
                        const tempContext = tempCanvas.getContext("2d");

                        // Set the size of the temporary canvas to match the original canvas element
                        tempCanvas.width = canvasCoords.width;
                        tempCanvas.height = canvasCoords.height;

                        // Extract the canvas region from the main canvas
                        const canvasImageData = context.getImageData(canvasCoords.x, canvasCoords.y, canvasCoords.width, canvasCoords.height);
                        tempContext?.putImageData(canvasImageData, 0, 0);

                        // Apply blur effect
                        tempContext!.filter = "blur(10px)";
                        tempContext?.drawImage(tempCanvas, 0, 0);

                        // Draw the blurred canvas region back on the main canvas
                        context.drawImage(tempCanvas, canvasCoords.x, canvasCoords.y, canvasCoords.width, canvasCoords.height);
                    });
                }
            }

            // Convert the canvas to an image
            const dataURL = canvas.toDataURL("image/png");

            // Postprocessing using video coordinates (Optional)
            // You can use these coordinates for further actions, such as cropping, highlighting, etc.
            console.log("Screenshot taken with video at:", videoCoords);

            // Create a download link and trigger the download
            const link = document.createElement("a");
            link.href = dataURL;
            link.download = "webpage_screenshot.png";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }
}

</script>

<template id="main-view">
    <div class="m-5 select-none">
        <h1 class="text-5xl font-bold" style="text-align: center">Emolysis</h1>
        <br>

        <div class="flex">
            <div class="grow"/>
            <div class="flex flex-row max-h-screen">
                <div>
                    <video controls
                           id="video" @seeked="onVideoSeeked" width="640" height="360"
                           style="border-radius: 1rem">
                        <source :src="dataPathStore.videoPath" type="video/mp4">
                    </video>

                    <!-- Screenshot Button -->
                    <div class="flex mt-3">
                        <button class="flex-1 btn btn-primary mr-3" @click="() => capturePageScreenshot(false)">Screenshot</button>
                        <button class="flex-1 btn" @click="() => capturePageScreenshot(true)">Privacy Mode Screenshot</button>
                    </div>

                    <div class="card w-auto h-auto bg-base-300 my-3 shadow-xl" style="min-height: 240px!important;">
                        <div class="card-body">
                            <h2 class="card-title">Overall Result</h2>
                            <AffectiveBarPlot
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
                            <div class="grow"/>
                            <div class="card-actions flex-none">
                                <input type="checkbox" class="checkbox checkbox-primary" v-model="visualChecked"
                                       @change="onVisualCheckedChange"/>
                            </div>
                        </div>
                        <FaceBlock :face-rows="faceRows"/>
                    </div>
                </div>
                <div class="flex flex-col">
                    <div id="audio-card" class="card card-checked shadow-xl grow"
                         :class="{'card-checked': audioChecked, 'card-unchecked': !audioChecked}"
                         style="width: 350px!important; min-width: 350px!important;">
                        <div class="card-body">
                            <div class="flex">
                                <h2 class="card-title flex-none">Audio Modality</h2>
                                <div class="grow w-1"/>
                                <div class="card-actions flex-none">
                                    <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                        <path
                                            d="M0 22h1v-5h4v5h2v-10h4v10h2v-15h4v15h2v-21h4v21h1v1h-24v-1zm4-4h-2v4h2v-4zm6-5h-2v9h2v-9zm6-5h-2v14h2v-14zm6-6h-2v20h2v-20z"/>
                                    </svg>
                                    <input type="checkbox" class="toggle toggle-primary"
                                           v-model="lineChartCheckedStore.audioChecked"/>
                                    <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                        <path
                                            d="M24 3.875l-6 1.221 1.716 1.708-5.351 5.358-3.001-3.002-7.336 7.242 1.41 1.418 5.922-5.834 2.991 2.993 6.781-6.762 1.667 1.66 1.201-6.002zm0 17.125v2h-24v-22h2v20h22z"/>
                                    </svg>
                                </div>
                                <div class="grow w-1"/>
                                <div class="card-actions flex-none">
                                    <input type="checkbox" class="checkbox checkbox-primary" v-model="audioChecked"/>
                                </div>
                            </div>
                            <AffectiveBarPlot
                                v-if="analysisEnable && !lineChartCheckedStore.audioChecked"
                                :emotion-prob="audioEmotionProb"
                                :index="101"
                                :length="config.faceInfoBarLength"
                                :svgWidth="config.overallBarLength"
                                :valence="audioValence"
                                :arousal="audioArousal"
                            />
                            <AffectiveLinePlot
                                v-if="analysisEnable && lineChartCheckedStore.audioChecked"
                                :svgWidth="config.overallBarLength"
                                :length="config.faceInfoLineLength"
                                :emotion-prob="audioEmotionProb"
                                :valence="audioValence"
                                :arousal="audioArousal"
                                :current-frame="currentFrame"
                                :index="101"
                                type="audio"
                            />
                        </div>
                    </div>
                    <div id="text-card" class="card card-checked my-3 shadow-xl grow"
                         :class="{'card-checked': textChecked, 'card-unchecked': !textChecked}"
                         style="width: 350px!important; min-width: 350px!important;">
                        <div class="card-body">
                            <div class="flex">
                                <h2 class="card-title flex-none">Text Modality</h2>
                                <div class="grow w-1"/>
                                <div class="card-actions flex-none">
                                    <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                        <path
                                            d="M0 22h1v-5h4v5h2v-10h4v10h2v-15h4v15h2v-21h4v21h1v1h-24v-1zm4-4h-2v4h2v-4zm6-5h-2v9h2v-9zm6-5h-2v14h2v-14zm6-6h-2v20h2v-20z"/>
                                    </svg>
                                    <input type="checkbox" class="toggle toggle-primary"
                                           v-model="lineChartCheckedStore.textChecked"/>
                                    <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                        <path
                                            d="M24 3.875l-6 1.221 1.716 1.708-5.351 5.358-3.001-3.002-7.336 7.242 1.41 1.418 5.922-5.834 2.991 2.993 6.781-6.762 1.667 1.66 1.201-6.002zm0 17.125v2h-24v-22h2v20h22z"/>
                                    </svg>
                                </div>
                                <div class="grow w-1"/>
                                <div class="card-actions flex-none">
                                    <input type="checkbox" class="checkbox checkbox-primary" v-model="textChecked"/>
                                </div>
                            </div>
                            <AffectiveBarPlot
                                v-if="analysisEnable && !lineChartCheckedStore.textChecked"
                                :emotion-prob="textEmotionProb"
                                :index="102"
                                :length="config.faceInfoBarLength"
                                :svgWidth="config.overallBarLength"
                                :valence="textValence"
                                :arousal="textArousal"
                            />
                            <AffectiveLinePlot
                                v-if="analysisEnable && lineChartCheckedStore.textChecked"
                                :svgWidth="config.overallBarLength"
                                :length="config.faceInfoLineLength"
                                :emotion-prob="textEmotionProb"
                                :valence="textValence"
                                :arousal="textArousal"
                                :current-frame="currentFrame"
                                :index="102"
                                type="text"
                            />

                        </div>
                    </div>
                </div>
            </div>
            <div class="grow"/>
        </div>
    </div>
    <FooterBlock/>
</template>
