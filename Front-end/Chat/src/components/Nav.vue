<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/users';
import AuthModal from './AuthModal.vue';
import { message } from 'ant-design-vue';
import { UnorderedListOutlined } from '@ant-design/icons-vue';
import { storeToRefs } from 'pinia';

const router = useRouter();
const userStore = useUserStore();

const { user } = storeToRefs(userStore);

const isMobile = ref(false);
const isMenuOpen = ref(false);

const checkResponsive = () =>
{
    isMobile.value = window.innerWidth < 700;
};

onMounted(() =>
{
    checkResponsive();
    window.addEventListener('resize', checkResponsive);
});

const toggleMenu = () =>
{
    isMenuOpen.value = !isMenuOpen.value;
};

const logout = async () =>
{
    await userStore.handleLogout();
    message.success('Đăng xuất thành công!', 2);
    router.push(`/`);
    setTimeout(() =>
    {
        window.location.reload();
    }, 2000);
}
</script>


<template>
    <div>
        <a-layout-header style="width: 100%;">
            <div class="nav-container">
                <div class="left-content">
                    <RouterLink to="/" style="font-size: 25px;">ChatApp</RouterLink>
                </div>

                <div class="right-content">
                    <template v-if="!isMobile">
                        <div class="menu-buttons" v-if="!user">
                            <AuthModal :isLogin="false" />
                            <AuthModal :isLogin="true" />
                        </div>

                        <div class="menu-buttons" v-else>
                            <a-button type="primary" @click.prevent="logout">
                                <LogoutOutlined />
                                Đăng xuất
                            </a-button>
                        </div>
                    </template>
                    <template v-else>
                        <a-dropdown :trigger="['click']">
                            <template #overlay>
                                <a-menu v-if="isMenuOpen">
                                    <div v-if="!user">
                                        <a-menu-item key="1">
                                            <AuthModal :isLogin="false" />
                                        </a-menu-item>
                                        <a-menu-item key="2">
                                            <AuthModal :isLogin="true" />
                                        </a-menu-item>
                                    </div>

                                    <div v-else>
                                        <a-menu-item key="1">
                                            <a-button type="primary" @click.prevent="logout">
                                                <LogoutOutlined />
                                                Đăng xuất
                                            </a-button>
                                        </a-menu-item>
                                    </div>
                                </a-menu>
                            </template>
                            <a-button type="primary" @click="toggleMenu">
                                <UnorderedListOutlined />
                            </a-button>
                        </a-dropdown>
                    </template>
                </div>
            </div>
        </a-layout-header>
    </div>
</template>

<style scoped>
.nav-container
{
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    width: 100%;
}

.left-content
{
    display: flex;
    align-items: center;
}

.left-content a
{
    margin-right: 10px;
}

.right-content
{
    display: flex;
    align-items: center;
}

.menu-buttons
{
    display: flex;
    align-items: center;
}
</style>