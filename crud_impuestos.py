import math
from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()

class crud_impuestos:
    def calcular_impuesto(self, balance, codigo_producto):
        try:
            # RF 10: Limites inclusivos (Desde <= Balance <= Hasta)
            sql = f"SELECT * FROM tarifas_impuestos WHERE codigo_producto='{codigo_producto}' AND {balance} >= desde AND {balance} <= hasta"
            tarifas = db.consultar(sql)

            # RF 11: Tarifa inexistente (Ej: el hueco de 6000 a 8000)
            if not tarifas or len(tarifas) == 0:
                return {'error': 'No existe una tarifa configurada para el balance indicado.'}

            # RF 12: Tarifas superpuestas
            if len(tarifas) > 1:
                return {'error': 'Existe más de una tarifa aplicable. Corrija la tabla tarifaria.'}

            t = tarifas[0]
            precio_base = float(t['precio_base'])
            adicional = float(t['adicional'])
            porcentaje = float(t['porcentaje'])
            desde = float(t['desde'])

            # Fórmulas de cálculo según el documento
            if porcentaje > 0:
                impuesto = float(balance) * (porcentaje / 100)
                bloques = 0
            else:
                excedente = float(balance) - desde
                # Bloques por cada mil o fracción usando CEIL
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
        return db.consultar(f"SELECT * FROM periodos_impuestos WHERE idCliente = {idCliente} ORDER BY fecha_desde DESC")

    def guardar_periodo(self, datos):
        try:
            # RF 03: Desde menor que Hasta
            if datos['fecha_desde'] >= datos['fecha_hasta']:
                return "La fecha Hasta debe ser posterior a la fecha Desde."

            # RF 04: Los períodos no pueden superponerse
            sql_check = f"""
                SELECT idPeriodo FROM periodos_impuestos
                WHERE idCliente = {datos['idCliente']} AND codigo_producto = '{datos['codigo_producto']}'
                AND fecha_desde < '{datos['fecha_hasta']}' AND fecha_hasta > '{datos['fecha_desde']}'
            """
            conflictos = db.consultar(sql_check)
            if conflictos and len(conflictos) > 0:
                return "El período indicado se superpone con un período existente."

            # RF 01 y RF 15: Guardar el nuevo periodo
            sql = """
                INSERT INTO periodos_impuestos(idCliente, codigo_producto, fecha_desde, fecha_hasta, balance, precio_mensual, estado)
                VALUES(%s, %s, %s, %s, %s, %s, 'Vigente')
            """
            valores = (datos['idCliente'], datos['codigo_producto'], datos['fecha_desde'], datos['fecha_hasta'], datos['balance'], datos['precio_mensual'])
            return db.ejecutar(sql, valores)
        except Error as e:
            return f"Error al guardar el periodo: {e}"