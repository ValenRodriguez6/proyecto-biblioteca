import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "47671188",
    "database": "biblioteca",
    "raise_on_warnings": True
}

def crear_conexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except:
        return None

def pedir_fecha(msg):
    while True:
        s = input(f"{msg} (YYYY-MM-DD): ")
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except:
            print("Fecha inválida")

def calcular_antiguedad_meses(f):
    h = date.today()
    m = (h.year - f.year) * 12 + (h.month - f.month)
    if h.day < f.day:
        m -= 1
    return max(m, 0)

def input_non_empty(msg):
    while True:
        v = input(msg).strip()
        if v:
            return v
        print("Campo vacío")

def obtener_cuota(mes, anio):
    conexion = crear_conexion()
    if conexion is None:
        return 3000
    cursor = conexion.cursor()
    cursor.execute("SELECT monto FROM cuotas WHERE mes=%s AND anio=%s LIMIT 1", (mes, anio))
    r = cursor.fetchone()
    cursor.close()
    conexion.close()
    if r:
        return float(r[0])
    return 3000

def agregar_usuario():
    conexion = crear_conexion()
    if conexion is None:
        return
    nombre = input_non_empty("Nombre: ")
    apellido = input_non_empty("Apellido: ")
    email = input_non_empty("Email: ")
    fecha_alta = pedir_fecha("Fecha alta")
    antig = calcular_antiguedad_meses(fecha_alta)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nombre,apellido,email,fecha_alta,antiguedad_meses)
        VALUES (%s,%s,%s,%s,%s)
    """, (nombre, apellido, email, fecha_alta, antig))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Usuario agregado")

def listar_usuarios():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario,nombre,apellido,email,fecha_alta,antiguedad_meses FROM usuarios")
    rows = cursor.fetchall()
    print("\n--- USUARIOS ---")
    print(f"{'ID':<4} {'Nombre':<15} {'Apellido':<15} {'Email':<30} {'Alta':<12} {'Antig':<5}")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]:<4} {r[1]:<15} {r[2]:<15} {r[3]:<30} {str(r[4]):<12} {r[5]:<5}")
    cursor.close()
    conexion.close()

def eliminar_usuario():
    conexion = crear_conexion()
    if conexion is None:
        return
    idu = input_non_empty("ID usuario: ")
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario FROM usuarios WHERE id_usuario=%s", (idu,))
    if cursor.fetchone() is None:
        print("No existe")
        cursor.close()
        conexion.close()
        return
    cursor.execute("""
        SELECT 1 
        FROM prestamos 
        WHERE id_usuario=%s AND devuelto = 0
        LIMIT 1
    """, (idu,))
    if cursor.fetchone():
        print("No se puede eliminar: el usuario tiene préstamos activos.")
        cursor.close()
        conexion.close()
        return
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    cursor.execute("""
        SELECT 1 
        FROM pagos 
        WHERE id_usuario=%s AND mes=%s AND anio=%s
        LIMIT 1
    """, (idu, mes_actual, anio_actual))
    if cursor.fetchone():
        print("No se puede eliminar: el usuario tiene pagos del mes actual.")
        cursor.close()
        conexion.close()
        return
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (idu,))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Usuario eliminado correctamente.")



def agregar_libro():
    conexion = crear_conexion()
    if conexion is None:
        return
    titulo = input_non_empty("Título: ")
    autor = input_non_empty("Autor: ")
    anio = input("Año: ")
    anio = int(anio) if anio.isdigit() else None
    cat = input("Categoría: ") or None
    st = input_non_empty("Stock: ")
    if not st.isdigit():
        print("Stock inválido")
        conexion.close()
        return
    st = int(st)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO libros (titulo,autor,anio_publicacion,categoria,stock)
        VALUES (%s,%s,%s,%s,%s)
    """, (titulo, autor, anio, cat, st))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Libro agregado")

def listar_libros():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor()
    cursor.execute("SELECT id_libro,titulo,autor,anio_publicacion,categoria,stock FROM libros ORDER BY id_libro")
    rows = cursor.fetchall()
    print("\n--- LIBROS ---")
    print(f"{'ID':<4} {'Título':<30} {'Autor':<20} {'Año':<6} {'Cat':<15} {'Stock':<6}")
    print("-" * 95)
    for l in rows:
        t = (l[1][:29] + "…") if len(l[1]) > 30 else l[1]
        a = (l[2][:19] + "…") if len(l[2]) > 20 else l[2]
        print(f"{l[0]:<4} {t:<30} {a:<20} {str(l[3]):<6} {str(l[4]):<15} {l[5]:<6}")
    cursor.close()
    conexion.close()

