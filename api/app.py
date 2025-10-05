from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import init_db 
from datetime import datetime, timedelta
import pywhatkit
from apscheduler.schedulers.background import BackgroundScheduler 


DATABASE = 'gym_data.db'
MESSAGE = "أهلاً {name}، تذكير بدفع اشتراك نادي الملاكمة. تاريخ الاستحقاق هو {due_date}. شكراً لك!"
WHATSAPP_WAIT_TIME = 35 
#REMINDER_HOUR = 9 

app = Flask(__name__)


def check_and_send_reminders():
    TODAY = datetime.now().date()
    

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, last_payment_date FROM members")
    members = cursor.fetchall()
    conn.close()

    print(f"[{datetime.now()}] بدء فحص التذكيرات...")

    for name, phone, last_payment_date_str in members:
        try:
            last_payment_date = parser.parse(last_payment_date_str).date() 
            due_date = last_payment_date + timedelta(days=30)
            reminder_date = due_date - timedelta(days=2) 
            if TODAY >= reminder_date:
                final_message = MESSAGE.format(name=name, due_date=due_date.strftime('%Y-%m-%d'))
                

                pywhatkit.sendwhatmsg_instantly(phone, final_message, wait_time=WHATSAPP_WAIT_TIME, tab_close=True)
                print(f"✅ تم الإرسال للمشترك {name}. التاريخ: {TODAY}")
                
            else:
                print(f"⏭️ تخطي {name}. التذكير غير مستحق اليوم.")

        except Exception as e:
            print(f"❌ خطأ في إرسال تذكير لـ {name}: {e}")
            


@app.route('/')
def index():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, last_payment_date FROM members ORDER BY name")
    members = cursor.fetchall()
    conn.close()
    

    return render_template('index.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():

    name = request.form['name']
    phone = request.form['phone']
    date_str = request.form['last_payment_date']
    

    try:
        parsed_date = parser.parse(date_str)
        formatted_date_str = parsed_date.strftime('%Y-%m-%d')
    except:

        return "صيغة التاريخ غير صحيحة. حاول: 2025-09-05 أو 05/09/2025", 400


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (name, phone, last_payment_date) VALUES (?, ?, ?)", 
                   (name, phone, formatted_date_str)) # 👈 استخدام formatted_date_str
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
@app.route('/edit_member/<int:member_id>')
def edit_member_form(member_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    member = cursor.fetchone()
    conn.close()
    
    if member is None:
        return "المشترك غير موجود", 404
    

    return render_template('edit_member.html', member=member)
@app.route('/update_member/<int:member_id>', methods=['POST'])
def update_member(member_id):

    name = request.form['name']
    phone = request.form['phone']
    date_str = request.form['last_payment_date']
    

    try:
        parsed_date = parser.parse(date_str)
        formatted_date_str = parsed_date.strftime('%Y-%m-%d')
    except:
        return "صيغة التاريخ غير صحيحة. حاول: 2025-09-05 أو 05/09/2025", 400


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE members SET name = ?, phone = ?, last_payment_date = ?
        WHERE id = ?
    """, (name, phone, formatted_date_str, member_id)) # 👈 استخدام formatted_date_str
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))




#scheduler = BackgroundScheduler()

#scheduler.add_job(check_and_send_reminders, 'cron', hour=REMINDER_HOUR, minute=54)
#scheduler.start()


if __name__ == '__main__': app.run()
