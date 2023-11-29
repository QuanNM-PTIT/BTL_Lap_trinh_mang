<script setup>
import Home from '../components/Home.vue'
import ChatSpace from '../components/ChatSpace.vue';
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/users';
import { storeToRefs } from 'pinia';

const userStore = useUserStore();

const { user } = storeToRefs(userStore);
</script>

<template>
    <main v-if="!user">
        <Home />
    </main>

    <main v-else>
        <ChatSpace />
    </main>
</template>