def eliminar_libro():
    conexion = crear_conexion()
    if conexion is None:
        return
    idl = input_non_empty("ID libro: ")
    cursor = conexion.cursor()
    cursor.execute("SELECT id_libro FROM libros WHERE id_libro=%s", (idl,))
    if cursor.fetchone() is None:
        print("No existe")
        cursor.close()
        conexion.close()
        return
    cursor.execute("SELECT 1 FROM prestamos WHERE id_libro=%s LIMIT 1", (idl,))
    if cursor.fetchone():
        print("Tiene préstamos")
        cursor.close()
        conexion.close()
        return
    cursor.execute("DELETE FROM libros WHERE id_libro=%s", (idl,))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Libro eliminado")

def modificar_stock():
    conexion = crear_conexion()
    if conexion is None:
        return
    idl = input("ID libro: ")
    if not idl.isdigit():
        print("Inválido")
        conexion.close()
        return
    st = input("Nuevo stock: ")
    if not st.isdigit():
        print("Inválido")
        conexion.close()
        return
    cursor = conexion.cursor()
    cursor.execute("UPDATE libros SET stock=%s WHERE id_libro=%s", (st, idl))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Stock actualizado")

def registrar_prestamo():
    conexion = crear_conexion()
    if conexion is None:
        return
    idu = input_non_empty("ID usuario: ")
    idl = input_non_empty("ID libro: ")
    fp = pedir_fecha("Fecha préstamo")
    fd = pedir_fecha("Fecha devolución prevista")
    cursor = conexion.cursor()
    try:
        cursor.callproc("registrar_prestamo_sp", (int(idu), int(idl), fp, fd))
        conexion.commit()
        print("Préstamo registrado (SP)")
        cursor.close()
        conexion.close()
        return
    except:
        pass
    cursor.execute("SELECT stock FROM libros WHERE id_libro=%s FOR UPDATE", (idl,))
    r = cursor.fetchone()
    if r is None or r[0] <= 0:
        print("Sin stock")
        cursor.close()
        conexion.close()
        return
    conexion.start_transaction()
    cursor.execute("""
        INSERT INTO prestamos (id_usuario,id_libro,fecha_prestamo,fecha_devolucion,devuelto,multa)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (idu, idl, fp, fd, 0, 0))
    cursor.execute("UPDATE libros SET stock=stock-1 WHERE id_libro=%s", (idl,))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Préstamo registrado")

def listar_prestamos():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            p.id_prestamo,
            u.nombre,
            u.apellido,
            l.titulo,
            p.fecha_prestamo,
            p.fecha_devolucion,
            p.devuelto,
            p.multa
        FROM prestamos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        JOIN libros l ON p.id_libro = l.id_libro
        ORDER BY p.id_prestamo
    """)
    rows = cursor.fetchall()
    print("\n--- PRÉSTAMOS ---")
    print(f"{'ID':<4} {'Usuario':<20} {'Libro':<25} {'F.Prest':<12} {'F.Dev':<12} {'Dev':<6} {'Multa':<10}")
    print("-" * 100)
    for r in rows:
        idp = r[0]
        usuario = f"{r[1]} {r[2]}"
        libro = r[3][:24] + ("…" if len(r[3]) > 25 else "")
        
        fprest = r[4].strftime("%Y-%m-%d")
        fdev = r[5].strftime("%Y-%m-%d") if r[5] else "-"
        
        dev = "Sí" if r[6] else "No"
        multa = f"{float(r[7]):.2f}"
        print(f"{idp:<4} {usuario:<20} {libro:<25} {fprest:<12} {fdev:<12} {dev:<6} {multa:<10}")
    cursor.close()
    conexion.close()


