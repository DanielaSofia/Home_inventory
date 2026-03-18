-- Criar base de dados
CREATE DATABASE IF NOT EXISTS casa
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE casa;

--------------------------------------------------
-- Tabela Divisão
--------------------------------------------------

CREATE TABLE inventory_divisao (

    id INT AUTO_INCREMENT PRIMARY KEY,

    nome VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

--------------------------------------------------
-- Tabela Itens
--------------------------------------------------

CREATE TABLE inventory_item (

    id INT AUTO_INCREMENT PRIMARY KEY,

    nome VARCHAR(200) NOT NULL,

    descricao TEXT,

    quantidade INT DEFAULT 1,

    valor_estimado DECIMAL(10,2),

    data_aquisicao DATE,

    imagem VARCHAR(255),

    divisao_id INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_item_divisao (divisao_id),

    CONSTRAINT fk_item_divisao
    FOREIGN KEY (divisao_id)
    REFERENCES divisao(id)
    ON DELETE SET NULL

);

--------------------------------------------------
-- Tabela Desejos
--------------------------------------------------

CREATE TABLE inventory_desejo (

    id INT AUTO_INCREMENT PRIMARY KEY,

    nome VARCHAR(200) NOT NULL,

    descricao TEXT,

    valor_estimado DECIMAL(10,2),

    imagem VARCHAR(255),

    divisao_id INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_desejo_divisao (divisao_id),

    CONSTRAINT fk_desejo_divisao
    FOREIGN KEY (divisao_id)
    REFERENCES divisao(id)
    ON DELETE SET NULL

);

--------------------------------------------------
-- Lista de Compras
--------------------------------------------------

CREATE TABLE inventory_compra (

    id INT AUTO_INCREMENT PRIMARY KEY,

    nome VARCHAR(200) NOT NULL,

    quantidade INT DEFAULT 1,

    comprado BOOLEAN DEFAULT FALSE,

    divisao_id INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_compra_divisao (divisao_id),

    CONSTRAINT fk_compra_divisao
    FOREIGN KEY (divisao_id)
    REFERENCES divisao(id)
    ON DELETE SET NULL

);

--------------------------------------------------
-- Inserir divisões padrão
--------------------------------------------------

INSERT INTO inventory_divisao (nome) VALUES
('Cozinha'),
('Sala'),
('Quarto'),
('Casa de banho'),
('Lavandaria'),
('Garagem'),
('Escritório');