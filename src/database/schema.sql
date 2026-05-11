-- =============================================================================
-- Library System — Database Schema
-- База даних у 3-й нормальній формі (3NF)
-- =============================================================================

-- Видалення таблиць у зворотному порядку залежностей
DROP TABLE IF EXISTS borrow_records;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS users;

-- =============================================================================
-- Таблиця: users (Користувачі)
-- =============================================================================
CREATE TABLE users (
    id              SERIAL          PRIMARY KEY,
    first_name      VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NOT NULL,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    phone           VARCHAR(20),
    role            VARCHAR(20)     NOT NULL DEFAULT 'reader'
                                    CHECK (role IN ('reader', 'librarian', 'admin')),
    password_hash   VARCHAR(255)    NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Індекси для частих запитів
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_last_name ON users(last_name);

COMMENT ON TABLE users IS 'Користувачі бібліотечної системи (читачі, бібліотекарі, адміністратори)';

-- =============================================================================
-- Таблиця: authors (Автори)
-- =============================================================================
CREATE TABLE authors (
    id              SERIAL          PRIMARY KEY,
    first_name      VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NOT NULL,
    birth_year      INTEGER,
    country         VARCHAR(100),
    biography       TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_authors_last_name ON authors(last_name);
CREATE INDEX idx_authors_country ON authors(country);

COMMENT ON TABLE authors IS 'Автори книг';

-- =============================================================================
-- Таблиця: books (Книги)
-- FK: author_id -> authors(id)
-- =============================================================================
CREATE TABLE books (
    id                  SERIAL          PRIMARY KEY,
    title               VARCHAR(500)    NOT NULL,
    isbn                VARCHAR(13)     NOT NULL UNIQUE,
    publication_year    INTEGER,
    genre               VARCHAR(100),
    quantity            INTEGER         NOT NULL DEFAULT 1 CHECK (quantity >= 0),
    available_quantity  INTEGER         NOT NULL DEFAULT 1 CHECK (available_quantity >= 0),
    author_id           INTEGER         NOT NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Зовнішній ключ
    CONSTRAINT fk_books_author
        FOREIGN KEY (author_id) REFERENCES authors(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Кількість доступних не може перевищувати загальну
    CONSTRAINT chk_available_lte_quantity
        CHECK (available_quantity <= quantity)
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_author_id ON books(author_id);
CREATE INDEX idx_books_genre ON books(genre);

COMMENT ON TABLE books IS 'Каталог книг бібліотеки';

-- =============================================================================
-- Таблиця: borrow_records (Записи про видачу книг)
-- FK: user_id -> users(id), book_id -> books(id)
-- =============================================================================
CREATE TABLE borrow_records (
    id              SERIAL          PRIMARY KEY,
    user_id         INTEGER         NOT NULL,
    book_id         INTEGER         NOT NULL,
    borrow_date     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date        DATE            NOT NULL,
    return_date     TIMESTAMP,
    penalty_amount  DECIMAL(10, 2)  NOT NULL DEFAULT 0.00 CHECK (penalty_amount >= 0),
    status          VARCHAR(20)     NOT NULL DEFAULT 'active'
                                    CHECK (status IN ('active', 'returned', 'overdue')),
    notes           TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Зовнішні ключі
    CONSTRAINT fk_borrow_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_borrow_book
        FOREIGN KEY (book_id) REFERENCES books(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_borrow_user_id ON borrow_records(user_id);
CREATE INDEX idx_borrow_book_id ON borrow_records(book_id);
CREATE INDEX idx_borrow_status ON borrow_records(status);
CREATE INDEX idx_borrow_due_date ON borrow_records(due_date);

COMMENT ON TABLE borrow_records IS 'Записи про видачу та повернення книг';

-- =============================================================================
-- Тригер: Автоматичне оновлення updated_at
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_authors_updated_at
    BEFORE UPDATE ON authors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_books_updated_at
    BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_borrow_records_updated_at
    BEFORE UPDATE ON borrow_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
