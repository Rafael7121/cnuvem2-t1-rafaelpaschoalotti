-- ================================================================
-- schema.sql — Criação do banco, tabela e inserção de dados iniciais
-- ================================================================
-- Disciplina: Computação em Nuvem II (ISW035)
-- Descrição:  Este script cria o banco de dados 'app_projeto',
--             a tabela 'produtos' e insere 5 registros de exemplo
--             que serão consultados pela aplicação Python.
-- Uso:
--   mysql -h HOST -u USER -p --ssl-mode=REQUIRED < sql/schema.sql
-- ================================================================

-- Cria o banco de dados caso ainda não exista
CREATE DATABASE IF NOT EXISTS app_projeto
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- Seleciona o banco para uso
USE app_projeto;

-- Cria a tabela 'produtos' com 5 colunas
-- id:        identificador único auto-incrementado
-- nome:      nome do produto (obrigatório)
-- descricao: descrição detalhada (opcional)
-- preco:     preço com 2 casas decimais (obrigatório)
-- categoria: categoria do produto (opcional)
-- criado_em: data/hora de criação (preenchido automaticamente)
CREATE TABLE IF NOT EXISTS produtos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100)   NOT NULL,
    descricao   TEXT,
    preco       DECIMAL(10,2)  NOT NULL,
    categoria   VARCHAR(50),
    criado_em   DATETIME       DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insere 5 registros de exemplo na tabela
-- Esses dados serão consultados pela aplicação Python
INSERT INTO produtos (nome, descricao, preco, categoria) VALUES
    ('Notebook Gamer',    'Notebook 16GB RAM, RTX 4060',       5499.90, 'Eletrônicos'),
    ('Mouse Wireless',    'Mouse ergonômico sem fio',           149.90, 'Periféricos'),
    ('Teclado Mecânico',  'Teclado switch blue, RGB',           329.90, 'Periféricos'),
    ('Monitor 27"',       'Monitor IPS 144Hz',                 1899.00, 'Eletrônicos'),
    ('Webcam Full HD',    'Webcam 1080p com microfone embutido', 249.90, 'Periféricos');