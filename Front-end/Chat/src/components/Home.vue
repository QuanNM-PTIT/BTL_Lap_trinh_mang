<script setup>
import { ref, onMounted, h } from 'vue'
import { LoadingOutlined } from '@ant-design/icons-vue';
import '/public/bg.svg';

const topics = ref([]);
const isLoading = ref(true);

onMounted(async () =>
{
    isLoading.value = false;
})

const indicator = h(LoadingOutlined,
    {
        style:
        {
            fontSize: '48px',
        },
        spin: true,
    });

</script>

<template>
    <!-- <div class="spinner" v-if="isLoading">
        <a-spin :indicator="indicator" />
    </div> -->
    <div class="background">
        <img src="bg.svg" alt="" style="width: 60%; margin-bottom: 6%;">
    </div>
</template>

<style scoped>
.quiz-container
{
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: space-between;
    padding: 20px 0;
}

.spinner
{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 60vh;
    width: 100%;
}

.background
{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100%;
}

@media (max-width: 768px)
{
    .quiz-container
    {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        align-items: space-between;
        justify-content: center;
        padding: 20px 0;
    }
}
</style>