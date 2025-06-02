from app import db
from datetime import datetime

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(20), unique=True, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    receiver_name = db.Column(db.String(100), nullable=False)
    receiver_address = db.Column(db.String(200), nullable=False)
    receiver_phone = db.Column(db.String(15))
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)
    courier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    distance = db.Column(db.Float)

    def mark_as_delivered(self):
        self.status = 'delivered'
        self.delivered_at = datetime.utcnow()