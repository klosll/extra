import base64
import pandas as pd
from io import BytesIO
from odoo.exceptions import UserError

def action_import_excel(self):
    if not self.import_file:
        raise UserError("Debe cargar un archivo para continuar.")
    try:
        file_content = base64.b64decode(self.import_file)
        excel_buffer = BytesIO(file_content)
        data = pd.read_excel(excel_buffer, dtype=str)
    except Exception as e:
        raise UserError(f"Error al leer el archivo Excel: {e}")

    required_columns = ['CODE', 'QTY']
    for column in required_columns:
        if column not in data.columns:
            raise UserError(f"La columna '{column}' es requerida en el archivo.")

    # Obtener todos los default_code primero
    product_codes = data['CODE'].unique().tolist()
    products = self.env['product.template'].search([('default_code', 'in', product_codes)])
    product_map = {product.default_code: product.product_variant_id.id for product in products}
    if len(product_map) != len(product_codes):
        missing = set(product_codes) - set(product_map.keys())
        raise UserError(f"Productos no encontrados para los códigos: {', '.join(missing)}")

    lines = []
    for index, row in data.iterrows():
        product_code = row['CODE']
        lot_id = self.env['stock.production.lot'].search([('name', '=', row.get('LOT'))], limit=1).id
        product_id = product_map.get(product_code)
        inventory_line = {
            'product_id': product_id,
            'prod_lot_id': lot_id,
            'product_qty': row['QTY'],
            'location_id': self.location_id.id,
        }
        lines.append((0, 0, inventory_line))
    self.line_ids = lines