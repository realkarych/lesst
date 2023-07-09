# <a href="https://t.me/LesstRobot">Lesst</a> — less than Email client
<img width="300" alt="Снимок экрана 2023-07-09 в 03 05 36" src="https://github.com/innerbots/lesst/assets/62261985/c7c86bf3-6b04-420d-a042-a3dfd6628466">

## Описание проекта
Полноценный почтовый клиент в Telegram. На базе Telegram BotAPI и <a href="https://telegram.org/blog/ultimate-privacy-topics-2-0/ru#temi-2-0">Форумов</a> (реализации "тем" / "тредов" в Telegram).

<img width="214" alt="Снимок экрана 2023-07-09 в 03 05 36" src="https://github.com/innerbots/lesst/assets/62261985/f1ef7453-e90c-4eca-b73b-49cde39effe1">

## Функциональность | Особенности бота
- Пользователь может подключить до пяти почтовых ящиков (Yandex, Gmail, MailRu). К каждому ящику создается форум для получения и отправки Email-ов.

  <img width="400" alt="Снимок экрана 2023-07-09 в 03 05 36" src="https://github.com/innerbots/lesst/assets/62261985/e29fe07b-1c8f-49cf-b8ed-ca03df340ea7">

- Все входящие письма сортируются по Email-адресам. Таким образом, пользователь получает все письма (включая спам), но может отключать уведомления / блокировать письма от конкретного Email-адреса. Благодаря этому, важное письмо не затеряется в "Спаме" и не будет обработано почтовым автофильтром.

  <img width="214" alt="Снимок экрана 2023-07-09 в 03 05 36" src="https://github.com/innerbots/lesst/assets/62261985/f1ef7453-e90c-4eca-b73b-49cde39effe1">
  
- Сразу после подключения ящика, бот подгружает последние 50 писем и сортирует их. Таким образом, пользователь может искать контент по последним письмам сразу после начала работы с ботом. Это аналог полноценного импорта в других почтовых клиентах.
- После настройки и первичного анализа почты, каждый входящий Email будет приходить в чат моментально. Пользователю приходит стандартное уведомление в Telegram.
  
  <img width="330" alt="Снимок экрана 2023-07-09 в 03 35 14" src="https://github.com/innerbots/lesst/assets/62261985/72feec68-fc90-4033-8966-0687a716b45d">

## Технический Стек
- Python3.11
- Poetry — менеджер зависимостей.
- <a href="https://github.com/aiogram/aiogram">Aiogram</a> — асинхронный фреймворк для работы с Telegram BotAPI.
- <a href="https://projectfluent.org/">Mozilla ProjectFluent</a> — система локализации. Бот работает на английском и русском языках.
- PostgreSQL (реляционная бд) + SQLalchemy (ORM) + asyncpg (коннектор) + alembic (миграции)
- Набор инструментов для асинхронной подгрузки Email-ов по IMAP и отправки по SMTP.
- Для шифрования при хранении пользовательских данных используются KDF, message digests, symmetric ciphers. Библиотека: https://pypi.org/project/cryptography/.
- APScheduler — аналог crontab — управление регулярными процессами.
- Systemd — запуск приложения на сервере. Можно заменить Docker-ом.
- Полный перечень использованных инструментов можно посмотреть в <a href="https://github.com/innerbots/lesst/blob/main/pyproject.toml">зависимостях проекта</a>.