def devolver_prestamo():
    conexion = crear_conexion()
    if conexion is None:
        return
    idp = input("ID préstamo: ")
    if not idp.isdigit():
        print("Inválido")
        conexion.close()
        return
    idp = int(idp)
    cursor = conexion.cursor()
    try:
        cursor.callproc("devolver_prestamo_sp", (idp,))
        conexion.commit()
        print("Devuelto (SP)")
        cursor.close()
        conexion.close()
        return
    except:
        pass

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_libro,p.fecha_prestamo,p.devuelto,u.nombre,u.apellido,l.titulo
        FROM prestamos p
        JOIN usuarios u ON p.id_usuario=u.id_usuario
        JOIN libros l ON p.id_libro=l.id_libro
        WHERE p.id_prestamo=%s
        FOR UPDATE
    """, (idp,))
    pr = cursor.fetchone()

    if pr is None:
        print("No existe")
        cursor.close()
        conexion.close()
        return

    if pr["devuelto"]:
        print("Ya devuelto")
        cursor.close()
        conexion.close()
        return

    hoy = date.today()
    dias = (hoy - pr["fecha_prestamo"]).days
    atraso = max(0, dias - 30)
    cuota = obtener_cuota(hoy.month, hoy.year)
    multa = atraso * (cuota * 0.03)

    conexion.start_transaction()
    cursor.execute("""
        UPDATE prestamos
        SET fecha_devolucion=%s, devuelto=1, multa=%s
        WHERE id_prestamo=%s
    """, (hoy, multa, idp))
    cursor.execute("UPDATE libros SET stock=stock+1 WHERE id_libro=%s", (pr["id_libro"],))
    conexion.commit()

    cursor.close()
    conexion.close()
    print("Devuelto")

def registrar_pago():
    conexion = crear_conexion()
    if conexion is None:
        return
    idu = input("ID usuario: ")
    if not idu.isdigit():
        print("Inválido")
        return
    monto = input("Monto: ")
    try:
        monto = float(monto)
    except:
        print("Inválido")
        return
    f = input("Fecha (YYYY-MM-DD): ")
    try:
        datetime.strptime(f, "%Y-%m-%d")
    except:
        print("Inválido")
        return
    mes = input("Mes (1-12): ")
    anio = input("Año: ")
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO pagos (id_usuario,fecha_pago,monto,mes,anio)
        VALUES (%s,%s,%s,%s,%s)
    """, (idu, f, monto, mes, anio))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Pago registrado")

def listar_pagos():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT pa.id_pago,u.nombre,u.apellido,pa.fecha_pago,pa.monto,pa.mes,pa.anio
        FROM pagos pa
        JOIN usuarios u ON pa.id_usuario=u.id_usuario
        ORDER BY pa.id_pago
    """)
    rows = cursor.fetchall()
    print("\n--- PAGOS ---")
    print(f"{'ID':<4} {'Usuario':<20} {'Fecha':<12} {'Monto':<10} {'Mes':<5} {'Año':<5}")
    print("-" * 70)
    for p in rows:
        usr = f"{p[1]} {p[2]}"
        fecha = p[3].strftime("%Y-%m-%d")
        monto = f"{float(p[4]):.2f}"
        print(f"{p[0]:<4} {usr:<20} {fecha:<12} {monto:<10} {p[5]:<5} {p[6]:<5}")
    cursor.close()
    conexion.close()

def modificar_cuota():
    conexion = crear_conexion()
    if conexion is None:
        return
    mes = input("Mes: ")
    anio = input("Año: ")
    monto = input("Monto: ")
    try:
        monto = float(monto)
    except:
        print("Inválido")
        return
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cuota FROM cuotas WHERE mes=%s AND anio=%s", (mes, anio))
    if cursor.fetchone():
        cursor.execute("UPDATE cuotas SET monto=%s WHERE mes=%s AND anio=%s", (monto, mes, anio))
    else:
        cursor.execute("INSERT INTO cuotas (mes,anio,monto) VALUES (%s,%s,%s)", (mes, anio, monto))
    conexion.commit()
    cursor.close()
    conexion.close()
    print("Cuota actualizada")

def buscar_libros():
    conexion = crear_conexion()
    if conexion is None:
        return
    txt = input("Texto: ")
    like = f"%{txt}%"
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id_libro,titulo,autor,anio_publicacion,categoria,stock
        FROM libros
        WHERE titulo LIKE %s OR autor LIKE %s
    """, (like, like))
    rows = cursor.fetchall()
    print("\n--- RESULTADOS LIBROS ---")
    print(f"{'ID':<4} {'Título':<30} {'Autor':<20} {'Año':<6} {'Cat':<15} {'Stock':<6}")
    print("-" * 95)
    for l in rows:
        t = (l[1][:29] + "…") if len(l[1]) > 30 else l[1]
        a = (l[2][:19] + "…") if len(l[2]) > 20 else l[2]
        print(f"{l[0]:<4} {t:<30} {a:<20} {str(l[3]):<6} {str(l[4]):<15} {l[5]:<6}")
    cursor.close()
    conexion.close()

