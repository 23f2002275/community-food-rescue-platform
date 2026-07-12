const Listings = {
    data() {
        return {
            items: [],
            filters: {
                keyword: '',
                food_type: '',
                dietary_tag: '',
                location: ''
            },
            page: 1,
            pages: 1,
            total: 0,
            loading: false,
            error: ''
        }
    },
    created() {
        this.loadListings()
    },
    methods: {
        async loadListings(page = 1) {
            this.loading = true
            this.error = ''
            try {
                const params = Object.assign({}, this.filters, { page, per_page: 9 })
                const response = await api.get('/listings', { params })
                this.items = response.data.items
                this.page = response.data.page
                this.pages = response.data.pages
                this.total = response.data.total
            } catch (error) {
                this.error = 'Could not load listings'
            } finally {
                this.loading = false
            }
        },
        clearFilters() {
            this.filters = { keyword: '', food_type: '', dietary_tag: '', location: '' }
            this.loadListings(1)
        },
        formatDate(value) {
            return new Date(value).toLocaleString()
        }
    },
    template: `
        <div class="container page-box">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div><h1 class="h2">Available food</h1><p class="text-muted mb-0">{{ total }} active listings</p></div>
                <router-link class="btn btn-success" to="/new-listing" v-if="$root.role === 'donor'">Add listing</router-link>
            </div>
            <div class="card p-4 mb-4">
                <form class="row g-3" @submit.prevent="loadListings(1)">
                    <div class="col-md-4"><input class="form-control" placeholder="Search title" v-model.trim="filters.keyword"></div>
                    <div class="col-md-2"><input class="form-control" placeholder="Food type" v-model.trim="filters.food_type"></div>
                    <div class="col-md-2"><input class="form-control" placeholder="Dietary tag" v-model.trim="filters.dietary_tag"></div>
                    <div class="col-md-2"><input class="form-control" placeholder="Location" v-model.trim="filters.location"></div>
                    <div class="col-md-2 d-flex gap-2"><button class="btn btn-success flex-fill">Search</button><button type="button" class="btn btn-outline-secondary" @click="clearFilters">Clear</button></div>
                </form>
            </div>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div class="card p-5 text-center" v-else-if="!items.length">No active listings found.</div>
            <div class="row g-4" v-else>
                <div class="col-md-6 col-lg-4" v-for="listing in items" :key="listing.id">
                    <div class="card listing-card p-4">
                        <div class="d-flex justify-content-between mb-3"><span class="badge bg-success">{{ listing.food_type }}</span><span class="badge bg-light text-dark">{{ listing.dietary_tag || 'Any' }}</span></div>
                        <h2 class="h5">{{ listing.title }}</h2>
                        <p class="text-muted mb-2">{{ listing.pickup_location }}</p>
                        <p class="fw-semibold">{{ listing.available_quantity }} {{ listing.unit }} available</p>
                        <small class="text-danger">Expires {{ formatDate(listing.expiry_time) }}</small>
                        <router-link class="btn btn-outline-success mt-4" :to="'/listings/' + listing.id">View details</router-link>
                    </div>
                </div>
            </div>
            <div class="d-flex justify-content-center gap-2 mt-4" v-if="pages > 1">
                <button class="btn btn-outline-success" :disabled="page <= 1" @click="loadListings(page - 1)">Previous</button>
                <span class="align-self-center">Page {{ page }} of {{ pages }}</span>
                <button class="btn btn-outline-success" :disabled="page >= pages" @click="loadListings(page + 1)">Next</button>
            </div>
        </div>
    `
}
