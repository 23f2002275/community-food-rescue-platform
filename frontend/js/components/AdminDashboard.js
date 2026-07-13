const AdminDashboard = {
    data() {
        return {
            tab: 'statistics',
            statistics: null,
            users: [],
            listings: [],
            error: '',
            success: ''
        }
    },
    created() {
        this.loadAll()
    },
    methods: {
        async loadAll() {
            this.error = ''
            try {
                const [stats, users, listings] = await Promise.all([
                    api.get('/admin/statistics'),
                    api.get('/admin/users'),
                    api.get('/admin/listings')
                ])
                this.statistics = stats.data
                this.users = users.data
                this.listings = listings.data
            } catch (error) {
                this.error = 'Could not load admin data'
            }
        },
        async setActive(user, active) {
            try {
                await api.patch('/admin/users/' + user.id + '/active', { active })
                this.success = 'User status updated'
                this.loadAll()
            } catch (error) {
                this.error = 'Could not update user'
            }
        },
        async setVisible(listing, visible) {
            try {
                await api.patch('/admin/listings/' + listing.id + '/visibility', { visible })
                this.success = 'Listing visibility updated'
                this.loadAll()
            } catch (error) {
                this.error = 'Could not update listing'
            }
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-4">Admin dashboard</h1>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="alert alert-success" v-if="success">{{ success }}</div>
            <div class="btn-group mb-4"><button class="btn" :class="tab === 'statistics' ? 'btn-success' : 'btn-outline-success'" @click="tab = 'statistics'">Statistics</button><button class="btn" :class="tab === 'users' ? 'btn-success' : 'btn-outline-success'" @click="tab = 'users'">Users</button><button class="btn" :class="tab === 'listings' ? 'btn-success' : 'btn-outline-success'" @click="tab = 'listings'">Listings</button></div>
            <div class="row g-4" v-if="tab === 'statistics' && statistics">
                <div class="col-md-3" v-for="(value, key) in statistics" :key="key"><div class="card stat-card p-4"><div class="text-muted text-capitalize">{{ key.replaceAll('_', ' ') }}</div><div class="display-6">{{ value }}</div></div></div>
            </div>
            <div class="card overflow-hidden" v-if="tab === 'users'">
                <div class="table-responsive"><table class="table mb-0"><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Action</th></tr></thead><tbody><tr v-for="user in users" :key="user.id"><td><strong>{{ user.name }}</strong><div class="small text-muted">{{ user.email }}</div></td><td>{{ user.roles.join(', ') }}</td><td>{{ user.active ? 'Active' : 'Blocked' }}</td><td><button class="btn btn-sm" :class="user.active ? 'btn-outline-danger' : 'btn-outline-success'" @click="setActive(user, !user.active)">{{ user.active ? 'Block' : 'Activate' }}</button></td></tr></tbody></table></div>
            </div>
            <div class="card overflow-hidden" v-if="tab === 'listings'">
                <div class="table-responsive"><table class="table mb-0"><thead><tr><th>Listing</th><th>Donor</th><th>Status</th><th>Action</th></tr></thead><tbody><tr v-for="listing in listings" :key="listing.id"><td>{{ listing.title }}</td><td>{{ listing.donor_name }}</td><td>{{ listing.status }}</td><td><button class="btn btn-sm" :class="listing.status === 'HIDDEN' ? 'btn-outline-success' : 'btn-outline-danger'" @click="setVisible(listing, listing.status === 'HIDDEN')">{{ listing.status === 'HIDDEN' ? 'Restore' : 'Hide' }}</button></td></tr></tbody></table></div>
            </div>
        </div>
    `
}
