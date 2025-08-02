CREATE DATABASE remont_db;

\c remont_db;

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role TEXT NOT NULL UNIQUE
);

CREATE TABLE status (
    status_id SERIAL PRIMARY KEY,
    status TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(role_id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    passw TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE engineer_profile (
    engin_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    balance DECIMAL(10,2) DEFAULT 0.00,
    schedule TEXT,
    CONSTRAINT fk_engineer_profile_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE request (
    request_id SERIAL PRIMARY KEY,
    operator_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    engineer_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    status_id INTEGER NOT NULL REFERENCES status(status_id) ON DELETE RESTRICT,
    phone TEXT NOT NULL,
    adress TEXT NOT NULL,
    techniq TEXT NOT NULL,
    description TEXT,
    customer_name TEXT NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_time TIMESTAMP,
    in_works_time TIMESTAMP,
    done_time TIMESTAMP,
    CONSTRAINT fk_request_operator FOREIGN KEY (operator_id) REFERENCES users(user_id),
    CONSTRAINT fk_request_engineer FOREIGN KEY (engineer_id) REFERENCES users(user_id),
    CONSTRAINT fk_request_status FOREIGN KEY (status_id) REFERENCES status(status_id)
);

CREATE TABLE balance_history (
    bh_id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    engineer_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    old_sum DECIMAL(10,2) NOT NULL,
    new_sum DECIMAL(10,2) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_balance_history_admin FOREIGN KEY (admin_id) REFERENCES users(user_id),
    CONSTRAINT fk_balance_history_engineer FOREIGN KEY (engineer_id) REFERENCES users(user_id)
);

CREATE TABLE request_history (
    request_id INTEGER NOT NULL REFERENCES request(request_id) ON DELETE CASCADE,
    changer_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_request_history_request FOREIGN KEY (request_id) REFERENCES request(request_id),
    CONSTRAINT fk_request_history_changer FOREIGN KEY (changer_id) REFERENCES users(user_id)
);

CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_engineer_profile_user_id ON engineer_profile(user_id);
CREATE INDEX idx_request_engineer_id ON request(engineer_id);
CREATE INDEX idx_request_status_id ON request(status_id);
CREATE INDEX idx_request_creation_date ON request(creation_date);
CREATE INDEX idx_request_assigned_time ON request(assigned_time);
CREATE INDEX idx_balance_history_engineer_id ON balance_history(engineer_id);
CREATE INDEX idx_balance_history_changed_at ON balance_history(changed_at);
CREATE INDEX idx_request_history_request_id ON request_history(request_id);
CREATE INDEX idx_request_history_changed_at ON request_history(changed_at);

INSERT INTO roles (role_id, role) VALUES 
(1, 'engineer'),
(2, 'operator'),
(3, 'manager');

INSERT INTO status (status_id, status) VALUES 
(1, 'Создана'),
(2, 'Назначена'),
(3, 'В работе'),
(4, 'Выполнена');

CREATE VIEW request_details AS
SELECT 
    r.request_id,
    r.operator_id,
    op.name AS operator_name,
    r.engineer_id,
    eng.name AS engineer_name,
    r.status_id,
    s.status AS status_name,
    r.phone,
    r.customer_name,
    r.adress AS address,
    r.techniq AS equipment,
    r.description,
    r.creation_date,
    r.assigned_time,
    r.in_works_time,
    r.done_time
FROM request r
LEFT JOIN users op ON r.operator_id = op.user_id
LEFT JOIN users eng ON r.engineer_id = eng.user_id
LEFT JOIN status s ON r.status_id = s.status_id;

CREATE VIEW engineer_details AS
SELECT 
    u.user_id,
    u.name,
    u.phone,
    u.email,
    ep.balance,
    ep.schedule,
    r.role
FROM users u
JOIN roles r ON u.role_id = r.role_id
LEFT JOIN engineer_profile ep ON u.user_id = ep.user_id
WHERE r.role = 'engineer'; 