import _ from "lodash";

export function moveTo(prevX: number, prevY: number, x: number, y: number, speed: number): { x: number, y: number } {
    const dx = x - prevX
    const dy = y - prevY
    const distance = Math.sqrt(dx * dx + dy * dy)
    if (distance < speed) {
        return {x, y}
    }
    const angle = Math.atan2(dy, dx)
    return {x: prevX + speed * Math.cos(angle), y: prevY + speed * Math.sin(angle)}
}

export function smoothArray(array: Array<number>, window: number): Array<number> {
    const smoothArray = []
    for (let i = 0; i < array.length; i++) {
        const start = Math.max(0, i - window)
        const end = Math.min(array.length, i + window)
        const subArray = array.slice(start, end)
        smoothArray.push(_.mean(subArray))
    }
    return smoothArray
}

export function smoothArrayBy<T>(array: Array<T>, window: number, key: keyof T): Array<T> {
    const smoothArray = []
    for (let i = 0; i < array.length; i++) {
        const start = Math.max(0, i - window)
        const end = Math.min(array.length, i + window)
        const subArray = array.slice(start, end).map(item => item[key])
        const mean = _.mean(subArray)
        smoothArray.push({...array[i], [key]: mean})
    }
    return smoothArray
}

export function llr2prob(llr: number): number {
    return 1 / (1 + Math.exp(-llr))
}
