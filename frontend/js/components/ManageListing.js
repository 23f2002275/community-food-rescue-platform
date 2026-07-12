const ManageListing = {
    data() {
        return {
            form: {
                title: '',
                description: '',
                food_type: '',
                dietary_tag: '',
                total_quantity: 1,
                unit: 'plates',
                pickup_location: '',
                pickup_notes: '',
                expiry_time: '',
                status: 'DRAFT'
            },
            error: '',
            loading: false,
            editing: Boolean(this.$route.params.id)
        }
    },
    created() {
        if (this.editing) {
            this.loadListing()
        }
    },
    methods: {
        async loadListing() {
            try {
                const response = await api.get('/listings/' + this.$route.params.id)
                const item = response.data
                this.form = {
                    title: item.title,
                    description: item.description || '',
                    food_type: item.food_type,
                    dietary_tag: item.dietary_tag || '',
                    total_quantity: item.total_quantity,
                    unit: item.unit,
                    pickup_location: item.pickup_location,
                    pickup_notes: item.pickup_notes || '',
                    expiry_time: item.expiry_time.slice(0, 16),
                    status: item.status
                }
            } catch (error) {
                this.error = 'Could not load listing'
            }
        },
        async submit() {
            this.error = ''
            this.loading = true
            try {
                if (this.editing) {
                    await api.put('/listings/' + this.$route.params.id, this.form)
                } else {
                    await api.post('/listings', this.form)
                }
                this.$router.push('/my-listings')
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not save listing'
            } finally {
                this.loading = false
            }
        }
    },
    template: `
        <div class="container page-box">
            <div class="card p-4 p-md-5">
                <h1 class="h3 mb-4">{{ editing ? 'Edit listing' : 'Create listing' }}</h1>
                <div class="alert alert-danger" v-if="error">{{ error }}</div>
                <form @submit.prevent="submit">
                    <div class="row g-3">
                        <div class="col-md-8"><label class="form-label">Title</label><input class="form-control" v-model.trim="form.title" required></div>
                        <div class="col-md-4"><label class="form-label">Food type</label><input class="form-control" v-model.trim="form.food_type" required></div>
                        <div class="col-12"><label class="form-label">Description</label><textarea class="form-control" rows="3" v-model.trim="form.description"></textarea></div>
                        <div class="col-md-4"><label class="form-label">Dietary tag</label><input class="form-control" placeholder="Vegetarian" v-model.trim="form.dietary_tag"></div>
                        <div class="col-md-4"><label class="form-label">Quantity</label><input class="form-control" type="number" min="1" v-model.number="form.total_quantity" required></div>
                        <div class="col-md-4"><label class="form-label">Unit</label><input class="form-control" v-model.trim="form.unit" required></div>
                        <div class="col-md-7"><label class="form-label">Pickup location</label><input class="form-control" v-model.trim="form.pickup_location" required></div>
                        <div class="col-md-5"><label class="form-label">Expiry time</label><input class="form-control" type="datetime-local" v-model="form.expiry_time" required></div>
                        <div class="col-12"><label class="form-label">Pickup notes</label><textarea class="form-control" rows="2" v-model.trim="form.pickup_notes"></textarea></div>
                        <div class="col-md-4" v-if="!editing"><label class="form-label">Initial status</label><select class="form-select" v-model="form.status"><option value="DRAFT">Draft</option><option value="ACTIVE">Active</option></select></div>
                    </div>
                    <div class="d-flex gap-2 mt-4"><button class="btn btn-success" :disabled="loading">{{ loading ? 'Saving...' : 'Save listing' }}</button><router-link class="btn btn-outline-secondary" to="/my-listings">Cancel</router-link></div>
                </form>
            </div>
        </div>
    `
}
