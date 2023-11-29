import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'

export const useUserStore = defineStore('users', () =>
{
    const user = ref(null);
    const token = ref(null);
    const errorMessage = ref('');
    const loading = ref(false);
    const router = useRouter();

    const handleLogin = async (credentials) =>
    {
        const { username, password } = credentials;

        loading.value = true;

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        await axios.post('http://localhost:8000/auth/login', formData)
            .then(async (response) =>
            {
                localStorage.setItem('token', response.data.access_token)
                token.value = response.data.access_token;

                axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('token');

                const userInfo = await axios.get('http://localhost:8000/auth/get_current_user');

                user.value =
                {
                    username: userInfo.data.username,
                    status: 'Đăng nhập'
                }

                localStorage.setItem('token', token.value);

                loading.value = false;
                errorMessage.value = '';
            })
            .catch((error) =>
            {
                loading.value = false;
                return errorMessage.value = "Thông tin đăng nhập không đúng!";
            });
    }

    const handleLogout = async () =>
    {
        user.value = null;
        token.value = '';
        localStorage.removeItem('token');
    }

    const clearErrorMessage = () =>
    {
        errorMessage.value = '';
    }

    const handleSignup = async (credentials) =>
    {
        const { username, password, re_password, full_name } = credentials;

        if (password.length < 8)
        {
            return errorMessage.value = 'Mật khẩu cần có tối thiểu 8 ký tự!';
        }

        if (password != re_password)
        {
            return errorMessage.value = 'Mật khẩu không khớp!';
        }

        loading.value = true;

        errorMessage.value = '';

        // Thêm người dùng vào database
        try
        {
            const response = await axios.post('http://localhost:8000/auth/register',
                {
                    full_name: full_name,
                    username: username,
                    password: password
                });

            user.value =
            {
                data: response.data,
                status: 'Đăng ký'
            }

            loading.value = false;
        }
        catch (e)
        {
            loading.value = false;
            return errorMessage.value = e.response.data.detail;
        }
    }

    const getUser = async () =>
    {
        token.value = localStorage.getItem('token');

        const tokenJWT = localStorage.getItem('token');

        if (tokenJWT)
        {
            axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('token');

            const userInfo = await axios.get('http://localhost:8000/auth/get_current_user').catch(async (e) =>
            {
                message.error(
                    'Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại để tiếp tục!',
                    3,
                );
                await handleLogout();
                router.push('/');
            });

            user.value =
            {
                username: userInfo.data.username,
            }
        }
    }

    return { user, token, handleLogin, handleLogout, handleSignup, clearErrorMessage, getUser, errorMessage, loading }
})
