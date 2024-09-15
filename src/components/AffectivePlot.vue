<script setup lang="ts">

import * as d3 from "d3";

import { computed, onMounted, onUpdated } from "vue";
import { config } from "@/config";
import _, { round } from "lodash";
import { EMOTIONS } from "@/global/consts";

const props = defineProps<{
    index: number,
    length: number,
    svgWidth: number,
    valence: number,
    arousal: number,
    emotionProb: Array<number>,
}>()

const svgEmotionId = computed(() => `svg-emotion-${props.index}`)
const svgValenceId = computed(() => `svg-valence-${props.index}`)
const svgArousalId = computed(() => `svg-arousal-${props.index}`)
const gEmotionId = computed(() => `g-emotion-${props.index}`)
const gValenceId = computed(() => `g-valence-${props.index}`)
const gArousalId = computed(() => `g-arousal-${props.index}`)

const emotion = computed(() => _.indexOf(props.emotionProb, _.max(props.emotionProb)))
const emotionName = computed(() => EMOTIONS[emotion.value])

const emotionBarLength = computed(() => props.emotionProb[emotion.value] * props.length)
const valenceBarLength = computed(() => props.valence / 1000 * props.length)
const arousalBarLength = computed(() => props.arousal / 1000 * props.length)

onMounted(async () => {
    // emotion
    const gEmotion = d3.select<SVGGElement, unknown>(`#${gEmotionId.value}`)
    gEmotion.append("text")
        .attr("x", 3)
        .attr("y", config.affectiveSvgHeight / 3)
        .attr("font-size", `${config.faceInfoFontSize}px`)
        .attr("font-weight", "bold")
        .text(`Emotion: ${emotionName.value}`)

    gEmotion.append("rect")
        .attr("x", 3)
        .attr("y", config.affectiveSvgHeight / 2)
        .attr("width", emotionBarLength.value)
        .attr("height", 10)
        .classed("emotion-bar", true)

    // valence
    const gValence = d3.select<SVGGElement, unknown>(`#${gValenceId.value}`)
    gValence.append("text")
        .attr("x", 3)
        .attr("y", config.affectiveSvgHeight / 3)
        .attr("font-size", `${config.faceInfoFontSize}px`)
        .attr("font-weight", "bold")
        .text(`Valence: ${round(props.valence, 0)}`)

    gValence.append("rect")
        .attr("x", 3)
        .attr("y", config.affectiveSvgHeight / 2)
        .attr("width", valenceBarLength.value)
        .attr("height", 10)
        .classed("valence-bar", true)

    // arousal
    const gArousal = d3.select<SVGGElement, unknown>(`#${gArousalId.value}`)
    gArousal.append("text")
        .attr("x", 3)
        .attr("y", config.affectiveSvgHeight / 3)
        .attr("font-size", `${config.faceInfoFontSize}px`)
        .attr("font-weight", "bold")
        .text(`Arousal: ${round(props.arousal, 0)}`)

    gArousal.append("rect")
        .attr("x", 3)
        .attr("y", config.affectiveSvgHeight / 2)
        .attr("width", arousalBarLength.value)
        .attr("height", 10)
        .classed("arousal-bar", true)
})

onUpdated(() => {
    // emotion
    const gEmotion = d3.select<SVGGElement, unknown>(`#${gEmotionId.value}`)
    gEmotion.select("text")
        .text(`Emotion: ${emotionName.value}`)

    gEmotion.select("rect")
        .transition()
        .duration(100)
        .attr("width", emotionBarLength.value)

    // valence
    const gValence = d3.select<SVGGElement, unknown>(`#${gValenceId.value}`)
    gValence.select("text")
        .text(`Valence: ${round(props.valence, 0)}`)

    gValence.select("rect")
        .transition()
        .duration(100)
        .attr("width", valenceBarLength.value)

    // arousal
    const gArousal = d3.select<SVGGElement, unknown>(`#${gArousalId.value}`)
    gArousal.select("text")
        .text(`Arousal: ${round(props.arousal, 0)}`)

    gArousal.select("rect")
        .transition()
        .duration(100)
        .attr("width", arousalBarLength.value)
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