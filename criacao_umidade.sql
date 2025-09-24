-- Criação da tabela CIDADE para armazenar informações sobre as cidades
CREATE DATABASE db_umidade;
USE db_umidade;

CREATE TABLE CIDADE (
    id_cidade INT PRIMARY KEY AUTO_INCREMENT,
    nome_cidade VARCHAR(255) NOT NULL
);

-- Criação da tabela PERIODO_TEMPO para armazenar os períodos de tempo das leituras
CREATE TABLE PERIODO_TEMPO (
    id_periodo INT PRIMARY KEY AUTO_INCREMENT,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME NOT NULL
);

-- Criação da tabela LEITURA_UMIDADE para armazenar os dados de umidade coletados
CREATE TABLE LEITURA_UMIDADE (
    id_leitura INT PRIMARY KEY AUTO_INCREMENT,
    valor_umidade DECIMAL(5, 2) NOT NULL,
    data_hora_leitura DATETIME NOT NULL,
    id_cidade INT,
    id_periodo INT,

    FOREIGN KEY (id_cidade) REFERENCES CIDADE(id_cidade),
    FOREIGN KEY (id_periodo) REFERENCES PERIODO_TEMPO(id_periodo)
);cidade