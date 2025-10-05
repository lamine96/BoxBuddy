import os
from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///gym_data.db') 

app = Flask(__name__)

if DATABASE_URL.startswith('postgresql://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Member(db.Model):
    __tablename__ = 'members' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    last_payment_date = db.Column(db.String(10), nullable=False) 

@app.teardown_request
def shutdown_session(exception=None):
    """تضمن إزالة الجلسة بعد اكتمال كل طلب."""
    db.session.remove()

@app.before_request
def setup_database():
    """يضمن وجود الجداول قبل معالجة أي طلب."""
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    members = Member.query.order_by(Member.name).all()
    members_data = [[m.id, m.name, m.phone, m.last_payment_date] for m in members]
    return render_template('index.html', members=members_data)

@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        db.session.add(new_member)
        db.session.commit()
    except Exception as e:
        db.session.rollback() 
        return f"حدث خطأ في قاعدة البيانات أثناء إضافة المشترك. يرجى مراجعة المدخلات: {e}", 500
    
    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    db.session.delete(member_to_delete)
    db.session.commit()
    return redirect(url_for('index'))
server = app
