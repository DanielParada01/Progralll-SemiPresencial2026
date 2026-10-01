import math
from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()

class crud_impuestos:
    def calcular_impuesto(self, balance, codigo_producto):
        try:
            sql = f"SELECT * FROM tarifas_impuestos WHERE codigo_producto='{codigo_producto}' AND {balance} >= desde AND {balance} <= hasta"
            tarifas = db.consultar(sql)

            if not tarifas or len(tarifas) == 0:
                return {'error': 'No existe una tarifa configurada para el balance indicado.'}

            if len(tarifas) > 1:
                return {'error': 'Existe más de una tarifa aplicable. Corrija la tabla tarifaria.'}

            t = tarifas[0]
            precio_base = float(t['precio_base'])
            adicional = float(t['adicional'])
            porcentaje = float(t['porcentaje'])
            desde = float(t['desde'])

            if porcentaje > 0:
                impuesto = float(balance) * (porcentaje / 100)
                bloques = 0
            else:
                excedente = float(balance) - desde
                bloques = math.ceil(excedente / 1000.0)
                impuesto = precio_base + (bloques * adicional)

            return {
                'msg': 'ok',
                'impuesto_mensual': round(impuesto, 2),
                'rango': f"${t['desde']} a ${t['hasta']}",
                'precio_base': precio_base,
                'excedente': round(float(balance) - desde, 2) if porcentaje == 0 else 0,
                'bloques': bloques,
                'adicional': adicional
            }
        except Exception as e:
            return {'error': f"Error de servidor: {e}"}

    def consultar_periodos(self, idCliente):
        # Solución analítica: Python json.dumps() falla con objetos Date y Decimal nativos de MySQL.
        # Usamos DATE_FORMAT y CAST en SQL para convertirlos a formatos compatibles antes de enviarlos al frontend.
        sql = f"""
            SELECT 
                idPeriodo, 
                codigo_producto, 
                DATE_FORMAT(fecha_desde, '%Y/%m/%d') as fecha_desde, 
                DATE_FORMAT(fecha_hasta, '%Y/%m/%d') as fecha_hasta, 
                CAST(balance AS FLOAT) as balance, 
                CAST(precio_mensual AS FLOAT) as precio_mensual, 
                estado 
            FROM periodos_impuestos 
            WHERE idCliente = {idCliente} 
            ORDER BY fecha_desde DESC
        """
        return db.consultar(sql)

    def guardar_periodo(self, datos):
        try:
            if datos['fecha_desde'] >= datos['fecha_hasta']:
                return "La fecha Hasta debe ser posterior a la fecha Desde."

            sql_check = f"""
                SELECT idPeriodo FROM periodos_impuestos
                WHERE idCliente = {datos['idCliente']} AND codigo_producto = '{datos['codigo_producto']}'
                AND fecha_desde < '{datos['fecha_hasta']}' AND fecha_hasta > '{datos['fecha_desde']}'
            """
            conflictos = db.consultar(sql_check)
            if conflictos and len(conflictos) > 0:
                return "El período indicado se superpone con un período existente."

            sql = """
                INSERT INTO periodos_impuestos(idCliente, codigo_producto, fecha_desde, fecha_hasta, balance, precio_mensual, estado)
                VALUES(%s, %s, %s, %s, %s, %s, 'Vigente')
            """
            valores = (datos['idCliente'], datos['codigo_producto'], datos['fecha_desde'], datos['fecha_hasta'], datos['balance'], datos['precio_mensual'])
            return db.ejecutar(sql, valores)
        except Error as e:
            return f"Error al guardar el periodo: {e}"