def buscar_usuarios():
    conexion = crear_conexion()
    if conexion is None:
        return
    txt = input("Texto: ")
    like = f"%{txt}%"
    cursor = conexion.cursor()
    resultados = []
    if txt.isdigit():
        cursor.execute("""
            SELECT id_usuario, nombre, apellido, email, fecha_alta, antiguedad_meses 
            FROM usuarios 
            WHERE id_usuario = %s
        """, (txt,))
        r = cursor.fetchone()
        if r:
            resultados.append(r)
    cursor.execute("""
        SELECT id_usuario, nombre, apellido, email, fecha_alta, antiguedad_meses
        FROM usuarios
        WHERE nombre LIKE %s OR apellido LIKE %s OR email LIKE %s
    """, (like, like, like))
    resultados.extend(cursor.fetchall())
    cursor.close()
    conexion.close()
    if not resultados:
        print("\nNo se encontraron usuarios.")
        return
    print("\n--- RESULTADOS USUARIOS ---")
    print(f"{'ID':<4} {'Nombre':<15} {'Apellido':<15} {'Email':<30} {'Alta':<12} {'Antig':<5}")
    print("-" * 90)
    for u in resultados:
        idu = u[0]
        nombre = u[1]
        apellido = u[2]
        email = u[3]
        alta = u[4].strftime("%Y-%m-%d")
        antig = u[5]
        print(f"{idu:<4} {nombre:<15} {apellido:<15} {email:<30} {alta:<12} {antig:<5}")


def reporte_morosos():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id_usuario,u.nombre,u.apellido,u.antiguedad_meses,
        (SELECT COUNT(DISTINCT CONCAT(mes,'-',anio)) FROM pagos WHERE id_usuario=u.id_usuario) AS pagados
        FROM usuarios u
    """)
    rows = cursor.fetchall()
    print("\n--- MOROSOS ---")
    print(f"{'ID':<4} {'Nombre':<15} {'Apellido':<15} {'Antig':<6} {'Pagados':<7} {'Adeuda':<7}")
    print("-" * 70)
    for r in rows:
        pag = r["pagados"] or 0
        ade = r["antiguedad_meses"] - pag
        if ade > 0:
            print(f"{r['id_usuario']:<4} {r['nombre']:<15} {r['apellido']:<15} {r['antiguedad_meses']:<6} {pag:<7} {ade:<7}")
    cursor.close()
    conexion.close()

def usuarios_sin_prestamos():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT u.id_usuario,u.nombre,u.apellido
        FROM usuarios u
        LEFT JOIN prestamos p ON u.id_usuario=p.id_usuario AND p.devuelto=0
        WHERE p.id_prestamo IS NULL
    """)
    rows = cursor.fetchall()
    print("\n--- USUARIOS SIN PRÉSTAMOS ACTIVOS ---")
    print(f"{'ID':<4} {'Nombre':<15} {'Apellido':<15}")
    print("-" * 40)
    for r in rows:
        print(f"{r[0]:<4} {r[1]:<15} {r[2]:<15}")
    cursor.close()
    conexion.close()

def prestamos_por_libro_incluyendo_sin_prestar():
    conexion = crear_conexion()
    if conexion is None:
        return
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT l.id_libro,l.titulo,p.id_prestamo
        FROM libros l
        LEFT JOIN prestamos p ON l.id_libro=p.id_libro
        ORDER BY l.id_libro
    """)
    rows = cursor.fetchall()
    print("\n--- LIBROS + PRÉSTAMOS ---")
    print(f"{'ID':<4} {'Título':<30} {'ID Prestamo':<12}")
    print("-" * 55)
    for r in rows:
        t = (r[1][:29] + "…") if len(r[1]) > 30 else r[1]
        print(f"{r[0]:<4} {t:<30} {str(r[2]):<12}")
    cursor.close()
    conexion.close()

def menu():
    while True:
        print("""
1. Agregar usuario
2. Listar usuarios
3. Eliminar usuario
4. Agregar libro
5. Listar libros
6. Eliminar libro
7. Modificar stock
8. Registrar préstamo
9. Listar préstamos
10. Devolver préstamo
11. Registrar pago
12. Listar pagos
13. Buscar libros
14. Buscar usuarios
15. Reporte morosos
16. Modificar cuota
17. Usuarios sin préstamos
18. Libros + préstamos
0. Salir
""")
        op = input("Opción: ")
        if op == "1": agregar_usuario()
        elif op == "2": listar_usuarios()
        elif op == "3": eliminar_usuario()
        elif op == "4": agregar_libro()
        elif op == "5": listar_libros()
        elif op == "6": eliminar_libro()
        elif op == "7": modificar_stock()
        elif op == "8": registrar_prestamo()
        elif op == "9": listar_prestamos()
        elif op == "10": devolver_prestamo()
        elif op == "11": registrar_pago()
        elif op == "12": listar_pagos()
        elif op == "13": buscar_libros()
        elif op == "14": buscar_usuarios()
        elif op == "15": reporte_morosos()
        elif op == "16": modificar_cuota()
        elif op == "17": usuarios_sin_prestamos()
        elif op == "18": prestamos_por_libro_incluyendo_sin_prestar()
        elif op == "0":
            print("Saliendo...")
            break
        else:
            print("Inválido")

if __name__ == "__main__":
    menu()
