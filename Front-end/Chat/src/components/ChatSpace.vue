<script setup>
import { SendOutlined, PaperClipOutlined } from '@ant-design/icons-vue';
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/users';
import { storeToRefs } from 'pinia';
import axios from 'axios';
import { FileOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

const userStore = useUserStore();

const { user } = storeToRefs(userStore);

const socket = new WebSocket(`ws://localhost:8000/ws/${user.value.username}`);

const file_socket = new WebSocket(`ws://localhost:8000/ws/file/${user.value.username}`);

const currentMessage = ref('');

const messages = ref([]);

const messagesOffline = ref([]);

const open = ref(false);

const fileInput = ref(null);

const isOnline = ref(navigator.onLine);

const listUsers = ref([]);

onMounted(async () =>
{
    await axios.get('http://localhost:8000/message/get_all').then((res) =>
    {
        res.data.forEach((msg) =>
        {
            messages.value.push({
                'username': msg.username,
                'message': msg.message,
                'type': msg.type
            });
        });
    });

    socket.onmessage = (e) =>
    {
        console.log(e.data);
        const data = JSON.parse(e.data);
        messages.value.push({
            'username': data.username,
            'message': data.message,
            'type': data.type
        });
    };

    file_socket.onmessage = (e) =>
    {
        const data = JSON.parse(e.data);
        messages.value.push({
            'username': data.username,
            'message': data.message,
            'type': data.type
        });
    };

    await axios.get('http://127.0.0.1:8000/api/user/get_all').then((res) =>
    {
        listUsers.value = res.data;
    });

    setInterval(async () =>
    {
        await axios.get('http://127.0.0.1:8000/api/user/get_all').then((res) =>
        {
            listUsers.value = res.data;
        });
    }, 2000);
});

const sendMessage = () =>
{
    const messageData = {
        type: 'text',
        content: currentMessage.value
    };
    currentMessage.value = '';

    if (!isOnline.value)
    {
        messagesOffline.value.push(messageData);
        return;
    }

    socket.send(JSON.stringify(messageData));
};

const handleOnline = () =>
{
    isOnline.value = true;
    syncMessages();
};

const handleOffline = () =>
{
    isOnline.value = false;
};

const syncMessages = () =>
{
    for (let i = 0; i < messagesOffline.value.length; i++)
    {
        if (messagesOffline.value[i].type == 'text')
            socket.send(JSON.stringify(messagesOffline.value[i]));
        else if (messagesOffline.value[i].type == 'file')
            file_socket.send(JSON.stringify(messagesOffline.value[i]));
    }
    messagesOffline.value = [];
};


const sendFile = async (file) =>
{
    const chunkSize = 1024 * 1024;
    let offset = 0;

    const hide = ref();

    if (!isOnline.value)
    {
        const data = {
            type: 'file_progress',
            content: file.name,
        }
        messagesOffline.value.push(data);
    }

    if (isOnline.value)
    {
        message
            .loading('Đang tải lên', 2.5)
            .then(() =>
            {
                hide.value = message.loading('Đang gửi', 0);
                while (offset < file.size)
                {
                    let end = offset + chunkSize;
                    if (end > file.size)
                        end = file.size;
                    const chunk = file.slice(offset, end);
                    const reader = new FileReader();

                    if (offset + chunkSize >= file.size)
                        offset = file.size;

                    reader.onload = () =>
                    {
                        const fileData = {
                            type: 'file',
                            name: file.name,
                            offset: offset,
                            content: reader.result,
                            totalSize: file.size
                        };
                        file_socket.send(JSON.stringify(fileData));
                        setTimeout(() => { }, 1000);
                    };

                    reader.readAsDataURL(chunk);
                    offset += chunkSize;
                }
            })
            .then(() =>
            {

                setTimeout(() => { hide.value(); message.success('Gửi file thành công', 2.5); }, 2000);
            });
    }
    else
    {
        message.loading('Đang tải lên', 1);
        while (offset < file.size)
        {
            let end = offset + chunkSize;
            if (end > file.size)
                end = file.size;
            const chunk = file.slice(offset, end);
            const reader = new FileReader();

            if (offset + chunkSize >= file.size)
                offset = file.size;

            reader.onload = () =>
            {
                const fileData = {
                    type: 'file',
                    name: file.name,
                    offset: offset,
                    content: reader.result,
                    totalSize: file.size
                };
                if (!isOnline.value)
                {
                    messagesOffline.value.push(fileData);
                    localStorage.setItem('messagesOffline', JSON.stringify(messagesOffline.value));
                    return;
                }
                file_socket.send(JSON.stringify(fileData));
                setTimeout(() => { }, 1000);
            };

            reader.readAsDataURL(chunk);
            offset += chunkSize;
        }
    }
};

const handleFileChange = (event) =>
{
    fileInput.value = event.target.files[0];
};

const handleFileClick = () =>
{
    open.value = true;
};

const handleFileInput = () =>
{
    sendFile(fileInput.value);
    open.value = false;
    fileInput.value = null;
};

window.addEventListener("online", handleOnline);
window.addEventListener("offline", handleOffline);

</script>

<template>
    <div class="super-container">
        <div class="user-status-bar">
            <div class="user-list" v-for="user_sts in listUsers" :key="user_sts.username">
                <div class="user">
                    <div class="infor">
                        <span class="username_status">{{ user_sts.username }}</span>
                        <span :class="'status ' + user_sts.status"></span>
                    </div>
                </div>
            </div>
        </div>

        <div class="chat-space-container">
            <div style="padding-bottom: 100px;">
                <div style="margin-top: 20px">
                    <div v-for="msg in messages" :key="msg.message">
                        <div class="message-container" :class="{ 'my-message': msg.username == user.username }">
                            <div class="username-container" v-if="msg.username != user.username">
                                <p class="username">{{ msg.username }}:</p>
                            </div>
                            <p v-if="msg.type == 'text'" class="message">{{ msg.message }}</p>
                            <p v-else class="message">
                                <a :href="'http://127.0.0.1:8000/message/file/' + msg.message" class="your-file"
                                    :class="{ 'my-file': msg.username == user.username }">
                                    <FileOutlined />
                                    {{ msg.message }}
                                </a>
                            </p>
                        </div>
                    </div>
                    <div v-for="(msg, index) in messagesOffline.filter(item => item.type !== 'file')" :key="index">
                        <div class="message-container my-message">
                            <p class="message" style="display: block;">{{ msg.content }}</p>
                        </div>
                        <p
                            style="text-align: end; margin: 2px 0 0 0; padding: 0 20px; font-size: 12px; color: rgb(183, 183, 183);">
                            Đang gửi</p>
                    </div>
                </div>
            </div>

            <a-form @submit.prevent="sendMessage" style="width: 100%;">
                <div class="chat-container">
                    <a-card class="chat-card">
                        <div style="display: flex;">
                            <a-button type="text" style="border-radius: 30px; border-color: white;">
                                <PaperClipOutlined style="font-size: 24px;" @click="handleFileClick" />
                            </a-button>

                            <a-modal v-model:visible="open" title="Gửi file" @ok="handleFileInput">
                                <input type="file" @change="handleFileChange" />
                            </a-modal>

                            <a-input style="border-radius: 15px;" placeholder="Nhập tin nhắn"
                                v-model:value="currentMessage" />
                            <a-button type="submit" style="margin-left: 5px; border-radius: 30px; border-color: white;">
                                <SendOutlined style="font-size: 24px;" />
                            </a-button>
                        </div>
                    </a-card>
                </div>
            </a-form>
        </div>
    </div>
</template>

<style scoped>
.chat-container
{
    position: fixed;
    bottom: 0;
    width: 85%;
    display: flex;
    justify-content: center;
}

.chat-card
{
    width: 95%;
    border-radius: 10px;
    box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.2);
    margin-bottom: 10px;
}

