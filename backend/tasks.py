from datetime import datetime
from celery_worker import celery
from extensions import db
from models import FoodListing

@celery.task(name='tasks.expire_listings')
def expire_listings():
    listings = FoodListing.query.filter(
        FoodListing.status == 'ACTIVE',
        FoodListing.expiry_time <= datetime.utcnow()
    ).all()

    for listing in listings:
        listing.status = 'EXPIRED'

    db.session.commit()
    return {'expired': len(listings)}
