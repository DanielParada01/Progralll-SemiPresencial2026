CREATE DATABASE IF NOT EXISTS db_academica;
USE db_academica;

CREATE TABLE IF NOT EXISTS usuarios_usss091825 (
    idUsuario INT(10) NOT NULL AUTO_INCREMENT,
    usuario CHAR(35),
    clave CHAR(35),
    nombre CHAR(85),
    direccion CHAR(100),
    telefono CHAR(9),
    PRIMARY KEY (idUsuario)
) DEFAULT CHARSET=utf8mb4;

-- Primer usuario para poder entrar al login por primera vez
INSERT INTO usuarios_usss091825 (usuario, clave, nombre, direccion, telefono)
VALUES ('admin', 'admin123', 'Administrador', 'San Salvador', '7777-7777');