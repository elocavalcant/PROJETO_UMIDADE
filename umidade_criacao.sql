-- Criação da tabela CIDADE para armazenar informações sobre as cidades
CREATE DATABASE db_umidade;
USE db_umidade;

CREATE TABLE CIDADE (
    id_cidade INT PRIMARY KEY AUTO_INCREMENT,
    nome_cidade VARCHAR(255) NOT NULL
);

DROP TABLE CIDADE;
-- Criação da tabela PERIODO_TEMPO para armazenar os períodos de tempo das leituras
CREATE TABLE PERIODO_TEMPO (
    id_periodo INT PRIMARY KEY AUTO_INCREMENT,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME NOT NULL,
    turno VARCHAR(15)
);
DROP TABLE PERIODO_TEMPO;
-- Criação da tabela LEITURA_UMIDADE para armazenar os dados de umidade coletados
CREATE TABLE LEITURA (
    id_leitura INT PRIMARY KEY AUTO_INCREMENT,
    umidade DECIMAL(5, 2) NOT NULL,
	altitude DECIMAL(5, 2) NOT NULL,
    temperatura DECIMAL(5, 2) NOT NULL,
    pressao DECIMAL(10, 2) NOT NULL,
    co2 INT NOT NULL,
    tempo_registro DATETIME NOT NULL
);

drop table LEITURA;

select * from LEITURA;