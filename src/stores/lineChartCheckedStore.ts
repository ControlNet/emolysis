import { defineStore } from 'pinia'

export const useLineChartCheckedStore = defineStore({
    id: 'lineChartChecked',
    state: () => ({
        audioChecked: false,
        textChecked: false,
    }),
    actions: {
        setAudioChecked(value: boolean) {
            this.audioChecked = value
        },

        setTextChecked(value: boolean) {
            this.textChecked = value
        }
    }
})