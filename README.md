# <a href="https://t.me/LesstRobot">Lesst</a> — less than Email client

## Описание проекта
Полноценный почтовый клиент в Telegram. На базе Telegram BotAPI и <a href="https://telegram.org/blog/ultimate-privacy-topics-2-0/ru#temi-2-0">Форумов</a> (реализации "тем" / "тредов" в Telegram).

<img width="600" alt="image" src="https://github.com/innerbots/lesst/assets/62261985/0a53cf29-a748-4710-bf64-a78f0abcb1ab">

## Функциональность | Особенности бота
- Пользователь может подключить до пяти почтовых ящиков (Yandex, Gmail, MailRu). К каждому ящику создается форум для получения и отправки Email-ов.
<img width="300" alt="Снимок экрана 2023-07-09 в 03 05 36" src="https://github.com/innerbots/lesst/assets/62261985/18324140-5607-424b-971e-da4fe81c3781">

- Все вложения к письмам присылаются в качестве файлов прямо в Telegram.
  
  <img width="263" alt="image" src="https://github.com/innerbots/lesst/assets/62261985/09720367-67a7-4701-a23b-f71427e27f93">

- Все входящие письма сортируются по Email-адресам. Таким образом, пользователь получает все письма (включая спам), но может отключать уведомления / блокировать письма от конкретного Email-адреса. Благодаря этому, важное письмо не затеряется в "Спаме" и не будет обработано почтовым автофильтром.

  <img width="292" alt="Снимок экрана 2023-07-09 в 04 11 11" src="https://github.com/innerbots/lesst/assets/62261985/5d0f8851-3595-44b9-876a-a01d0e09a415">

- Сразу после подключения ящика, бот подгружает последние 50 писем и сортирует их. Таким образом, пользователь может искать контент по последним письмам сразу после начала работы с ботом. Это аналог полноценного импорта в других почтовых клиентах.
- После настройки и первичного анализа почты, каждый входящий Email будет приходить в чат моментально. Пользователю приходит стандартное уведомление в Telegram.
  
  <img width="330" alt="Снимок экрана 2023-07-09 в 03 35 14" src="https://github.com/innerbots/lesst/assets/62261985/9b244a3f-93ac-4553-9a1c-f0c6129fd8ae">


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
