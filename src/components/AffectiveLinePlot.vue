<script setup lang="ts">

import * as d3 from "d3";

import { computed, onMounted, onUpdated } from "vue";
import { config } from "@/config";
import _, { round } from "lodash";
import { EMOTIONS } from "@/global/consts";
import { getTextData, type TextRow } from "@/preprocess/text";
import type { Data, DataRow } from "@/preprocess/common";
import { getAudioData } from "@/preprocess/audio";

const props = defineProps<{
    index: number,
    svgWidth: number,
    length: number,
    currentFrame: number,
    valence: number,
    arousal: number,
    emotionProb: Array<number>,
    type: "visual" | "audio" | "text"
}>()

const svgEmotionId = computed(() => `svg-emotion-${props.index}`)
const svgValenceId = computed(() => `svg-valence-${props.index}`)
const svgArousalId = computed(() => `svg-arousal-${props.index}`)
const gEmotionId = computed(() => `g-emotion-${props.index}`)
const gValenceId = computed(() => `g-valence-${props.index}`)
const gArousalId = computed(() => `g-arousal-${props.index}`)
const verticalLineEmotionId = computed(() => `vertical-line-emotion-${props.index}`)
const verticalLineValenceId = computed(() => `vertical-line-valence-${props.index}`)
const verticalLineArousalId = computed(() => `vertical-line-arousal-${props.index}`)

const emotion = computed(() => _.indexOf(props.emotionProb, _.max(props.emotionProb)))
const emotionName = computed(() => EMOTIONS[emotion.value])

function addAxis(svg: d3.Selection<SVGSVGElement, unknown, any, undefined>, x: d3.ScaleLinear<number, number>, y: d3.ScaleLinear<number, number>) {
    // add the x-axis
    svg.append("g")
        .attr("transform", `translate(0, ${config.affectiveSvgHeight})`)
        .call(d3.axisBottom(x))

    // add the y-axis
    svg.append("g")
        .call(d3.axisLeft(y))
}

let x: d3.ScaleLinear<number, number, never>;

onMounted(async () => {
    let rawData: Data
    // collect the data and build the line chart
    if (props.type === "visual") {
        return
    } else if (props.type === "audio") {
        rawData = await getAudioData()
    } else if (props.type === "text") {
        // textData: Map<number, TextRow>, the key is the frame number
        // TextRow: {frame: number, valence: number, arousal: number, emotionProb: Array<number>}
        // draw a line chart for the video
        rawData = await getTextData()
    } else {
        return
    }

    const data = Array.from(rawData.values())
    console.log(`data length: ${data.length} ${props.type}`)

    x = d3.scaleLinear()
        .domain([0, data.length])
        .range([0, props.length])

    // emotion
    const yEmotion = d3.scaleLinear()
        .domain([_.min(data.map(d => _.min(d.emotionProb)! * 1000))! - 30, _.max(data.map(d => _.max(d.emotionProb)! * 1000))! + 30])
        .range([config.affectiveSvgHeight, config.affectiveSvgHeight * 0.5])

    const lineEmotion = d3.line<TextRow>()
        .x(d => x(d.frame))
        .y(d => yEmotion(_.max(d.emotionProb)! * 1000))

    const gEmotion = d3.select<SVGSVGElement, unknown>(`#${gEmotionId.value}`)

    gEmotion.append("text")
        .attr("y", config.affectiveSvgHeight / 3)
        .attr("font-size", `${config.faceInfoFontSize}px`)
        .attr("font-weight", "bold")
        .text(`Emotion: ${emotionName.value}`)

    gEmotion.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "blue")
        .attr("stroke-width", 1.5)
        .attr("d", lineEmotion)
    addAxis(gEmotion, x, yEmotion)

    // valence
    const yValence = d3.scaleLinear()
        .domain([_.min(data.map(d => d.valence))! - 30, _.max(data.map(d => d.valence))! + 30])
        .range([config.affectiveSvgHeight, config.affectiveSvgHeight * 0.5])

    const lineValence = d3.line<TextRow>()
        .x(d => x(d.frame))
        .y(d => yValence(d.valence))

    const gValence = d3.select<SVGSVGElement, unknown>(`#${gValenceId.value}`)

    gValence.append("text")
        .attr("y", config.affectiveSvgHeight / 3)
        .attr("font-size", `${config.faceInfoFontSize}px`)
        .attr("font-weight", "bold")
        .text(`Valence: ${round(props.valence, 0)}`)

    gValence.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 1.5)
        .attr("d", lineValence)
    addAxis(gValence, x, yValence)

    // arousal
    const yArousal = d3.scaleLinear()
        .domain([_.min(data.map(d => d.arousal))! - 30, _.max(data.map(d => d.arousal))! + 30])
        .range([config.affectiveSvgHeight, config.affectiveSvgHeight * 0.5])

    const lineArousal = d3.line<TextRow>()
        .x(d => x(d.frame))
        .y(d => yArousal(d.arousal))

    const gArousal = d3.select<SVGSVGElement, unknown>(`#${gArousalId.value}`)

    gArousal.append("text")
        .attr("y", config.affectiveSvgHeight / 3)
        .attr("font-size", `${config.faceInfoFontSize}px`)
        .attr("font-weight", "bold")
        .text(`Arousal: ${round(props.arousal, 0)}`)
    gArousal.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "orange")
        .attr("stroke-width", 1.5)
        .attr("d", lineArousal)
    addAxis(gArousal, x, yArousal)

    // add a vertical bar to show the current time position
    gEmotion.append("line")
        .attr("id", verticalLineEmotionId.value)
        .attr("x1", x(props.currentFrame))
        .attr("y1", config.affectiveSvgHeight * 0.5)
        .attr("x2", x(props.currentFrame))
        .attr("y2", config.affectiveSvgHeight)
        .attr("stroke", "black")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "5,5")

    gValence.append("line")
        .attr("id", verticalLineValenceId.value)
        .attr("x1", x(props.currentFrame))
        .attr("y1", config.affectiveSvgHeight * 0.5)
        .attr("x2", x(props.currentFrame))
        .attr("y2", config.affectiveSvgHeight)
        .attr("stroke", "black")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "5,5")

    gArousal.append("line")
        .attr("id", verticalLineArousalId.value)
        .attr("x1", x(props.currentFrame))
        .attr("y1", config.affectiveSvgHeight * 0.5)
        .attr("x2", x(props.currentFrame))
        .attr("y2", config.affectiveSvgHeight)
        .attr("stroke", "black")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "5,5")
})

