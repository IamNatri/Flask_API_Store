from db import db


class item_tags_sdt(db.Model):
    __tablename__ = "item_tags_sdt"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
