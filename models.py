from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class InventoryModel(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer(), unique=True)
    item_name = db.Column(db.String())
    stock = db.Column(db.Integer())

    def __init__(self, item_id, item_name, stock):
        self.item_id = item_id
        self.item_name = item_name
        self.stock = stock

    def __repr__(self):
        return f"id #{self.item_id} - {self.item_name} - {self.stock} left"
