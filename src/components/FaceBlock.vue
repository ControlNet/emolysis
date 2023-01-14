<script lang="ts" setup>
import type { FaceRow } from "@/preprocess/faces";
import FaceInfo from "@/components/FaceInfo.vue";

const props = defineProps<{
    faceRows: Array<FaceRow>
}>()

</script>

<template>
    <div class="flex flex-col">
        <div v-for="(row, i) in props.faceRows">
            <FaceInfo :d="row" :index="i" />
        </div>
    </div>
</template>
