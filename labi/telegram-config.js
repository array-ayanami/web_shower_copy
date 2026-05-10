const TELEGRAM_CONFIG = {
    botToken: '8698285693:AAGLcK8piwUhL0rAf16wr4xuhLciaPqmLqo',
    chatId: '350638036'
};

async function sendToTelegram(message) {
    const url = 'https://api.telegram.org/bot' + TELEGRAM_CONFIG.botToken + '/sendMessage';
    
    const data = {
        chat_id: TELEGRAM_CONFIG.chatId,
        text: message,
        parse_mode: 'HTML'
    };

    try {
        console.log('Отправка в Telegram:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log('Ответ Telegram:', result);
        
        if (result.ok) {
            console.log('Telegram: сообщение отправлено');
            return true;
        } else {
            console.error('Telegram ошибка:', result.description);
            return false;
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        return false;
    }
}