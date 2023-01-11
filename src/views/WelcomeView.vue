<script lang="ts" setup>

import { type Ref, ref } from "vue";
import FooterBlock from "@/components/FooterBlock.vue";
import { closeSocket, getSocket } from "@/global/socket";
import type { Message, MessageProcessData, MessageResultData, MessageVideoData } from "@/global/consts";
import _ from "lodash";
import { config } from "@/config";

const showProgressBar = ref(false)
const buttonAvailable = ref(true)
const processingStatus = ref("")
const progressBarValue: Ref<number | undefined> = ref(undefined)
const progressBarMax: Ref<number | undefined> = ref(undefined)
const connectionError = ref(false)

async function onClick() {
    const fileInput = document.getElementById("file-input") as HTMLInputElement
    const file = fileInput.files![0] as File | undefined

    if (file !== undefined) {
        // only support mp4
        if (file.type !== "video/mp4") {
            alert("Only support mp4 file")
            return
        }

        buttonAvailable.value = false
        showProgressBar.value = true
        processingStatus.value = "Uploading file..."
        const connection = getSocket()
        connection.onopen = async () => {
            connection.send(file)
        }

        connection.onmessage = async (event) => {
            const data = JSON.parse(event.data) as Message<MessageProcessData | MessageVideoData | MessageResultData | {}>
            if (data.status !== "done") {
                await connection.send("")
            } else {
                closeSocket()
            }
            console.log(data)
            switch (data.status) {
                case "uploaded": {
                    processingStatus.value = "Processing speech recognition"
                    progressBarValue.value = 0
                    progressBarMax.value = 1
                    break
                }
                case "audio": {
                    const {current, total} = data.data as MessageProcessData
                    processingStatus.value = `Processing audio ${_.round(current / total * 100)}%`
                    progressBarValue.value = current / total * 0.1
                    break
                }
                case "audio done": {
                    progressBarValue.value = 0.1
                    break
                }
                case "text": {
                    const {current, total} = data.data as MessageProcessData
                    processingStatus.value = `Processing text ${_.round(current / total * 100)}%`
                    progressBarValue.value = 0.1 + current / total * 0.1
                    break
                }
                case "text done": {
                    progressBarValue.value = 0.2
                    break
                }
                case "visual start": {
                    config.fps = (data.data as MessageVideoData).fps
                    break
                }
                case "visual": {
                    const {current, total} = data.data as MessageProcessData
                    processingStatus.value = `Processing visual ${_.round(current / total * 100)}%`
                    progressBarValue.value = 0.2 + current / total * 0.8
                    break
                }
                case "visual done": {
                    progressBarValue.value = 1
                    break
                }
                case "done": {
                    const { id } = data.data as MessageResultData
                    console.log("href", `/remote/${id}`)
                    break
                }
            }
        }

        const onError = () => {
            connectionError.value = true
            processingStatus.value = "Connection error"
        }

        connection.onerror = onError
        connection.onclose = onError
    }
}


</script>

<template>
    <div class="hero bg-base-200 min-h-screen">
        <div class="hero-content text-center">
            <div class="max-w-md">
                <h1 class="text-5xl font-bold">Emolysis</h1>
                <p class="py-6">An emotion analysis toolkit in multiparty interaction.</p>
                <div class="form-control">
                    <div class="input-group">
                        <input type="file" id="file-input" class="file-input file-input-bordered w-full max-w-xs" />
                        <button class="btn" @click="onClick"
                                :class="{ 'btn-disabled': !buttonAvailable, 'btn-primary': buttonAvailable }">
                            {{ buttonAvailable ? "Upload" : "Processing" }}
                        </button>
                    </div>
                </div>
                <div class="h-1">
                    <progress class="progress progress-primary w-65"
                              :class="{'progress-primary': !connectionError, 'progress-error': connectionError}"
                              v-if="showProgressBar" :value="progressBarValue" :max="progressBarMax"></progress>
                    <p class="py-2">{{ processingStatus }}</p>
                </div>
            </div>
        </div>
    </div>
    <FooterBlock />
</template>

<style>
progress {
    @apply transition-all duration-500;
}
</style>