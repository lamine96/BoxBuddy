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
    name = request.form['name']
    phone = request.form['phone'].strip() 
    date_str = request.form['last_payment_date']
    
    if not all([name, phone, date_str]):
        return "يجب ملء جميع الحقول (الاسم، الهاتف، تاريخ الدفع).", 400

    try:
        parsed_date = parser.parse(date_str)
        formatted_date_str = parsed_date.strftime('%Y-%m-%d')
    except:
        return "صيغة التاريخ غير صحيحة. حاول: 2025-09-05 أو 05/09/2025", 400

    new_member = Member(name=name, phone=phone, last_payment_date=formatted_date_str)
    
    try:
        db.session.add(new_member)
        db.session.commit()
    except Exception as e:
        db.session.rollback() 
        return f"حدث خطأ في قاعدة البيانات أثناء إضافة المشترك. يرجى مراجعة المدخلات: {e}", 500
    
    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    member_to_delete = Member.query.get_or_404(member_id)
    db.session.delete(member_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_member/<int:member_id>')
def edit_member_form(member_id):
    member = Member.query.get_or_404(member_id)
    member_data = [member.id, member.name, member.phone, member.last_payment_date]
    return render_template('edit_member.html', member=member_data)

@app.route('/update_member/<int:member_id>', methods=['POST'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    
    name = request.form['name']
    phone = request.form['phone']
    date_str = request.form['last_payment_date']
    
    try:
        parsed_date = parser.parse(date_str)
        formatted_date_str = parsed_date.strftime('%Y-%m-%d')
    except:
        return "صيغة التاريخ غير صحيحة. حاول: 2025-09-05 أو 05/09/2025", 400

    member.name = name
    member.phone = phone
    member.last_payment_date = formatted_date_str
    
    db.session.commit()
    
    return redirect(url_for('index'))
server = app
