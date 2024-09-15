<script setup lang="ts">
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { GITHUB_URL, PAPER_URL } from "@/global/consts";
</script>

<template>
    <footer class="footer footer-center p-4 bg-base-300 text-base-content bottom-0 absolute">
        <div class="flex w-full">
            <div class="w-1" />
            <p class="h-5">Authors: Shreya Ghosh*, Zhixi Cai*, Parul Gupta, Garima Sharma, Abhinav Dhall, Munawar Hayat</p>
            <div class="grow" />
            <a :href="PAPER_URL">Paper</a>
            <a :href="PAPER_URL"><font-awesome-icon icon="fa-solid fa-book" class="h-5 align-middle"/></a>
            <div class="divider divider-horizontal h-5 align-middle mx-2"></div>
            <a :href="GITHUB_URL"><p style="vertical-align: middle">GitHub</p></a>
            <a :href="GITHUB_URL"><font-awesome-icon icon="fa-brands fa-github" class="h-5 align-middle"/></a>
            <div class="w-1" />
        </div>
    </footer>
</template>
