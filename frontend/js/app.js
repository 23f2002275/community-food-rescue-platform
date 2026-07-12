const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/listings', component: Listings },
    { path: '/listings/:id', component: ListingDetails },
    { path: '/listings/:id/edit', component: ManageListing, meta: { auth: true, role: 'donor' } },
    { path: '/new-listing', component: ManageListing, meta: { auth: true, role: 'donor' } },
    { path: '/my-listings', component: MyListings, meta: { auth: true, role: 'donor' } },
    { path: '/dashboard', component: Dashboard, meta: { auth: true } },
    { path: '/reservations', component: Reservations, meta: { auth: true } },
    { path: '/admin', component: AdminDashboard, meta: { auth: true, role: 'admin' } }
]

const router = new VueRouter({ routes })

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('food_rescue_token')
    const user = JSON.parse(localStorage.getItem('food_rescue_user') || 'null')
    const role = user && user.roles ? user.roles[0] : null

    if (to.matched.some(record => record.meta.auth) && !token) {
        next('/login')
        return
    }

    const neededRole = to.matched.find(record => record.meta.role)
    if (neededRole && neededRole.meta.role !== role) {
        next('/dashboard')
        return
    }

    next()
})

new Vue({
    el: '#app',
    router,
    data: {
        token: localStorage.getItem('food_rescue_token'),
        user: JSON.parse(localStorage.getItem('food_rescue_user') || 'null')
    },
    computed: {
        isLoggedIn() {
            return Boolean(this.token)
        },
        role() {
            return this.user && this.user.roles ? this.user.roles[0] : null
        }
    },
    created() {
        if (this.token) {
            this.loadUser()
        }
    },
    methods: {
        setAuth(token, user) {
            this.token = token
            this.user = user
            localStorage.setItem('food_rescue_token', token)
            localStorage.setItem('food_rescue_user', JSON.stringify(user))
        },
        async loadUser() {
            try {
                const response = await api.get('/auth/me')
                this.user = response.data
                localStorage.setItem('food_rescue_user', JSON.stringify(response.data))
            } catch (error) {
                this.clearAuth()
            }
        },
        clearAuth() {
            this.token = null
            this.user = null
            localStorage.removeItem('food_rescue_token')
            localStorage.removeItem('food_rescue_user')
        },
        async logout() {
            try {
                await api.post('/auth/logout')
            } catch (error) {
            }
            this.clearAuth()
            this.$router.push('/login')
        }
    }
})
