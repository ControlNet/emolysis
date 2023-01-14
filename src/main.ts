import { createApp } from 'vue'
import { createPinia } from 'pinia'
import "@/assets/tailwind.css"

import App from './App.vue'
import router from "@/router";
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faBook } from "@fortawesome/free-solid-svg-icons"


library.add(faGithub, faBook)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.component("font-awesome-icon", FontAwesomeIcon)

app.mount("#app")
