from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()

class crud_usuarios:
    def consultar(self, buscar):
        return db.consultar(
            "SELECT * FROM usuarios_usss091825 WHERE usuario LIKE %s OR nombre LIKE %s",
            (f"%{buscar}%", f"%{buscar}%")
        )
    def crud_usuarios_usss091825(self, datos):
        try:
            if datos['accion'] != 'eliminar':
                # no permitir dos usuarios con el mismo nombre de usuario
                repetido = db.consultar(
                    "SELECT idUsuario FROM usuarios_usss091825 WHERE usuario=%s AND idUsuario<>%s",
                    (datos['usuario'], datos['idUsuario'] or 0)
                )
                if repetido:
                    return "El usuario ya existe, elija otro nombre de usuario."

            if datos['accion'] == 'nuevo':
                sql = """
                    INSERT INTO usuarios_usss091825(usuario,clave,nombre,direccion,telefono)
                    VALUES(%s,%s,%s,%s,%s)
                """
                valores = (datos['usuario'], datos['clave'], datos['nombre'], datos['direccion'], datos['telefono'])
            elif datos['accion'] == 'modificar':
                sql = """
                    UPDATE usuarios_usss091825 SET usuario=%s,clave=%s,nombre=%s,direccion=%s,telefono=%s
                    WHERE idUsuario=%s
                """
                valores = (datos['usuario'], datos['clave'], datos['nombre'], datos['direccion'], datos['telefono'], datos['idUsuario'])
            else:
                sql = """
                    DELETE FROM usuarios_usss091825 WHERE idUsuario=%s
                """
                valores = (datos['idUsuario'],)
            return db.ejecutar(sql, valores)
        except Error as e:
            return f"Error al guardar el usuario: {e}"

    def login(self, datos):
        # BINARY hace que la clave distinga mayusculas y minusculas
        usuarios = db.consultar(
            "SELECT idUsuario FROM usuarios_usss091825 WHERE usuario=%s AND BINARY clave=%s",
            (datos['usuario'], datos['clave'])
        )
        if usuarios:
            return 'ok'
        return 'Usuario o clave incorrectos.'
