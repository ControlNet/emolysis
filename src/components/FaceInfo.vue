<script lang="ts" setup>
import type { FaceRow } from "@/preprocess/faces";
import { computed, onUnmounted, onUpdated, ref } from "vue";
import { config } from "@/config";
import { moveTo } from "@/utils";
import AffectivePlot from "@/components/AffectivePlot.vue";
import { useVideoStore } from "@/stores/videoStore";
import { useFaceCheckedStore } from "@/stores/faceCheckedStore";

const props = defineProps<{
    index: number
    d: FaceRow
}>()

const canvasId = computed(() => `canvas-${props.index}`)
let isContinuous = ref(false)

let prevCoords: { x: number, y: number } = {x: -1, y: -1}

const newCoords = computed(() => {
    if (!isContinuous.value) {
        prevCoords = {x: props.d.x1, y: props.d.y1}
    } else {
        prevCoords = moveTo(prevCoords.x, prevCoords.y, props.d.x1, props.d.y1, 1)
    }
    return prevCoords
})

let previousSw = 0
let previousSh = 0

const sw = computed(() => {
    if (!isContinuous.value) {
        previousSw = props.d.x2 - props.d.x1
    }
    return previousSw
})

const sh = computed(() => {
    if (!isContinuous.value) {
        previousSh = props.d.y2 - props.d.y1
    }
    return previousSh
})

onUnmounted(() => {
    isContinuous.value = false
})

onUpdated(() => {
    const canvas = document.getElementById(canvasId.value) as HTMLCanvasElement
    const video = document.getElementById("video") as HTMLVideoElement
    const ctx = canvas.getContext("2d") as CanvasRenderingContext2D
    ctx.drawImage(video,
        newCoords.value.x > 0 ? newCoords.value.x : 0,
        newCoords.value.y > 0 ? newCoords.value.y : 0,
        sw.value, sh.value, 0, 0, config.faceCanvasSize, config.faceCanvasSize
    )
    isContinuous.value = true
})

const videoStore = useVideoStore()
videoStore.$onAction(({name}) => {
    if (name === "onVideoSeeked") {
        isContinuous.value = false
    }
})

const faceCheckedStore = useFaceCheckedStore()
const faceChecked = ref(faceCheckedStore.faceChecked[props.index])

function onCheckboxChange() {
    faceCheckedStore.setFaceChecked(props.index, faceChecked.value)
}

</script>

<template>
    <div class="flex flex-row p-0.5 m-0.5 face-info-div" style="border-radius: 1rem"
         :class="{'card-checked': faceChecked, 'card-unchecked': !faceChecked || !faceCheckedStore.visualChecked}">
        <div>
            <canvas :id="canvasId" :width="config.faceCanvasSize" :height="config.faceCanvasSize" class="bg-gray-400"
                    style="border-radius: 1rem"
            />
        </div>
        <div>
            <AffectivePlot
                :emotion-prob="props.d.emotionProb"
                :valence="props.d.valence"
                :arousal="props.d.arousal"
                :index="props.index"
                :length="config.faceInfoBarLength"
                :svgWidth="config.faceInfoBarLength"
            />
        </div>
        <div class="flex flex-col">
            <div class="grow" />
            <input type="checkbox" class="checkbox checkbox-primary" v-model="faceChecked"
                   @change="onCheckboxChange" />
            <div class="grow" />
        </div>
    </div>
</template>

<style scoped>
.face-info-div {
    @apply transition-all duration-300
}
</style>