const Login = {
    data() {
        return {
            form: {
                email: '',
                password: ''
            },
            error: '',
            loading: false
        }
    },
    methods: {
        async submit() {
            this.error = ''
            this.loading = true
            try {
                const response = await api.post('/auth/login', this.form)
                this.$root.setAuth(response.data.token, response.data.user)
                this.$router.push('/dashboard')
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Login failed'
            } finally {
                this.loading = false
            }
        }
    },
    template: `
        <div class="container auth-box">
            <div class="card p-4 p-md-5">
                <h1 class="h3 mb-4">Login</h1>
                <div class="alert alert-danger" v-if="error">{{ error }}</div>
                <form @submit.prevent="submit">
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input class="form-control" type="email" v-model.trim="form.email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input class="form-control" type="password" v-model="form.password" required>
                    </div>
                    <button class="btn btn-success w-100" :disabled="loading">{{ loading ? 'Please wait...' : 'Login' }}</button>
                </form>
                <p class="text-muted mt-4 mb-0">Demo donor: donor@foodrescue.com / donor123</p>
                <p class="text-muted mb-0">Demo receiver: receiver@foodrescue.com / receiver123</p>
                <p class="text-muted mb-0">Demo admin: admin@foodrescue.com / admin123</p>
            </div>
        </div>
    `
}
