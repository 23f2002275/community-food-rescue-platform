const Dashboard = {
    data() {
        return {
            data: null,
            error: ''
        }
    },
    created() {
        this.load()
    },
    methods: {
        async load() {
            try {
                const response = await api.get('/dashboard')
                this.data = response.data
            } catch (error) {
                this.error = 'Could not load dashboard'
            }
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-1">Dashboard</h1>
            <p class="text-muted mb-4" v-if="$root.user">Welcome back, {{ $root.user.name }}</p>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div v-if="data">
                <div class="row g-4" v-if="data.role === 'donor'">
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Active listings</div><div class="display-6">{{ data.active_listings }}</div></div></div>
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Pending requests</div><div class="display-6">{{ data.pending_requests }}</div></div></div>
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Completed pickups</div><div class="display-6">{{ data.completed_pickups }}</div></div></div>
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Quantity donated</div><div class="display-6">{{ data.quantity_donated }}</div></div></div>
                </div>
                <div class="row g-4" v-if="data.role === 'receiver'">
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Pending</div><div class="display-6">{{ data.pending_requests }}</div></div></div>
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Approved</div><div class="display-6">{{ data.approved_requests }}</div></div></div>
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Collected</div><div class="display-6">{{ data.collected_requests }}</div></div></div>
                    <div class="col-md-3"><div class="card stat-card p-4"><div class="text-muted">Cancelled</div><div class="display-6">{{ data.cancelled_requests }}</div></div></div>
                </div>
                <div class="row g-4" v-if="data.role === 'admin'">
                    <div class="col-md-4"><div class="card stat-card p-4"><div class="text-muted">Active listings</div><div class="display-6">{{ data.active_listings }}</div></div></div>
                    <div class="col-md-4"><div class="card stat-card p-4"><div class="text-muted">Reservations</div><div class="display-6">{{ data.reservations }}</div></div></div>
                    <div class="col-md-4"><div class="card stat-card p-4"><div class="text-muted">Collected</div><div class="display-6">{{ data.collected }}</div></div></div>
                </div>
                <div class="card p-4 mt-4">
                    <div class="d-flex justify-content-between"><h2 class="h5">Recent activity</h2><router-link to="/reservations">Open reservations</router-link></div>
                    <div class="table-responsive mt-3" v-if="data.recent.length">
                        <table class="table"><thead><tr><th>Listing</th><th>Receiver</th><th>Quantity</th><th>Status</th></tr></thead><tbody><tr v-for="item in data.recent" :key="item.id"><td>{{ item.listing_title }}</td><td>{{ item.receiver_name }}</td><td>{{ item.requested_quantity }} {{ item.unit }}</td><td>{{ item.status }}</td></tr></tbody></table>
                    </div>
                    <p class="text-muted mb-0" v-else>No recent activity.</p>
                </div>
            </div>
        </div>
    `
}
