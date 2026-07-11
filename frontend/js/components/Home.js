const Home = {
    data() {
        return {
            listings: []
        }
    },
    created() {
        this.loadListings()
    },
    methods: {
        async loadListings() {
            try {
                const response = await api.get('/listings?per_page=3')
                this.listings = response.data.items
            } catch (error) {
                this.listings = []
            }
        }
    },
    template: `
        <div>
            <section class="hero">
                <div class="container text-center">
                    <h1 class="display-4 fw-bold">Share food before it is wasted</h1>
                    <p class="lead mt-3">Donors publish surplus food and receivers reserve it for collection.</p>
                    <router-link class="btn btn-success btn-lg mt-3" to="/listings">Browse available food</router-link>
                </div>
            </section>
            <section class="container py-5">
                <div class="row g-4 mb-5">
                    <div class="col-md-4"><div class="card p-4 text-center"><h3>1</h3><p class="mb-0">Donors create a food listing</p></div></div>
                    <div class="col-md-4"><div class="card p-4 text-center"><h3>2</h3><p class="mb-0">Receivers request a quantity</p></div></div>
                    <div class="col-md-4"><div class="card p-4 text-center"><h3>3</h3><p class="mb-0">Pickup is approved and collected</p></div></div>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2 class="h4 mb-0">Latest listings</h2>
                    <router-link to="/listings">View all</router-link>
                </div>
                <div class="row g-4">
                    <div class="col-md-4" v-for="listing in listings" :key="listing.id">
                        <div class="card listing-card p-4">
                            <span class="badge bg-success align-self-start mb-3">{{ listing.food_type }}</span>
                            <h3 class="h5">{{ listing.title }}</h3>
                            <p class="text-muted">{{ listing.pickup_location }}</p>
                            <p>{{ listing.available_quantity }} {{ listing.unit }} available</p>
                            <router-link class="btn btn-outline-success mt-auto" :to="'/listings/' + listing.id">View details</router-link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    `
}
