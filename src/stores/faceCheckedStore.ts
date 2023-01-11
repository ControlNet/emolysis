import { defineStore } from 'pinia'

export const useFaceCheckedStore = defineStore({
    id: 'faceChecked',
    state: () => ({
        faceChecked: Array(99).fill(true) as Array<boolean>,
        visualChecked: true
    }),
    actions: {
        setFaceChecked(index: number, value: boolean) {
            this.faceChecked[index] = value
        },
        setVisualChecked(value: boolean) {
            this.visualChecked = value
        }
    }
})