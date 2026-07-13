const Reservations = {
    data() {
        return {
            items: [],
            error: '',
            success: '',
            review: {
                reservation_id: null,
                rating: 5,
                comment: ''
            }
        }
    },
    created() {
        this.load()
    },
    methods: {
        async load() {
            try {
                const response = await api.get('/reservations/mine')
                this.items = response.data
            } catch (error) {
                this.error = 'Could not load reservations'
            }
        },
        async action(item, name) {
            this.error = ''
            this.success = ''
            try {
                const response = await api.patch('/reservations/' + item.id + '/' + name)
                this.success = response.data.message
                this.load()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Action failed'
            }
        },
        openReview(item) {
            this.review = { reservation_id: item.id, rating: 5, comment: '' }
        },
        async submitReview() {
            try {
                const response = await api.post('/reservations/' + this.review.reservation_id + '/reviews', this.review)
                this.success = response.data.message
                this.review = { reservation_id: null, rating: 5, comment: '' }
                this.load()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Review failed'
            }
        },
        formatDate(value) {
            return value ? new Date(value).toLocaleString() : '-'
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-1">Reservations</h1>
            <p class="text-muted mb-4">Requests involving your account</p>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="alert alert-success" v-if="success">{{ success }}</div>
            <div class="card p-4 mb-4" v-if="review.reservation_id">
                <h2 class="h5">Add review</h2>
                <form class="row g-3" @submit.prevent="submitReview">
                    <div class="col-md-2"><select class="form-select" v-model.number="review.rating"><option v-for="n in 5" :value="n">{{ n }}/5</option></select></div>
                    <div class="col-md-8"><input class="form-control" placeholder="Comment" v-model.trim="review.comment"></div>
                    <div class="col-md-2"><button class="btn btn-success w-100">Submit</button></div>
                </form>
            </div>
            <div class="card p-5 text-center" v-if="!items.length">No reservations found.</div>
            <div class="card overflow-hidden" v-else>
                <div class="table-responsive">
                    <table class="table mb-0">
                        <thead><tr><th>Listing</th><th>People</th><th>Quantity</th><th>Requested</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="item in items" :key="item.id">
                                <td><router-link :to="'/listings/' + item.listing_id">{{ item.listing_title }}</router-link></td>
                                <td><div>Donor: {{ item.donor_name }}</div><div>Receiver: {{ item.receiver_name }}</div></td>
                                <td>{{ item.requested_quantity }} {{ item.unit }}</td>
                                <td>{{ formatDate(item.requested_at) }}</td>
                                <td><span class="badge bg-secondary">{{ item.status }}</span></td>
                                <td>
                                    <div class="d-flex flex-wrap gap-1">
                                        <button class="btn btn-sm btn-success" v-if="$root.role === 'donor' && item.status === 'PENDING'" @click="action(item, 'approve')">Approve</button>
                                        <button class="btn btn-sm btn-outline-danger" v-if="$root.role === 'donor' && item.status === 'PENDING'" @click="action(item, 'reject')">Reject</button>
                                        <button class="btn btn-sm btn-primary" v-if="$root.role === 'donor' && item.status === 'APPROVED'" @click="action(item, 'collect')">Collected</button>
                                        <button class="btn btn-sm btn-outline-warning" v-if="['PENDING', 'APPROVED'].includes(item.status)" @click="action(item, 'cancel')">Cancel</button>
                                        <button class="btn btn-sm btn-outline-success" v-if="item.status === 'COLLECTED' && !item.reviewed_by.includes($root.user.id)" @click="openReview(item)">Review</button>
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
