const ListingDetails = {
    data() {
        return {
            listing: null,
            form: {
                requested_quantity: 1,
                message: ''
            },
            error: '',
            success: '',
            loading: true
        }
    },
    created() {
        this.loadListing()
    },
    methods: {
        async loadListing() {
            this.loading = true
            try {
                const response = await api.get('/listings/' + this.$route.params.id)
                this.listing = response.data
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Listing not found'
            } finally {
                this.loading = false
            }
        },
        async reserve() {
            this.error = ''
            this.success = ''
            try {
                const response = await api.post('/listings/' + this.listing.id + '/reservations', this.form)
                this.success = response.data.message
                this.form = { requested_quantity: 1, message: '' }
            } catch (error) {
                if (!this.$root.isLoggedIn) {
                    this.$router.push('/login')
                    return
                }
                this.error = error.response && error.response.data ? error.response.data.message : 'Request failed'
            }
        },
        formatDate(value) {
            return new Date(value).toLocaleString()
        }
    },
    template: `
        <div class="container page-box">
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="row g-4" v-if="listing">
                <div class="col-lg-8">
                    <div class="card p-4 p-md-5">
                        <div class="d-flex gap-2 mb-3"><span class="badge bg-success">{{ listing.food_type }}</span><span class="badge bg-secondary">{{ listing.dietary_tag || 'No dietary tag' }}</span></div>
                        <h1 class="h2">{{ listing.title }}</h1>
                        <p class="text-muted">Posted by {{ listing.donor_name }}</p>
                        <p class="lead">{{ listing.description || 'No description provided.' }}</p>
                        <hr>
                        <div class="row g-3">
                            <div class="col-md-6"><strong>Available</strong><div>{{ listing.available_quantity }} {{ listing.unit }}</div></div>
                            <div class="col-md-6"><strong>Pickup location</strong><div>{{ listing.pickup_location }}</div></div>
                            <div class="col-md-6"><strong>Expiry</strong><div>{{ formatDate(listing.expiry_time) }}</div></div>
                            <div class="col-md-6"><strong>Status</strong><div>{{ listing.status }}</div></div>
                        </div>
                        <div class="alert alert-light mt-4 mb-0"><strong>Pickup notes:</strong> {{ listing.pickup_notes || 'No extra notes' }}</div>
                    </div>
                    <div class="card p-4 mt-4" v-if="listing.reviews && listing.reviews.length">
                        <h2 class="h5">Reviews</h2>
                        <div class="border-top pt-3 mt-3" v-for="review in listing.reviews" :key="review.id">
                            <strong>{{ review.reviewer_name }}</strong> · {{ review.rating }}/5
                            <p class="mb-0">{{ review.comment }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card p-4" v-if="$root.role === 'receiver'">
                        <h2 class="h5">Request food</h2>
                        <div class="alert alert-success" v-if="success">{{ success }}</div>
                        <form @submit.prevent="reserve">
                            <div class="mb-3"><label class="form-label">Quantity</label><input class="form-control" type="number" min="1" :max="listing.available_quantity" v-model.number="form.requested_quantity" required></div>
                            <div class="mb-3"><label class="form-label">Message</label><textarea class="form-control" rows="3" v-model.trim="form.message"></textarea></div>
                            <button class="btn btn-success w-100">Send request</button>
                        </form>
                    </div>
                    <div class="card p-4" v-else-if="!$root.isLoggedIn">
                        <p>Login as a receiver to request this food.</p>
                        <router-link class="btn btn-success" to="/login">Login</router-link>
                    </div>
                    <div class="card p-4" v-else>
                        <p class="mb-0">Only receiver accounts can request listings.</p>
                    </div>
                </div>
            </div>
        </div>
    `
}