onUpdated(() => {
    // update the text with the latest value, and the vertical bar to show the current time position
    if (!x) {
        return
    }

    // emotion
    const gEmotion = d3.select<SVGGElement, unknown>(`#${gEmotionId.value}`)
    gEmotion.select("text")
        .text(`Emotion: ${emotionName.value}`)

    gEmotion.select(`#${verticalLineEmotionId.value}`)
        .transition()
        .duration(100)
        .attr("x1", x(props.currentFrame))
        .attr("x2", x(props.currentFrame))

    // valence
    const gValence = d3.select<SVGGElement, unknown>(`#${gValenceId.value}`)
    gValence.select("text")
        .text(`Valence: ${round(props.valence, 0)}`)

    gValence.select(`#${verticalLineValenceId.value}`)
        .transition()
        .duration(100)
        .attr("x1", x(props.currentFrame))
        .attr("x2", x(props.currentFrame))

    // arousal
    const gArousal = d3.select<SVGGElement, unknown>(`#${gArousalId.value}`)
    gArousal.select("text")
        .text(`Arousal: ${round(props.arousal, 0)}`)

    gArousal.select(`#${verticalLineArousalId.value}`)
        .transition()
        .duration(100)
        .attr("x1", x(props.currentFrame))
        .attr("x2", x(props.currentFrame))
})

</script>

<template>
    <div class="flex flex-col">
        <div class="affective-block">
            <svg :id="svgEmotionId" :height="config.affectiveSvgHeight" :width="props.svgWidth">
                <g :id="gEmotionId" />
            </svg>
        </div>
        <div class="affective-block">
            <svg :id="svgValenceId" :height="config.affectiveSvgHeight" :width="props.svgWidth">
                <g :id="gValenceId" />
            </svg>
        </div>
        <div class="affective-block">
            <svg :id="svgArousalId" :height="config.affectiveSvgHeight" :width="props.svgWidth">
                <g :id="gArousalId" />
            </svg>
        </div>
    </div>
</template>

<style scoped>
.affective-block {
    @apply p-0.5
}
</style>