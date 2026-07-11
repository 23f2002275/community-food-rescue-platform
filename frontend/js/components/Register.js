const Register = {
    data() {
        return {
            form: {
                name: '',
                email: '',
                password: '',
                role: 'receiver',
                phone: '',
                address: ''
            },
            error: '',
            success: '',
            loading: false
        }
    },
    methods: {
        async submit() {
            this.error = ''
            this.success = ''
            this.loading = true
            try {
                const response = await api.post('/auth/register', this.form)
                this.success = response.data.message
                setTimeout(() => this.$router.push('/login'), 700)
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Registration failed'
            } finally {
                this.loading = false
            }
        }
    },
    template: `
        <div class="container auth-box">
            <div class="card p-4 p-md-5">
                <h1 class="h3 mb-4">Create account</h1>
                <div class="alert alert-danger" v-if="error">{{ error }}</div>
                <div class="alert alert-success" v-if="success">{{ success }}</div>
                <form @submit.prevent="submit">
                    <div class="mb-3"><label class="form-label">Name</label><input class="form-control" v-model.trim="form.name" required></div>
                    <div class="mb-3"><label class="form-label">Email</label><input class="form-control" type="email" v-model.trim="form.email" required></div>
                    <div class="mb-3"><label class="form-label">Password</label><input class="form-control" type="password" minlength="6" v-model="form.password" required></div>
                    <div class="mb-3">
                        <label class="form-label">Account type</label>
                        <select class="form-select" v-model="form.role">
                            <option value="receiver">Receiver</option>
                            <option value="donor">Donor</option>
                        </select>
                    </div>
                    <div class="mb-3"><label class="form-label">Phone</label><input class="form-control" v-model.trim="form.phone"></div>
                    <div class="mb-3"><label class="form-label">Address</label><textarea class="form-control" rows="2" v-model.trim="form.address"></textarea></div>
                    <button class="btn btn-success w-100" :disabled="loading">{{ loading ? 'Creating...' : 'Register' }}</button>
                </form>
            </div>
        </div>
    `
}
