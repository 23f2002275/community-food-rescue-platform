const MyListings = {
    data() {
        return {
            items: [],
            error: '',
            success: ''
        }
    },
    created() {
        this.load()
    },
    methods: {
        async load() {
            try {
                const response = await api.get('/listings/mine')
                this.items = response.data
            } catch (error) {
                this.error = 'Could not load your listings'
            }
        },
        async changeStatus(item, status) {
            this.error = ''
            try {
                await api.patch('/listings/' + item.id + '/status', { status })
                this.success = 'Status updated'
                this.load()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not update status'
            }
        },
        async remove(item) {
            if (!confirm('Delete this listing?')) return
            try {
                await api.delete('/listings/' + item.id)
                this.load()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not delete listing'
            }
        },
        formatDate(value) {
            return new Date(value).toLocaleString()
        }
    },
    template: `
        <div class="container page-box">
            <div class="d-flex justify-content-between align-items-center mb-4"><div><h1 class="h2">My listings</h1><p class="text-muted mb-0">Manage your food donations</p></div><router-link class="btn btn-success" to="/new-listing">Create listing</router-link></div>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="alert alert-success" v-if="success">{{ success }}</div>
            <div class="card p-4 text-center" v-if="!items.length">You have not created any listings.</div>
            <div class="card overflow-hidden" v-else>
                <div class="table-responsive">
                    <table class="table mb-0">
                        <thead><tr><th>Listing</th><th>Quantity</th><th>Expiry</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="item in items" :key="item.id">
                                <td><strong>{{ item.title }}</strong><div class="small text-muted">{{ item.pickup_location }}</div></td>
                                <td>{{ item.available_quantity }} / {{ item.total_quantity }} {{ item.unit }}</td>
                                <td>{{ formatDate(item.expiry_time) }}</td>
                                <td><span class="badge bg-secondary status-badge">{{ item.status }}</span></td>
                                <td>
                                    <div class="d-flex flex-wrap gap-1">
                                        <router-link class="btn btn-sm btn-outline-primary" :to="'/listings/' + item.id + '/edit'">Edit</router-link>
                                        <button class="btn btn-sm btn-outline-success" v-if="item.status === 'DRAFT'" @click="changeStatus(item, 'ACTIVE')">Publish</button>
                                        <button class="btn btn-sm btn-outline-warning" v-if="item.status === 'ACTIVE'" @click="changeStatus(item, 'CLOSED')">Close</button>
                                        <button class="btn btn-sm btn-outline-danger" @click="remove(item)">Delete</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `
}
