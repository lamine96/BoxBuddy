import sqlite3

def init_db():

    conn = sqlite3.connect('gym_data.db')
    cursor = conn.cursor()



    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            last_payment_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("تم إنشاء أو تحديث قاعدة بيانات SQLite بنجاح.")
