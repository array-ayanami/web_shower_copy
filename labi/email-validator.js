// email-validator.js
// API для проверки email через htmlweb.ru
const EMAIL_API_URL = 'https://htmlweb.ru/json/service/email';
const API_KEY = '63980470ca365312c7dc6322ea6059b4'; // ← Вставьте сюда ваш API-ключ из профиля htmlweb.ru

/**
 * Проверка email через htmlweb.ru API
 * @param {string} email - email для проверки
 * @returns {Promise} результат проверки
 */
async function validateEmail(email) {
    if (!email) {
        return { valid: false, reason: 'Email не указан' };
    }
    
    try {
        // Формируем URL запроса
        const url = `${EMAIL_API_URL}?email=${encodeURIComponent(email)}&api_key=${API_KEY}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // === ПРОВЕРКА НА ОДНОРАЗОВЫЕ ПОЧТЫ ===
        // Поле disposable = true означает одноразовый email
        if (result.disposable === true) {
            return { valid: false, reason: 'Одноразовые email запрещены' };
        }

        // === ДРУГИЕ ПРОВЕРКИ ===
        
        // Неверный формат email
        if (result.format_valid === false) {
            return { valid: false, reason: result.error || 'Некорректный формат email' };
        }

        // MX-запись не найдена (домен не принимает почту)
        if (result.mx_found === false) {
            return { valid: false, reason: 'Почтовый сервер домена не найден' };
        }

        // Если всё хорошо
        if (result.message === 'email валидный' || result.message === 'Email одноразовый') {
            // message === 'Email одноразовый' уже обработан выше, но на всякий случай
            if (result.message === 'Email одноразовый') {
                return { valid: false, reason: 'Одноразовые email запрещены' };
            }
            return { valid: true };
        }

        // Если API вернул ошибку
        if (result.error) {
            return { valid: false, reason: result.error };
        }

        // По умолчанию считаем валидным (fail-open при неясном ответе)
        return { valid: true };

    } catch (error) {
        console.error('Ошибка проверки email через htmlweb:', error);
        // При ошибке API разрешаем регистрацию, чтобы не блокировать пользователей
        return { valid: true };
    }
}