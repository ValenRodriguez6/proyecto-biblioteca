
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    fecha_alta DATE NOT NULL,
    antiguedad_meses INT NOT NULL
);

CREATE TABLE libros (
    id_libro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(150) NOT NULL,
    anio_publicacion INT,
    categoria VARCHAR(100),
    stock INT NOT NULL
);

CREATE TABLE prestamos (
    id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_libro INT NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion DATE,
    devuelto TINYINT(1) NOT NULL DEFAULT 0,
    multa DECIMAL(10,2) NOT NULL DEFAULT 0,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,

    FOREIGN KEY (id_libro)
        REFERENCES libros(id_libro)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_pago DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    mes INT NOT NULL,
    anio INT NOT NULL,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE cuotas (
    id_cuota INT AUTO_INCREMENT PRIMARY KEY,
    mes TINYINT NOT NULL,
    anio SMALLINT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    UNIQUE KEY (mes, anio)
);

INSERT INTO usuarios (nombre, apellido, email, fecha_alta, antiguedad_meses)
VALUES
('Diego', 'Fernandez', 'diego@gmail.com', '2024-01-15', 10),
('Ana', 'Martinez', 'ana@gmail.com', '2024-02-10', 9),
('Luis', 'Gomez', 'luis@gmail.com', '2024-03-05', 8),
('Carla', 'Sosa', 'carla@gmail.com', '2023-12-20', 11),
('Ricardo', 'Nuñez', 'ricardo@gmail.com', '2024-01-25', 10),
('Marina', 'Torres', 'marina@gmail.com', '2024-02-01', 9),
('Jorge', 'Castro', 'jorge@gmail.com', '2023-11-30', 12),
('Lucia', 'Paz', 'lucia@gmail.com', '2024-03-01', 8),
('Pablo', 'Acosta', 'pablo@gmail.com', '2024-04-01', 7),
('Sofia', 'Luna', 'sofia@gmail.com', '2024-01-10', 10);

INSERT INTO libros (titulo, autor, anio_publicacion, categoria, stock)
VALUES
('El principito', 'Antoine de Saint-Exupéry', 1943, 'Ficción', 5),
('Cien años de soledad', 'Gabriel García Márquez', 1967, 'Realismo mágico', 4),
('1984', 'George Orwell', 1949, 'Distopía', 6),
('Fahrenheit 451', 'Ray Bradbury', 1953, 'Ciencia ficción', 3),
('Orgullo y prejuicio', 'Jane Austen', 1813, 'Romance', 4),
('It', 'Stephen King', 1986, 'Terror', 2),
('El alquimista', 'Paulo Coelho', 1988, 'Ficción', 6),
('La metamorfosis', 'Franz Kafka', 1915, 'Ficción', 4),
('Crimen y castigo', 'Fiódor Dostoyevski', 1866, 'Drama', 5),
('Harry Potter y la piedra filosofal', 'J.K. Rowling', 1997, 'Fantasía', 7);


INSERT INTO cuotas (mes, anio, monto)
VALUES 
(1, 2025, 3000),
(2, 2025, 3000),
(11, 2025, 3000);

CREATE INDEX idx_prestamos_id_usuario ON prestamos(id_usuario);

CREATE INDEX idx_prestamos_id_libro ON prestamos(id_libro);

CREATE INDEX idx_pagos_usuario_mes_anio ON pagos(id_usuario, mes, anio);

CREATE INDEX idx_libros_titulo ON libros(titulo);
DELIMITER $$

CREATE FUNCTION calcular_multa(fecha_prestamo DATE) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE dias INT;
    DECLARE atraso INT;
    DECLARE cuota_monto DECIMAL(10,2);
    DECLARE multa DECIMAL(10,2);

    SET dias = DATEDIFF(CURDATE(), fecha_prestamo);
    SET atraso = GREATEST(dias - 30, 0);

    SELECT monto INTO cuota_monto
    FROM cuotas
    WHERE mes = MONTH(CURDATE()) AND anio = YEAR(CURDATE())
    LIMIT 1;

    IF cuota_monto IS NULL THEN
        SET cuota_monto = 3000.00;
    END IF;

    SET multa = atraso * (cuota_monto * 0.03);
    RETURN ROUND(multa, 2);
END$$
DELIMITER ;
DELIMITER $$

CREATE PROCEDURE registrar_prestamo_sp(
    IN p_id_usuario INT,
    IN p_id_libro INT,
    IN p_fecha_prestamo DATE,
    IN p_fecha_devolucion DATE
)
BEGIN
    DECLARE v_stock INT;

    START TRANSACTION;

    SELECT stock INTO v_stock
    FROM libros
    WHERE id_libro = p_id_libro
    FOR UPDATE;

    IF v_stock IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Libro no existe';
    ELSEIF v_stock <= 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Sin stock';
    ELSE
        INSERT INTO prestamos (id_usuario, id_libro, fecha_prestamo, fecha_devolucion, devuelto, multa)
        VALUES (p_id_usuario, p_id_libro, p_fecha_prestamo, p_fecha_devolucion, 0, 0);

        UPDATE libros
        SET stock = stock - 1
        WHERE id_libro = p_id_libro;

        COMMIT;
    END IF;

END$$
DELIMITER ;
DELIMITER $$

CREATE PROCEDURE devolver_prestamo_sp(
    IN p_id_prestamo INT
)
BEGIN
    DECLARE v_id_libro INT;
    DECLARE v_fecha_prestamo DATE;
    DECLARE v_devuelto TINYINT;
    DECLARE v_multa DECIMAL(10,2);

    START TRANSACTION;

    SELECT id_libro, fecha_prestamo, devuelto
    INTO v_id_libro, v_fecha_prestamo, v_devuelto
    FROM prestamos
    WHERE id_prestamo = p_id_prestamo
    FOR UPDATE;

    IF v_id_libro IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prestamo no existe';
    ELSEIF v_devuelto = 1 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prestamo ya devuelto';
    ELSE
        SET v_multa = calcular_multa(v_fecha_prestamo);

        UPDATE prestamos
        SET fecha_devolucion = CURDATE(),
            devuelto = 1,
            multa = v_multa
        WHERE id_prestamo = p_id_prestamo;

        UPDATE libros
        SET stock = stock + 1
        WHERE id_libro = v_id_libro;

        COMMIT;
    END IF;

END$$
DELIMITER ;
