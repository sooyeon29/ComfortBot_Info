from flask import Flask, request, jsonify, send_from_directory, session
import openai
import sqlite3
import os
from datetime import datetime
import pytz

# Flask 앱 설정
app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.urandom(24)
KST = pytz.timezone('Asia/Seoul')

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")


# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    dob TEXT,
                    gender TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    chat_history TEXT,
                    status TEXT
                )''')
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    return send_from_directory(".", "index.html")


@app.route('/reset-session', methods=['POST'])
def reset_session():
    # session.clear()
    return jsonify({"message": "새로운 사용자가 인식되었습니다."})


@app.route('/user-info', methods=['POST'])
def save_user_info():
    user_info = request.json
    # session['user_info'] = user_info
    # session['start_time'] = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    # session['chat_history'] = []

    # 챗봇 첫 메시지
    # first_bot_message = f"Hi {user_info['name']}!"
    # session['chat_history'].append({"user": None, "bot": first_bot_message})

    # 사용자 정보를 DB에 삽입
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    # 중복 여부 확인
    # c.execute("SELECT COUNT(*) FROM users WHERE name = ? AND start_time = ?",
    #           (user_info['name'], session['start_time']))
    # if c.fetchone()[0] == 0:
    #     c.execute(
    #         '''INSERT INTO users (name, dob, gender, start_time, chat_history, status)
    #                  VALUES (?, ?, ?, ?, ?, ?)''',
    #         (user_info['name'], user_info['dob'], user_info['gender'],
    #          session['start_time'], '[]', 'incomplete'))
    # conn.commit()
    # conn.close()
    start_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute(
        '''INSERT INTO users (name, dob, gender, start_time, chat_history, status)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_info['name'], user_info['dob'], user_info['gender'],
         start_time, '[]', 'incomplete'))
    conn.commit()
    conn.close()


    return jsonify({"message": "사용자 정보가 성공적으로 저장되었습니다."})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("user_input", "")

    user_info = data.get("user_info", {})  # ← 새로 추가
    chat_history = data.get("chat_history", [])  # ← 새로 추가

    # chat_history = session.get('chat_history', [])

    # 사용자의 첫 메시지 저장
    chat_history.append({"user": user_input, "bot": None})

    # GPT 호출을 통해 사랑세포 응답 생성
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # GPT-4o 모델 호출
            messages=[{
                "role":
                "system",
                "content":
                """
You are a chatbot named "Roro."

Roro is not designed to provide emotional comfort through empathy. Instead, your purpose is to offer informational comfort by delivering accurate, structured explanations that reduce user anxiety and confusion.

Roro’s users are facing concerns such as:
- Career uncertainty or academic pressure (grades, exams, deadlines)
- Difficulties with relationships or social isolation
- Financial stress or family conflict
- Health or well-being concerns
- Struggles with confidence or self-worth
- Romantic or relationship stress


Your role is to:
- Help users logically organize their thoughts
- Provide clear and structured information
- Support users in making informed decisions

Follow these seven key rules:

1. **Information-focused, minimal emotional expression**  
   Do NOT use emotionally empathetic language.  
   ✅ Use objective, structured guidance instead.  
   Example: “This type of situation is typically addressed in the following way.”

2. **Always follow: Problem definition → Information structuring → Decision guidance**  
   ✅ Clarify the problem, outline the key points, and provide options.  
   Example: “Your situation can be divided into two areas: A and B. Let me explain each.”

3. **Use structured formats**  
   ✅ Present information using lists, steps, or comparisons.  
   Example: “Here are three strategies to consider: 1)… 2)… 3)…”

4. **No emotional comfort, only cognitive clarity**  
   ❌ Avoid phrases like “That must have been hard.”  
   ✅ Use: “This type of concern is common. A standard approach is as follows.”

5. **Neutral and calm tone**  
   ✅ Use polite, professional, and emotionally restrained language.  
   Example: “Let me know if you need further clarification.”

6. **Keep flow natural and progressive**  
   ✅ Guide step by step. Avoid repetitive phrases.  
   ✅ Naturally transition to related topics.  
   Example: “Would you like to explore this further?”

7. **No emojis or emoticons**  
   ❌ Do not use any visual symbols to express emotion.

---

Sample conversation flow:

- Start: “Which part is most concerning to you? If you share more, I’ll help organize it for you.”
- Organize: “It seems your concern falls into two areas: 1) A, 2) B.”
- Inform: “Let me explain the pros and cons of each path.”
- Support decision: “Do you feel one option suits your needs better?”
- Close: “I hope this helped clarify things. Let me know if you’d like to go deeper.”

Remember: You are not a therapist or emotional supporter. You are a calm, clear, structured assistant that reduces uncertainty and supports logical understanding.

                    """
            }, {
                "role": "user",
                "content": user_input
            }])
        bot_reply = response['choices'][0]['message']['content']
    except Exception as e:
        print("🔥 GPT 호출 오류:", e)  # 🔥 이걸 반드시 추가!
        bot_reply = "죄송해요, 오류가 발생했습니다."

    # 응답 저장 및 반환
    chat_history.append({"user": user_input, "bot": bot_reply})
    # session['chat_history'] = chat_history

    # 실시간 저장

    # conn = sqlite3.connect('chatbot.db')
    # c = conn.cursor()
    # c.execute(
    #     'UPDATE users SET chat_history = ? WHERE name = ? AND start_time = ?',

    # conn.commit()
    # conn.close()
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    start_time = data.get("start_time") or datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''INSERT OR REPLACE INTO users (name, dob, gender, start_time, chat_history, status)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_info.get('name'), user_info.get('dob'), user_info.get('gender'),
         start_time, str(chat_history), 'incomplete'))
    conn.commit()
    conn.close()


    # return jsonify({"reply": bot_reply})
    return jsonify({
        "reply": bot_reply,
        "chat_history": chat_history,
        "start_time": start_time
    })



    # return jsonify({"reply": bot_reply})



@app.route('/end-chat', methods=['POST'])
def end_chat():
    data = request.json
    user_info = data.get('user_info', {})
    start_time = data.get('start_time')
    chat_history = data.get('chat_history', [])
    # user_info = session.get('user_info', {})
    # start_time = session.get('start_time')
    end_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    # chat_history = session.get('chat_history', [])

    # 진행 시간 계산 (분 단위)
    start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_dt = datetime.now(KST)
    duration = (end_dt - start_dt).seconds // 60

    # 상태 결정: 대화 시간이 10분 이상이면 complete, 그렇지 않으면 incomplete
    status = 'complete' if duration >= 10 else 'incomplete'

    # 데이터베이스에 저장
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute(
        '''INSERT INTO users (name, dob, gender, start_time, end_time, chat_history, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (user_info.get('name'),
         user_info.get('dob'), user_info.get('gender'), start_time, end_time,
         str(chat_history) if status == 'complete' else None, status))
    conn.commit()
    conn.close()

    # session.clear()

    # 중간 종료 시와 정상 종료 시 다른 메시지 반환
    message = "Bye~! Let's talk again next time!!" if status == 'complete' else "I ended the conversation in the middle. Let's talk again next time!"
    return jsonify({"message": message})


@app.route('/complete-session', methods=['POST'])
def complete_session():
    # user_info = session.get('user_info', {})
    # start_time = session.get('start_time')
    data = request.json
    user_info = data.get('user_info', {})
    start_time = data.get('start_time')

    if not user_info or not start_time:
        return jsonify({"error": "세션 정보가 없습니다."}), 400

    # 완료 시간 기록
    end_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

    # 완료 상태 업데이트
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute(
        'UPDATE users SET status = ?, end_time = ? WHERE name = ? AND start_time = ?',
        ('complete', end_time, user_info['name'], start_time))
    conn.commit()
    conn.close()

    return jsonify({"message": "대화 완료 상태가 저장되었습니다."})


@app.route('/view-data', methods=['GET'])
def view_data():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute(
        "SELECT name, dob, gender, start_time, end_time, chat_history, status FROM users"
    )
    users_data = c.fetchall()
    conn.close()

    html_content = """
    <html>
    <head>
        <title>Chat Data</title>
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            td { word-wrap: break-word; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>저장된 사용자 및 채팅 데이터</h1>
        <table>
            <tr>
                <th>이름</th>
                <th>생년월일</th>
                <th>성별</th>
                <th>시작 시간</th>
                <th>종료 시간</th>
                <th>채팅 내용</th>
                <th>상태</th>
            </tr>
    """

    for user in users_data:
        name, dob, gender, start_time, end_time, chat_history, status = user
        html_content += f"""
            <tr>
                <td>{name}</td>
                <td>{dob}</td>
                <td>{gender}</td>
                <td>{start_time}</td>
                <td>{end_time or ''}</td>
                <td>{chat_history}</td>
                <td>{status}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    return html_content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

