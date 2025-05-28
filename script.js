// HTML 요소 가져오기
const userInfoForm = document.getElementById('user-info-form');
const userInfoContainer = document.getElementById('user-info-container');
const chatContainer = document.getElementById('chat-container');
const chatOutput = document.getElementById('chat-output');
const textInputForm = document.getElementById('text-input-form');
const textInput = document.getElementById('text-input');

let timer;

// 채팅 화면을 아래로 스크롤하는 함수
function scrollToBottom() {
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

// 새로운 사용자 인식 위한 새로고침 처리
window.onload = async () => {
    await fetch('/reset-session', { method: 'POST' }); // 새 세션 요청
    userInfoContainer.style.display = 'block';
    chatContainer.style.display = 'none';
};

// 사용자 정보 폼 제출 처리
userInfoForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userInfo = {
        name: document.getElementById('name').value,
        dob: document.getElementById('dob').value,
        gender: document.getElementById('gender').value
    };

    try {
        await fetch('/user-info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userInfo)
        });
    } catch (err) {
        console.error('사용자 정보 저장 중 오류:', err);
        return;
    }

    userInfoContainer.style.display = 'none';
    chatContainer.style.display = 'block';
    document.getElementById('chat-header').style.display = 'flex'; // 헤더 보이기
    
    // ✅ 유미의 머릿속 부분을 챗봇 대화창 안에서 표시
    const thoughtContainer = document.createElement('div');
    thoughtContainer.className = 'chat-thought'; // 새로운 스타일 적용
    thoughtContainer.innerHTML = `
        <p class="thought-title">🧠Your Inner Thoughts🧠</p>
        <p class="thought-text">Tell me about the recent worries or difficult moments you've experienced.</p>

    `;

    chatOutput.appendChild(thoughtContainer); // 대화창 내부에 추가
    scrollToBottom();

    // ✅ 챗봇과 사용자 대화 추가 (일반 채팅 메시지)
    setTimeout(() => {
        addBotMessage(`Hi, I'm Roro. I'm always here and ready to listen to whatever you're going through, ${userInfo.name}.`);

        setTimeout(() => {
            addUserMessage(`I've been feeling overwhelmed lately...
Should I talk about what I just wrote?`);

            setTimeout(() => {
                addBotMessage(`Yes, exactly! Let’s talk more about what you just shared.
You can also tell me about any other worries or concerns on your mind. Whatever it is, I’m here to listen.`);
                scrollToBottom();
            }, 800);

        }, 800);

    }, 800);
    scrollToBottom(); // 화면 하단으로 스크롤
    startTimers();

    });

// 채팅 폼 제출 처리
textInputForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    sendMessage();
});

// 엔터 키 입력 감지
textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Shift + Enter는 줄바꿈, Enter는 전송
        e.preventDefault(); // 기본 Enter 동작 방지
        sendMessage(); // 메시지 전송
    }
});

// 메시지 전송 함수
function sendMessage() {
    const userInput = textInput.value.trim();
    if (!userInput) return;

    addUserMessage(userInput);
    textInput.value = ''; // 입력창 초기화
    scrollToBottom();

    // 서버로 메시지 전송
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        addBotMessage(data.reply);
        scrollToBottom();
    })
    .catch(err => {
        console.error('채팅 중 오류:', err);
    });
}

// 사용자 메시지를 채팅에 추가
function addUserMessage(message) {
    const userMessage = document.createElement('div');
    userMessage.className = 'user-message';
    userMessage.textContent = message;
    chatOutput.appendChild(userMessage);
}

// 봇 메시지를 채팅에 추가 (프로필 사진 포함)
function addBotMessage(message) {
    const botMessageContainer = document.createElement('div');
    botMessageContainer.className = 'bot-message-container';

    const botProfilePic = document.createElement('img');
    botProfilePic.src = 'gpt_profile.png';
    botProfilePic.alt = '사랑세포';
    botProfilePic.className = 'profile-pic';

    const botMessage = document.createElement('div');
    botMessage.className = 'bot-message';
    const cleaned = message.replace(/\n{2,}/g, '\n\n'); // 줄바꿈 2개 이상은 2개로 제한
    botMessage.innerHTML = marked.parse(message);

    botMessageContainer.appendChild(botProfilePic);
    botMessageContainer.appendChild(botMessage);
    chatOutput.appendChild(botMessageContainer);
    scrollToBottom();
}

// 채팅 화면을 아래로 스크롤하는 함수
function scrollToBottom() {
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

let startTime, endTime, timer5Min, timer15Min;

function startTimers() {
    startTime = new Date();

    // 5분 타이머: 완료하기 버튼 표시
    timer5Min = setTimeout(() => {
        const finishButton = document.createElement('button');
        finishButton.textContent = 'Finsh conversation';
        finishButton.className = 'finish-button'; // 완료하기 버튼에 클래스 적용
        finishButton.style.marginTop = '10px';

        // 완료 버튼 클릭 시 동작 정의
        finishButton.onclick = async () => {
            try {
                // 데이터베이스에 완료 상태 저장
                await fetch('/complete-session', { method: 'POST' });

                // 다음 페이지로 전환
                chatContainer.style.display = 'none';
                document.getElementById('final-page').style.display = 'block';
            } catch (err) {
                console.error('완료 상태 저장 중 오류:', err);
            }
        };

        chatContainer.appendChild(finishButton);
    }, 5 * 60 * 1000);

    // 5.5분 타이머: 자동 종료 처리
    timer15Min = setTimeout(() => {
        addBotMessage('Our time for today has come to an end. Thank you for sharing your thoughts with me — it’s a bit sad, but let’s continue our conversation next time!');
        textInputForm.style.display = 'none';

        // 완료하기 버튼만 남기기
        const finishButton = document.querySelector('.finish-button');
        if (finishButton) finishButton.style.display = 'block';

        // 10초 후 자동 이동
        setTimeout(async () => {
            try {
                // 자동 완료 상태를 서버에 저장
                await fetch('/complete-session', { method: 'POST' });

                // 마지막 페이지로 전환
                chatContainer.style.display = 'none';
                document.getElementById('final-page').style.display = 'block';
            } catch (err) {
                console.error('자동 완료 처리 중 오류:', err);
            }
        }, 5000); // 5초 대기
    }, 5.5 * 60 * 1000);
}



// 채팅 세션 종료 및 서버에 알림
async function endChatSession() {
    try {
        const response = await fetch('/end-chat', { method: 'POST' });
        const data = await response.json();
        addBotMessage(data.message);
        textInputForm.style.display = 'none';
    } catch (err) {
        console.error('채팅 종료 중 오류:', err);
    }
}

// 실시간 데이터 미리보기
async function fetchData() {
    try {
        const response = await fetch('/view-data');
        const data = await response.text();
        // console.log('Fetched Data:', data); // 데이터를 콘솔에 출력
    } catch (err) {
        console.error('데이터 가져오기 오류:', err);
    }
}



// 5초마다 데이터 갱신
setInterval(fetchData, 10000);