.message-container
{
    display: flex;
    align-items: center;
    padding: 0 20px;
    margin-bottom: 10px;
}

.my-message
{
    justify-content: flex-end;
}

.my-message .message
{
    background-color: #007bff;
    color: white;
}

.message
{
    padding: 10px;
    background-color: #e0e0e0;
    border-radius: 20px;
    display: inline-block;
    color: black;
    max-width: 70%;
    margin: 5px 0 0 0;
}

.username
{
    font-weight: bold;
    margin-right: 5px;
    color: black;
    margin-bottom: 0;
}

.my-message .username
{
    justify-content: flex-end;
}

.username-container
{
    display: flex;
    align-items: center;
    justify-content: center;
}

.my-file
{
    color: white !important;
    text-decoration: underline;
}

.your-file
{
    color: black;
    text-decoration: underline;
}

.super-container
{
    display: flex;
    height: 100vh;
}

.user-status-bar
{
    width: 15%;
    height: 100%;
    background-color: #f4f4f4d5;
}

.user-list
{
    padding: 10px;
}

.user
{
    display: flex;
    align-items: center;
    border-radius: 10px;
    background-color: white;
    width: 100%;
    box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.2);
}

.username_status
{
    margin-right: 8px;
    color: black;
}

.status
{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.online
{
    background-color: rgb(8, 243, 8);
}

.offline
{
    background-color: red;
}

.afk
{
    background-color: rgb(240, 240, 0);
}

.chat-space-container
{
    width: 85%;
}

.infor
{
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}
</style>

  