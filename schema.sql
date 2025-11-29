CREATE DATABASE IF NOT EXISTS inkflow_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE inkflow_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,      -- Унікальний номер паспорта
    username VARCHAR(50) NOT NULL UNIQUE,   -- Логін (має бути унікальним)
    email VARCHAR(100) NOT NULL UNIQUE,     -- Пошта
    password_hash VARCHAR(255) NOT NULL,    -- Пароль (зашифрований, ми не бачимо "12345")
    avatar_url VARCHAR(255) DEFAULT NULL,   -- Посилання на картинку аватарки
    bio TEXT,                               -- Опис профілю ("Люблю каву і детективи")

    role ENUM('user', 'admin') DEFAULT 'user', -- Хто це? Адмін чи простий смертний?

    -- Фінанси та Гейміфікація
    balance INT DEFAULT 0,                  -- Гаманець (скільки монет на рахунку)
    streak_count INT DEFAULT 0,             -- Скільки днів підряд заходив
    last_login_date DATE DEFAULT NULL,      -- Дата останнього входу (щоб рахувати дні)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Коли зареєструвався
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,            -- Назва книги
    author VARCHAR(100) NOT NULL,           -- Автор
    description TEXT,                       -- Анотація (про що книга)
    cover_image VARCHAR(255),               -- Назва файлу обкладинки (напр. "dune.jpg")

    -- Файлова частина
    file_path VARCHAR(255),                 -- Назва файлу для скачування (напр. "dune.pdf")
    price_coins INT DEFAULT 0,              -- Ціна скачування (0 = безкоштовно)

    views_count INT DEFAULT 0,              -- Лічильник переглядів (для "Топ книг")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,                   -- До якої книги належить цей розділ?
    title VARCHAR(255) NOT NULL,            -- Назва розділу (напр. "Розділ 1. Початок")
    content LONGTEXT NOT NULL,              -- САМ ТЕКСТ КНИГИ (тут багато літер)
    order_number INT NOT NULL,              -- Номер по порядку (щоб розділи не переплутались)

    -- Зв'язок: Якщо видалити книгу, зникнуть і її розділи (CASCADE)
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE library_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,

    -- ТВОЇ СТАТУСИ (Полиці):
    status ENUM('planned', 'reading', 'completed', 'dropped') DEFAULT 'planned',
    -- 'planned' = Прочитати пізніше
    -- 'reading' = Читаю зараз
    -- 'completed' = Прочитано
    -- 'dropped' = Кинув читати

    is_favorite BOOLEAN DEFAULT FALSE,      -- Чи натиснув "Сердечко"? (Так/Ні)

    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,

    -- Захист від дублікатів: Не можна додати одну книгу двічі в список
    UNIQUE KEY unique_library_entry (user_id, book_id)
);

CREATE TABLE reading_progress (
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    chapter_id INT NOT NULL,                -- На якому розділі?
    scroll_position INT DEFAULT 0,          -- На якому пікселі (висота прокрутки)?
    last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, book_id),         -- Один запис на одну книгу для юзера
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

CREATE TABLE purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,                  -- Хто платив гроші (з кого списали)
    receiver_id INT NOT NULL,               -- Кому дісталася книга (для подарунків)
    book_id INT NOT NULL,                   -- Яку книгу купили
    price_paid INT NOT NULL,                -- Скільки заплатили (історія цін важлива)

    is_gift BOOLEAN DEFAULT FALSE,          -- Це подарунок?
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    selected_text TEXT NOT NULL,            -- Текст, який юзер виділив
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);