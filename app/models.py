from datetime import datetime
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True,nullable=False)
    email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class People(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    salutation: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    organization: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128), index=True)
    role: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    gender: so.Mapped[Optional[str]] = so.mapped_column(sa.String(16))
    city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    state: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    business_phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    mobile_phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    sector: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    linkedin: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    def __repr__(self):
        return '<People {} {}>'.format(self.first_name or '', self.last_name or '')
    
    def as_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != 'id'  # Exclude auto-incremented id
        }
    
class Log(db.Model):
    '''
    result: summary of final outcome e.g. Successfully updated 1000 records. Failed 12 records.
    status: status of this record processing (e.g., "completed", "error", or "in progress").
    created_at: when the task started.
    '''
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    status: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    result: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Log {}>'.format(self.id)
    
class LogDetail(db.Model):
    '''
    log_id: foreign key to Log.id
    record_name: name of the record being processed (e.g., "John Doe")
    status: status of this record processing (e.g., "success", "error").
    source: source URL (if scraping).
    detail: Extra info (e.g. raw scraped fields, exception trace).
    created_at: when the task started.
    '''
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    log_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey("log.id"))
    record_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    status: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    source: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128)) # source url
    detail: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.now)

    def __repr__(self):
        return '<LogDetail {}>'.format(self.id)
    
class IP(db.Model):  
    __tablename__ = "ip"

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=False)
    port: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32), nullable=True)
    source: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128), nullable=True)
    is_expired: so.Mapped[Optional[bool]] = so.mapped_column(sa.Boolean, default=False, nullable=False)

class GovPeople(db.Model):
    __tablename__ = "gov_people"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    salutation: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    organization: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128), index=True)
    role: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    gender: so.Mapped[Optional[str]] = so.mapped_column(sa.String(16))
    city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    state: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    business_phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    mobile_phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    sector: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))

    def __repr__(self):
        return '<GovPeople {} {}>'.format(self.first_name or '', self.last_name or '')

    def as_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != 'id'  # Exclude auto-incremented id
        }