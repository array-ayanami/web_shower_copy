// scripts.js
document.addEventListener("DOMContentLoaded", function() {
    updateProfileButton();

    // === ОБНОВЛЕНИЕ КНОПКИ ПРОФИЛЯ ===
    function updateProfileButton() {
        const profileBtn = document.getElementById('profileBtn');
        if (!profileBtn) return;
        
        const user = JSON.parse(localStorage.getItem('currentUser'));
        if (user) {
            profileBtn.textContent = user.name;
        } else {
            profileBtn.textContent = 'Иванов Иван';
        }
    } 

    // === ПОКАЗ ПРОФИЛЯ ===
    window.showProfile = function() {
        const user = JSON.parse(localStorage.getItem('currentUser'));
        if (!user) {
            window.location.href = 'register.html';
        } else {
            alert('Имя: ' + user.name + '\nEmail: ' + user.email);
        }
    };

    // === ВЫХОД ИЗ СИСТЕМЫ ===
    window.logout = function() {
        localStorage.removeItem('currentUser');
        updateProfileButton();
        alert('Вы вышли из системы.');
    };

    // === ВАЛИДАЦИЯ ФОРМЫ РЕГИСТРАЦИИ ===
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');

        // Функция показа ошибки
        function showError(input, message) {
            input.style.borderColor = '#e74c3c';
            input.style.boxShadow = '0 0 5px rgba(231, 76, 60, 0.3)';

            const existingError = input.parentNode.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }

            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = '#e74c3c';
            errorDiv.style.fontSize = '12px';
            errorDiv.style.marginTop = '5px';
            errorDiv.textContent = message;
            input.parentNode.appendChild(errorDiv);
        }

        // Функция очистки ошибок
        function clearErrors() {
            document.querySelectorAll('.error-message').forEach(function(el) {
                el.remove();
            });
            document.querySelectorAll('input').forEach(function(input) {
                input.style.borderColor = '';
                input.style.boxShadow = '';
            });
        }

        // Очистка ошибки при вводе
        [nameInput, emailInput, passwordInput].forEach(function(input) {
            input.addEventListener('input', function() {
                this.style.borderColor = '';
                this.style.boxShadow = '';
                const existingError = this.parentNode.querySelector('.error-message');
                if (existingError) {
                    existingError.remove();
                }
            });
        });

        // Обработчик отправки формы
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            clearErrors();

            const name = nameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            let isValid = true;

            // Проверка имени
            if (name.length < 2) {
                showError(nameInput, 'Имя должно быть не менее 2 символов');
                isValid = false;
            } else if (name.length > 32) {
                showError(nameInput, 'Имя не должно превышать 32 символа');
                isValid = false;
            } else if (!/^[А-ЯЁ][а-яё]*$/.test(name)) {
                showError(nameInput, 'Имя с заглавной буквы, только русские буквы');
                isValid = false;
            }

            // Проверка email
            if (!email) {
                showError(emailInput, 'Введите email');
                isValid = false;
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                showError(emailInput, 'Введите корректный email');
                isValid = false;
            } else if (/[а-яё]/i.test(email)) {
                showError(emailInput, 'Email только на латинице');
                isValid = false;
            } else {
                // Проверка через API (включая проверку на одноразовые почты)
                const validation = await validateEmail(email);
                if (!validation.valid) {
                    showError(emailInput, validation.reason);
                    isValid = false;
                }
            }

            // Проверка пароля
            if (password.length < 6) {
                showError(passwordInput, 'Пароль должен быть не менее 6 символов');
                isValid = false;
            } else if (password.length > 32) {
                showError(passwordInput, 'Пароль не должен превышать 32 символа');
                isValid = false;
            }

            if (!isValid) {
                return;
            } 

            // Проверка на дубликат
            let users = JSON.parse(localStorage.getItem('users')) || [];
            const userExists = users.some(function(user) {
                return user.email === email;
            });

            if (userExists) {
                showError(emailInput, 'Этот email уже зарегистрирован');
                return;
            }

            // Успешная регистрация
            const newUser = {
                name: name,
                email: email,
                password: password
            };
            users.push(newUser);
            localStorage.setItem('users', JSON.stringify(users));
            localStorage.setItem('currentUser', JSON.stringify(newUser));

            alert('Регистрация прошла успешно!');
            window.location.href = 'booking.html';
        });
    }

    // === ФОРМА БРОНИРОВАНИЯ ===
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        const user = JSON.parse(localStorage.getItem('currentUser'));
        const authMessage = document.getElementById('authMessage');

        if (user) {
            bookingForm.style.display = 'block';
        } else {
            if (authMessage) {
                authMessage.textContent = 'Для бронирования необходимо зарегистрироваться.';
            }
        }

        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const dateInput = document.querySelector('input[type="date"]');
            const timeInput = document.querySelector('input[type="time"]');
            
            if (!dateInput || !timeInput) {
                alert('Заполните дату и время');
                return;
            }

            const date = dateInput.value;
            const time = timeInput.value;

            if (!date || !time) {
                alert('Заполните дату и время');
                return;
            }

            const bookings = JSON.parse(localStorage.getItem('bookings')) || [];
            bookings.push({ date: date, time: time, user: user ? user.name : 'Гость' });
            localStorage.setItem('bookings', JSON.stringify(bookings));

            alert('Бронирование успешно выполнено!');
            window.location.href = 'mybookings.html';
        });
    }

    // === ФОРМА ОБРАТНОЙ СВЯЗИ + TELEGRAM ===
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = document.getElementById('feedbackName').value.trim();
            const email = document.getElementById('feedbackEmail').value.trim();
            const subject = document.getElementById('feedbackSubject').value;
            const message = document.getElementById('feedbackMessage').value.trim();
            const statusDiv = document.getElementById('feedbackStatus');

            if (!name || !email || !subject || !message) {
                if (statusDiv) {
                    statusDiv.innerHTML = '<p style="color: #e74c3c;">Заполните все поля</p>';
                }
                return;
            }

            // Здесь можно добавить валидацию email для формы обратной связи тоже
            // const validation = await validateEmail(email);
            // if (!validation.valid) { ... }

            const subjectText = {
                'booking': 'Бронирование',
                'technical': 'Техническая проблема',
                'suggestion': 'Предложение',
                'other': 'Другое'
            }[subject] || subject;

            // Отправка в Telegram (только для обратной связи)
            if (typeof sendToTelegram === 'function') {
                const telegramMessage = '💬 <b>Новое сообщение обратной связи</b>\n' +
                    '👤 Имя: ' + name + '\n' +
                    '📧 Email: ' + email + '\n' +
                    '📌 Тема: ' + subjectText + '\n' +
                    '💭 Сообщение:\n' + message + '\n' +
                    '🕐 Время: ' + new Date().toLocaleString('ru-RU');

                try {
                    const success = await sendToTelegram(telegramMessage);
                    if (statusDiv) {
                        if (success) {
                            statusDiv.innerHTML = '<p style="color: #27ae60;">Сообщение отправлено!</p>';
                            feedbackForm.reset();
                        } else {
                            statusDiv.innerHTML = '<p style="color: #e74c3c;">Ошибка отправки. Попробуйте позже.</p>';
                        }
                    }
                } catch (err) {
                    if (statusDiv) {
                        statusDiv.innerHTML = '<p style="color: #e74c3c;">Ошибка отправки. Попробуйте позже.</p>';
                    }
                }
            } else {
                if (statusDiv) {
                    statusDiv.innerHTML = '<p style="color: #27ae60;">Сообщение сохранено локально!</p>';
                }
                feedbackForm.reset();
            }
        });
    }

    // === СПИСОК БРОНИРОВАНИЙ ===
    const bookingsList = document.getElementById('bookingsList');
    if (bookingsList) {
        const bookings = JSON.parse(localStorage.getItem('bookings')) || [];

        if (bookings.length === 0) {
            bookingsList.innerHTML = '<li>У вас пока нет бронирований.</li>';
        } else {
            bookings.forEach(function(booking, index) {
                const li = document.createElement('li');
                li.innerHTML = '<p>Дата: ' + booking.date + ', Время: ' + booking.time + '</p>' +
                    '<button onclick="cancelBooking(' + index + ')">Отменить</button>';
                bookingsList.appendChild(li);
            });
        }
    }

    // === ВЫПАДАЮЩЕЕ МЕНЮ ===
    const dropdown = document.querySelector('.dropdown');
    const dropdownContent = document.getElementById('dropdownMenu');

    if (dropdown && dropdownContent) {
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownContent.classList.toggle('show');
        });

        document.addEventListener('click', function() {
            dropdownContent.classList.remove('show');
        });
    }
});

// === ОТМЕНА БРОНИРОВАНИЯ (глобальная функция) ===
function cancelBooking(index) {
    let bookings = JSON.parse(localStorage.getItem('bookings')) || [];
    if (confirm('Вы уверены, что хотите отменить бронь?')) {
        bookings.splice(index, 1);
        localStorage.setItem('bookings', JSON.stringify(bookings));
        location.reload();
    }
}