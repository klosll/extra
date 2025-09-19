# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import datetime
from pytz import timezone
import json
import requests

TIMEOUT = 20
# KALEIDOTRANS_TOKEN_ENDPOINT = 'https://portal.kaleidotrans.com/api/Auth/auth.php?licencia=WQQF7T3Q88OBW3BPMB'

class StockPicking(models.Model):
    _inherit = "stock.picking"

    servicio_id = fields.Integer(string='Servicio', help="ID del servicio de KaleidoTrans")
    note_kaleidotrans = fields.Text(string='Mensajes KaleidoTrans')

    def action_send_kaleidotrans(self):
        if self.note_kaleidotrans == False:
            self.note_kaleidotrans = ""
        hoy = datetime.now(timezone(self.env.user.tz))
        fecha_hora = hoy.strftime('%Y-%m-%d %H:%M:%S')
        cargador = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.idcliente')
        if cargador:
            id_cargador = cargador
        else:
            id_cargador = self.cmr_loader_id
        if id_cargador:
            for picking in self:
                token_kaleidotrans = self._generate_refresh_token()
                respuesta = self._get_listar_pedidos(token_kaleidotrans)
                if respuesta['pedidosCompletos'][0]['pedido']['IdPedido'] == self.servicio_id:
                    resp_mod = self._put_modificar_pedidos(token_kaleidotrans)
                    resp_mod_cod = resp_mod.get("code", 200)
                    if resp_mod_cod != 200:
                        picking.note_kaleidotrans = fecha_hora +" -> "+ resp_mod['error'] +"\n"+str(picking.note_kaleidotrans)
                    else:
                        picking.note_kaleidotrans = fecha_hora +" -> "+ resp_mod['mensaje'] +"\n"+str(picking.note_kaleidotrans)
                else:
                    pedido = self._post_pedidos(token_kaleidotrans)
                    pedido_cod = pedido.get("code", 200)
                    if pedido_cod != 200:
                        picking.note_kaleidotrans = fecha_hora +" -> "+ pedido['error'] +"\n"+str(picking.note_kaleidotrans)
                    else:
                        picking.servicio_id = pedido["IdServicio"]
                        picking.note_kaleidotrans = fecha_hora + " -> " + pedido['mensaje'] + "\n" + str(picking.note_kaleidotrans)
        else:
            self.note_kaleidotrans = fecha_hora +" -> El cargador no está asignado." +"\n"+str(self.note_kaleidotrans)

    @api.model
    def _generate_refresh_token(self):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        client_id = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.client_secret')
        values = {'user': client_id, 'password': client_secret}
        url = 'https://portal.kaleidotrans.com/api/Auth/auth.php?licencia='+licencia_code
        headers = {'Content-type': 'application/json'}
        request = requests.post(url, data=json.dumps(values), headers=headers)
        response = request.json()
        return response["token"]

    @api.model
    def _get_conductor(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        conductor_nif = self.crm_driver_id.vat
        if conductor_nif:
            url = 'https://portal.kaleidotrans.com/api/MaestrosPrimarios/Conductores/listar.php?licencia='+licencia_code+\
                  '&NIF='+conductor_nif
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "El Conductor no tiene NIF (Conductores en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_cabeza(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        cabeza_matricula = self.cmr_tractor_id.license_plate
        if cabeza_matricula:
            url = 'https://portal.kaleidotrans.com/api/MaestrosPrimarios/Vehiculos/listar.php?licencia='+licencia_code+\
                  '&matricula='+cabeza_matricula
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "Cabeza de vehículo no tiene matrícula (Vehículos en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_remolque(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        remolque_matricula = self.cmr_semi_trailer_id.license_plate
        if remolque_matricula:
            url = 'https://portal.kaleidotrans.com/api/MaestrosPrimarios/Vehiculos/listar.php?licencia='+licencia_code+\
                  '&matricula='+remolque_matricula
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "Remolque de vehículo no tiene matrícula (Vehículos en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_poblaciones_dir_ent(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        codPostal = self.partner_id.zip
        if codPostal:
            url = 'https://portal.kaleidotrans.com/api/MaestrosSecundarios/Poblaciones/listar.php?licencia='+licencia_code+\
                  '&CodPostal='+codPostal
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "Dirección de entrega no tiene Código Postal (Poblaciones en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_sitios_dir_ent(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        cif = self.partner_id.vat
        if cif:
            prefijo = cif[:2]
            if prefijo == 'ES':
                cif = cif[2:]
            url = 'https://portal.kaleidotrans.com/api/MaestrosSecundarios/Sitios/listar.php?licencia='+licencia_code+\
                  '&CIF='+cif
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "Dirección de entrega no tiene CIF (Sitios en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_poblaciones_cargador(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        company = self.env.company
        codPostal = company.zip
        if not codPostal:
            codPostal = self.cmr_loader_id.zip
        if codPostal:
            url = 'https://portal.kaleidotrans.com/api/MaestrosSecundarios/Poblaciones/listar.php?licencia='+licencia_code+\
                  '&CodPostal='+codPostal
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "El cargador no tiene Código Postal (Poblaciones en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_sitios_cargador(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        company = self.env.company
        cif = company.vat
        if not cif:
            cif = self.cmr_loader_id.vat
        if cif:
            prefijo = cif[:2]
            if prefijo == 'ES':
                cif = cif[2:]
            url = 'https://portal.kaleidotrans.com/api/MaestrosSecundarios/Sitios/listar.php?licencia='+licencia_code+\
                  '&CIF='+cif
            headers = {'Authorization': token_kaleidotrans}
            request = requests.get(url, headers=headers)
            response = request.json()
        else:
            response = {"mensaje": "El cargador no tiene CIF (Sitios en KaleidoTrans).",
                        "code": 404}
        return response

    @api.model
    def _get_bultos(self):
        lista_bultos = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.bultos')
        lista_bultos = lista_bultos.split(',')
        response = 0
        for bulto in lista_bultos:
            domain = [('product_id.default_code', '=', bulto)]
            for line in self.move_line_ids.filtered_domain(domain):
                response = response + line.qty_done
        return response

    @api.model
    def _get_pallet_entrega(self):
        domain = [('product_id.product_tmpl_id.palet', '=', True)]
        response = 0
        for line in self.move_line_ids.filtered_domain(domain):
            response = response + line.qty_done
        return response

    @api.model
    def _get_listar_pedidos(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        idPedido = str(self.servicio_id)
        url = 'https://portal.kaleidotrans.com/api/GestionTrafico/Pedidos/listar.php?licencia='+licencia_code+\
              '&IdPedido='+idPedido
        headers = {'Authorization': token_kaleidotrans}
        request = requests.get(url, headers=headers)
        response = request.json()
        return response

    @api.model
    def _put_modificar_pedidos(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        idPedido = self.servicio_id
        if idPedido:
            fecha_realizado = self.custom_date_done
            fecha_hora = fecha_realizado.strftime('%Y-%m-%d %H:%M:%S')
            fecha = fecha_realizado.strftime('%Y-%m-%d')
            bultos = self._get_bultos()
            if not bultos:
                bultos = 0
            palletEntrega = self._get_pallet_entrega()
            if not palletEntrega:
                palletEntrega = 0
            conductor = self._get_conductor(token_kaleidotrans)
            id_conductor_puntos = conductor.get("code", 200)
            if id_conductor_puntos != 200:
                response = {"error": "Revise NIF del Conductor (Conductores en KaleidoTrans).",
                            "code": 404}
                return response
            vehiculo = self._get_cabeza(token_kaleidotrans)
            id_vehiculo_puntos = vehiculo.get("code", 200)
            if id_vehiculo_puntos != 200:
                response = {"error": "Revise matrícula de Cabeza de vehículo (Vehículos en KaleidoTrans).",
                            "code": 404}
                return response
            remolque = self._get_remolque(token_kaleidotrans)
            id_remolque_puntos = remolque.get("code", 200)
            if id_remolque_puntos != 200:
                response = {"error": "Revise matrícula de Remolque de vehículo (Vehículos en KaleidoTrans).",
                            "code": 404}
                return response
            poblacion_dir_ent = self._get_poblaciones_dir_ent(token_kaleidotrans)
            sitio_dir_ent = self._get_sitios_dir_ent(token_kaleidotrans)
            poblacion_dir_ent_puntos = poblacion_dir_ent.get("code", 200)
            sitio_dir_ent_sitios = sitio_dir_ent.get("code", 200)
            if poblacion_dir_ent_puntos != 200:
                response = {"error": "Revise Cod. Postal de Población de entrega del cliente (Poblaciones en KaleidoTrans).",
                            "code": 404}
                return response
            if sitio_dir_ent_sitios != 200:
                response = {"error": "Revise CIF de entrega del cliente (Sitios en KaleidoTrans).",
                            "code": 404}
                return response
            id_conductor = conductor['choferes'][0]['IdChofer']
            id_vehiculo = vehiculo['vehiculos'][0]['IdVehiculo']
            id_remolque = remolque['vehiculos'][0]['IdVehiculo']
            idPunto_dir_ent = poblacion_dir_ent['puntos'][0]['IdPunto']
            idLugar_dir_ent = sitio_dir_ent['sitios'][0]['IdLugar']
            poblacion_cargador = self._get_poblaciones_cargador(token_kaleidotrans)
            sitio_cargador = self._get_sitios_cargador(token_kaleidotrans)
            poblacion_cargador_puntos = poblacion_cargador.get("code", 200)
            sitio_cargador_sitios = sitio_cargador.get("code", 200)
            if poblacion_cargador_puntos != 200:
                response = {"error": "Revise Cod. Postal de Población del cargador (Poblaciones en KaleidoTrans).",
                            "code": 404}
                return response
            if sitio_cargador_sitios != 200:
                response = {"error": "Revise CIF del cargador.",
                            "code": 404}
                return response
            idPunto_cargador = poblacion_cargador['puntos'][0]['IdPunto']
            idLugar_cargador = sitio_cargador['sitios'][0]['IdLugar']
            sale_name = self.name
            idUsuario = int(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.idusuario'))
            idCliente = int(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.idcliente'))
            precio_cli = float(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.precio_cli'))
            iva_cli = float(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.iva_cli'))
            importe_cli = float(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.importe_cli'))
            peso_envio = self.shipping_weight
            values = {
                "IdPedido": idPedido,
                "FechaCreacion": fecha,
                "estadoPedido": "Servicio",
                "IdFactura": None,
                "IdFacturaPro": None,
                "referencia": sale_name,
                "referencia2": None,
                "IdCliente": idCliente,
                "IdMercancia": None,
                "IdRutaTipo": None,
                "IdGrupoAlbaran": None,
                "IdEstado": None,
                "IdAgenda": None,
                "IdVehiculo": id_vehiculo,
                "IdRemolque": id_remolque,
                "IdRemolque2": None,
                "IdChofer": id_conductor,
                "IdChofer2": None,
                "IdProveedor": None,
                "IdPuntoIntermedio": None,
                "IdDelegacion": None,
                "IdPuntoInicio": None,
                "IdPuntoFin": None,
                "KmCarga": None,
                "KmVacio": None,
                "campo1": None,
                "campo2": None,
                "campo3": None,
                "campo4": None,
                "campo5": None,
                "campo6": None,
                "campo7": None,
                "campo8": None,
                "campo9": None,
                "campo10": None,
                "campo11": None,
                "campo12": None,
                "campo13": None,
                "campo14": None,
                "campo15": None,
                "campo16": None,
                "campo17": None,
                "campo18": None,
                "campo19": None,
                "campo20": None,
                "VehiculoRemolque": None,
                "Fecha_Inicio": fecha,
                "Fecha_Fin": fecha,
                "Hora_Inicio": None,
                "Hora_Fin": None,
                "observacion": None,
                "observacion2": None,
                "nota": None,
                "infoadic_mercancia": None,
                "infoadic_lugarcarga": None,
                "infoadic_lugardescarga": None,
                "incidencia": None,
                "Kms": None,
                "Origen": None,
                "Fin": None,
                "LugarOrigen": None,
                "LugarFin": None,
                "IdTarifa": None,
                "IdZonaOrigen": None,
                "IdZonaDestino": None,
                "IdUsuario": 1,
                "PrecioPro": None,
                "PrecioCli": None,
                "IdConceptoPro": None,
                "IdConceptoCli": None,
                "IdUMPro": None,
                "IdUMCli": None,
                "CantidadPro": None,
                "CantidadCli": None,
                "CantidadRealPro": None,
                "CantidadRealCli": None,
                "ImportePro": None,
                "ImporteCli": None,
                "IVAPro": None,
                "IVACli": None,
                "DtoPro": None,
                "DtoCli": None,
                "ConceptoPro": None,
                "ConceptoCli": None,
                "IdViaje": None,
                "Asignacion": 5,
                "idfacturaprovisional": None,
                "CabezaEXT": None,
                "ChoferEXT": None,
                "RemolqueEXT": None,
                "RemolqueEXT2": None,
                "DNIEXT": None,
                "FechaFinalizacion": fecha_hora,
                "FirmaCarga": None,
                "NombreFirmaCarga": None,
                "DNIFirmaCarga": None,
                "fechaFirmaCarga": fecha_hora,
                "FirmaDescarga": None,
                "NombreFirmaDescarga": None,
                "DNIFirmaDescarga": None,
                "fechaFirmaDescarga": fecha_hora,
                "IdVehiculoFacturable": None,
                "TipoServicio": "Servicio",
                "IdPasajero": None,
                "Camilla": 0,
                "Acompañante": 0,
                "Urgente": 0,
                "Ausente": 0,
                "TES": 1,
                "IdaYVuelta": None,
                "EsPortalCliente": 0,
                "FechaFirmaTransportista": fecha_hora,
                "FechaFirmaCliente": fecha_hora,
                "DNIFirmaCliente": None,
                "NombreFirmaCliente": None,
                "FirmaCliente": "Servicio",
                "fechaInicioPedido": fecha_hora,
                "Beneficio": None,
                "IdRutaCP": None,
                "LiquidadoChofer": None,
                "IdPuntoOrigen": None,
                "IdPuntoDestino": None,
                "IdEmpleado": None,
                "impEmpleado": None,
                "PorcEmpleado": None,
                "EmpLiquidado": 0,
                "lineasPedidoPrecio": [
                    {
                        "Id_pedido": idPedido,
                        "id_linea": 1,
                        "id_concepto_cliente": 1,
                        "cantidad_cli": "1.00000",
                        "cantidadRealCli": None,
                        "concepto_cli": None,
                        "id_um_cli": None,
                        "precio_cli": precio_cli,
                        "importe_cli": importe_cli,
                        "iva_cli": iva_cli,
                        "dto_cli": "0.00",
                        "id_concepto_pro": None,
                        "cantidad_pro": "0.00000",
                        "cantidadRealPro": None,
                        "concepto_pro": None,
                        "id_um_pro": None,
                        "precio_pro": "0.00000",
                        "importe_pro": "0.00",
                        "iva_pro": None,
                        "dto_pro": None,
                        "campo1": None,
                        "campo2": None,
                        "campo3": None,
                        "campo4": None,
                        "campo5": None,
                        "campo6": None,
                        "campo7": None,
                        "campo8": None,
                        "campo9": None,
                        "campo10": None,
                        "TextoLibrePro": None,
                        "TextoLibreCli": None,
                        "IdUsuario": idUsuario,
                        "IdMercanciaCli": None,
                        "IdMercanciaPro": None,
                        "Hijo": None
                    }
                ],
                "lineasPortacoche": [],
                "lineasCardes": [
                    {
                        "IdPedido": idPedido,
                        "Linea": 1,
                        "tipo": "C",
                        "Idpunto": idPunto_cargador,
                        "IdLugar": idLugar_cargador,
                        "SitioManual": None,
                        "Fecha": fecha,
                        "Hora": None,
                        "Temperatura": "",
                        "Cantidad": "0.00000000",
                        "CantidadReal": "0.00000000",
                        "IdUnidadMedida": None,
                        "RefereCarDes": sale_name,
                        "IdMercancia": None,
                        "MercanciaManual": None,
                        "CambioPalets": None,
                        "PesoVolumen": peso_envio,
                        "Observaciones": None,
                        "Bultos": bultos,
                        "PaletEntrega": palletEntrega,
                        "PaletRecibidos": None,
                        "latitud": None,
                        "longitud": None,
                        "campo1": None,
                        "campo2": None,
                        "campo3": None,
                        "campo4": None,
                        "campo5": None,
                        "campo6": None,
                        "campo7": None,
                        "campo8": None,
                        "campo9": None,
                        "campo10": None,
                        "contadorcar": None,
                        "contadordescar": None,
                        "Enganche": None,
                        "PuntoIntermedio": None,
                        "FechaFinalizacionCarDes": None,
                        "LatitudFin": None,
                        "longitudFin": None,
                        "lineaoculto": 1,
                        "firma": None,
                        "DNIFirma": None,
                        "nombreFirma": None,
                        "enCargaDescarga": None,
                        "latitudEnCargaDescarga": None,
                        "longitudEnCargaDescarga": None,
                        "fechaEnCargaDescarga": None,
                        "cargadoDescargado": None,
                        "latitudCargadoDescargado": None,
                        "longitudCargadoDescargado": None,
                        "fechaCargadoDescargado": None,
                        "incidencias": None,
                        "cancelada": None,
                        "fechaCancelada": None,
                        "kilometros_previos": None,
                        "kilometros_siguientes": None
                    },
                    {
                        "IdPedido": idPedido,
                        "Linea": 2,
                        "tipo": "D",
                        "Idpunto": idPunto_dir_ent,
                        "IdLugar": idLugar_dir_ent,
                        "SitioManual": None,
                        "Fecha": fecha,
                        "Hora": None,
                        "Temperatura": "",
                        "Cantidad": "0.00000000",
                        "CantidadReal": "0.00000000",
                        "IdUnidadMedida": None,
                        "RefereCarDes": sale_name,
                        "IdMercancia": None,
                        "MercanciaManual": None,
                        "CambioPalets": None,
                        "PesoVolumen": peso_envio,
                        "Observaciones": None,
                        "Bultos": bultos,
                        "PaletEntrega": palletEntrega,
                        "PaletRecibidos": None,
                        "latitud": None,
                        "longitud": None,
                        "campo1": None,
                        "campo2": None,
                        "campo3": None,
                        "campo4": None,
                        "campo5": None,
                        "campo6": None,
                        "campo7": None,
                        "campo8": None,
                        "campo9": None,
                        "campo10": None,
                        "contadorcar": None,
                        "contadordescar": None,
                        "Enganche": None,
                        "PuntoIntermedio": None,
                        "FechaFinalizacionCarDes": None,
                        "LatitudFin": None,
                        "longitudFin": None,
                        "lineaoculto": 1,
                        "firma": None,
                        "DNIFirma": None,
                        "nombreFirma": None,
                        "enCargaDescarga": None,
                        "latitudEnCargaDescarga": None,
                        "longitudEnCargaDescarga": None,
                        "fechaEnCargaDescarga": None,
                        "cargadoDescargado": None,
                        "latitudCargadoDescargado": None,
                        "longitudCargadoDescargado": None,
                        "fechaCargadoDescargado": None,
                        "incidencias": None,
                        "cancelada": None,
                        "fechaCancelada": None,
                        "kilometros_previos": None,
                        "kilometros_siguientes": None
                    }
                ]
            }

            url = 'https://portal.kaleidotrans.com/api/GestionTrafico/Pedidos/modificar.php?licencia=' + licencia_code
            headers = {'Authorization': token_kaleidotrans}
            request = requests.put(url, data=json.dumps(values), headers=headers)
            response = request.json()
            return response

    @api.model
    def _post_pedidos(self, token_kaleidotrans):
        licencia_code = self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.licencia')
        hoy = datetime.now(timezone(self.env.user.tz))
        fecha_hora = hoy.strftime('%Y-%m-%d %H:%M:%S')
        fecha = hoy.strftime('%Y-%m-%d')
        bultos = self._get_bultos()
        if not bultos:
            bultos = 0
        palletEntrega = self._get_pallet_entrega()
        if not palletEntrega:
            palletEntrega = 0
        conductor = self._get_conductor(token_kaleidotrans)
        id_conductor_puntos = conductor.get("code", 200)
        if id_conductor_puntos != 200:
            response = {"error": "Revise NIF del Conductor (Conductores en KaleidoTrans).",
                        "code": 404}
            return response
        vehiculo = self._get_cabeza(token_kaleidotrans)
        id_vehiculo_puntos = vehiculo.get("code", 200)
        if id_vehiculo_puntos != 200:
            response = {"error": "Revise matrícula de Cabeza de vehículo (Vehículos en KaleidoTrans).",
                        "code": 404}
            return response
        remolque = self._get_remolque(token_kaleidotrans)
        id_remolque_puntos = remolque.get("code", 200)
        if id_remolque_puntos != 200:
            response = {"error": "Revise matrícula de Remolque de vehículo (Vehículos en KaleidoTrans).",
                        "code": 404}
            return response
        poblacion_dir_ent = self._get_poblaciones_dir_ent(token_kaleidotrans)
        sitio_dir_ent = self._get_sitios_dir_ent(token_kaleidotrans)
        poblacion_dir_ent_puntos = poblacion_dir_ent.get("code", 200)
        sitio_dir_ent_sitios = sitio_dir_ent.get("code", 200)
        if poblacion_dir_ent_puntos != 200:
            response = {"error": "Revise Cod. Postal de Población de entrega del cliente (Poblaciones en KaleidoTrans).",
                        "code": 404}
            return response
        if sitio_dir_ent_sitios != 200:
            response = {"error": "Revise CIF de entrega del cliente (Sitios en KaleidoTrans).",
                        "code": 404}
            return response
        id_conductor = conductor['choferes'][0]['IdChofer']
        id_vehiculo = vehiculo['vehiculos'][0]['IdVehiculo']
        id_remolque = remolque['vehiculos'][0]['IdVehiculo']
        idPunto_dir_ent = poblacion_dir_ent['puntos'][0]['IdPunto']
        idLugar_dir_ent = sitio_dir_ent['sitios'][0]['IdLugar']
        poblacion_cargador = self._get_poblaciones_cargador(token_kaleidotrans)
        sitio_cargador = self._get_sitios_cargador(token_kaleidotrans)
        poblacion_cargador_puntos = poblacion_cargador.get("code", 200)
        sitio_cargador_sitios = sitio_cargador.get("code", 200)
        if poblacion_cargador_puntos != 200:
            response = {"error": "Revise Cod. Postal de Población del cargador (Poblaciones en KaleidoTrans).",
                        "code": 404}
            return response
        if sitio_cargador_sitios != 200:
            response = {"error": "Revise CIF del cargador.",
                        "code": 404}
            return response
        idPunto_cargador = poblacion_cargador['puntos'][0]['IdPunto']
        idLugar_cargador = sitio_cargador['sitios'][0]['IdLugar']
        sale_name = self.name
        idUsuario = int(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.idusuario'))
        idCliente = int(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.idcliente'))
        precio_cli = float(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.precio_cli'))
        iva_cli = float(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.iva_cli'))
        importe_cli = float(self.env['ir.config_parameter'].sudo().get_param('kaleidotrans.importe_cli'))
        peso_envio = self.shipping_weight
        values = {'FechaCreacion': fecha,
                  'estadoPedido': 'Servicio',
                  'IdFactura': None,
                  'IdFacturaPro': None,
                  'IdCliente': idCliente,
                  'referencia': sale_name,
                  'referencia2': None,
                  'IdMercancia': None,
                  'IdRutaTipo': None,
                  'IdGrupoAlbaran': None,
                  'IdEstado': None,
                  'IdAgenda': None,
                  'IdVehiculo': id_vehiculo,
                  'IdRemolque': id_remolque,
                  'IdRemolque2': None,
                  'IdChofer': id_conductor,
                  'IdChofer2': None,
                  'IdProveedor': None,
                  'KmCarga': None,
                  'KmVacio': None,
                  'IdPuntoIntermedio': None,
                  'Campo1': None,
                  'Campo2': None,
                  'Campo3': None,
                  'Campo4': None,
                  'Campo5': None,
                  'Campo6': None,
                  'Campo7': None,
                  'Campo8': None,
                  'Campo9': None,
                  'Campo10': None,
                  'Campo11': None,
                  'Campo12': None,
                  'Campo13': None,
                  'Campo14': None,
                  'Campo15': None,
                  'Campo16': None,
                  'Campo17': None,
                  'Campo18': None,
                  'Campo19': None,
                  'Campo20': None,
                  'VehiculoRemolque': None,
                  'Fecha_Inicio': fecha,
                  'Fecha_Fin': fecha,
                  'Hora_Inicio': None,
                  'Hora_Fin': None,
                  'observacion': None,
                  'observacion2': None,
                  'nota': None,
                  'infoadic_mercancia': None,
                  'infoadic_lugarcarga': None,
                  'infoadic_lugardescarga': None,
                  'incidencia': None,
                  'Kms': None,
                  'Origen': None,
                  'Fin': None,
                  'LugarOrigen': None,
                  'LugarFin': None,
                  'IdTarifa': None,
                  'IdZonaOrigen': None,
                  'IdZonaDestino': None,
                  'IdUsuario': 1,
                  'PrecioPro': None,
                  'PrecioCli': None,
                  'IdConceptoPro': None,
                  'IdConceptoCli': None,
                  'IdUMPro': None,
                  'IdUMCli': None,
                  'CantidadPro': None,
                  'CantidadCli': None,
                  'CantidadRealPro': None,
                  'CantidadRealCli': None,
                  'ImportePro': None,
                  'ImporteCli': None,
                  'IVAPro': None,
                  'IVACli': None,
                  'DtoPro': None,
                  'DtoCli': None,
                  'ConceptoPro': None,
                  'ConceptoCli': None,
                  'IdViaje': None,
                  'Asignacion': 5,
                  'idfacturaprovisional': None,
                  'CabezaEXT': None,
                  'ChoferEXT': None,
                  'RemolqueEXT': None,
                  'RemolqueEXT2': None,
                  'DNIEXT': None,
                  'FechaFinalizacion': fecha_hora,
                  'FirmaCarga': None,
                  'NombreFirmaCarga': None,
                  'DNIFirmaCarga': None,
                  'fechaFirmaCarga': fecha_hora,
                  'FirmaDescarga': None,
                  'NombreFirmaDescarga': None,
                  'DNIFirmaDescarga': None,
                  'fechaFirmaDescarga': fecha_hora,
                  'IdVehiculoFacturable': None,
                  'TipoServicio': 'Servicio',
                  'IdPasajero': None,
                  'Camilla': None,
                  'Acompañante': None,
                  'Urgente': None,
                  'Ausente': None,
                  'TES': 1,
                  'IdaYVuelta': None,
                  'FechaFirmaTransportista': fecha_hora,
                  'FechaFirmaCliente': fecha_hora,
                  'DNIFirmaCliente': None,
                  'NombreFirmaCliente': None,
                  'FirmaCliente': None,
                  'fechaInicioPedido': fecha_hora,
                  'Beneficio': None,
                  'IdRutaCP': None,
                  'LiquidadoChofer': None,
                  'IdPuntoOrigen': None,
                  'IdPuntoDestino': None,
                  'lineasPedidoPortacoches': [
                      {
                        'Linea': None,
                        'Marca': None,
                        'Modelo': None,
                        'Bastidor': None,
                        'Matricula': None,
                        'Peso': None,
                        'IdUsuario': None
                      }
                    ],
                  'lineasPedidoPrecio': [
                      {
                        'id_linea': 1,
                        'id_concepto_cliente': 1,
                        'cantidad_cli': 1,
                        'cantidadRealCli': None,
                        'concepto_cli': None,
                        'id_um_cli': None,
                        'precio_cli': precio_cli,
                        'Importe_cli': importe_cli,
                        'iva_cli': iva_cli,
                        'dto_cli': 0,
                        'id_concepto_pro': None,
                        'concepto_pro': None,
                        'cantidad_pro': None,
                        'cantidadRealPro': None,
                        'id_um_pro': None,
                        'precio_pro': None,
                        'importe_pro': None,
                        'iva_pro': None,
                        'dto_pro': None,
                        'IdMercanciaCli': None,
                        'IdMercanciaPro': None,
                        'Campo1': None,
                        'Campo2': None,
                        'Campo3': None,
                        'Campo4': None,
                        'Campo5': None,
                        'Campo6': None,
                        'Campo7': None,
                        'Campo8': None,
                        'Campo9': None,
                        'Campo10': None,
                        'TextoLibrePro': None,
                        'TextoLibreCli': None,
                        'IdUsuario': idUsuario
                      }
                    ],
                  'lineasPedidoCardes': [
                      {
                        'Linea': 1,
                        'tipo': 'C',
                        'IdPunto': idPunto_cargador,
                        'IdLugar': idLugar_cargador,
                        'SitioManual': None,
                        'Fecha': fecha,
                        'Hora': None,
                        'Temperatura': None,
                        'Cantidad': None,
                        'CantidadReal': None,
                        'IdUnidadMedida': None,
                        'RefereCarDes': sale_name,
                        'IdMercancia': None,
                        'MercanciaManual': None,
                        'CambioPalets': None,
                        'PesoVolumen': peso_envio,
                        'Observaciones': None,
                        'Bultos': bultos,
                        'PaletEntrega': palletEntrega,
                        'PaletRecibidos': None,
                        'latitud': None,
                        'longitud': None,
                        'Campo1': None,
                        'Campo2': None,
                        'Campo3': None,
                        'Campo4': None,
                        'Campo5': None,
                        'Campo6': None,
                        'Campo7': None,
                        'Campo8': None,
                        'Campo9': None,
                        'Campo10': None,
                        'contadorcar': None,
                        'contadordescar': None,
                        'Enganche': None,
                        'PuntoIntermedio': None,
                        'FechaFinalizacionCarDes': None,
                        'LatitudFin': None,
                        'longitudFin': None,
                        'lineaoculto': None,
                        'firma': None,
                        'DNIFirma': None,
                        'nombreFirma': None,
                        'enCargaDescarga': None,
                        'latitudEnCargaDescarga': None,
                        'longitudEnCargaDescarga': None,
                        'fechaEnCargaDescarga': None,
                        'cargadoDescargado': None,
                        'latitudCargadoDescargado': None,
                        'longitudCargadoDescargado': None,
                        'fechaCargadoDescargado': None,
                        'incidencias': None,
                        'cancelada': None,
                        'fechaCancelada': None,
                        'kilometros_previos': None,
                        'kilometros_siguientes': None
                      },
                      {
                        'Linea': 2,
                        'tipo': 'D',
                        'IdPunto': idPunto_dir_ent,
                        'IdLugar': idLugar_dir_ent,
                        'SitioManual': None,
                        'Fecha': fecha,
                        'Hora': None,
                        'Temperatura': None,
                        'Cantidad': None,
                        'CantidadReal': None,
                        'IdUnidadMedida': None,
                        'RefereCarDes': sale_name,
                        'IdMercancia': None,
                        'MercanciaManual': None,
                        'CambioPalets': None,
                        'PesoVolumen': peso_envio,
                        'Observaciones': None,
                        'Bultos': bultos,
                        'PaletEntrega': palletEntrega,
                        'PaletRecibidos': None,
                        'latitud': None,
                        'longitud': None,
                        'Campo1': None,
                        'Campo2': None,
                        'Campo3': None,
                        'Campo4': None,
                        'Campo5': None,
                        'Campo6': None,
                        'Campo7': None,
                        'Campo8': None,
                        'Campo9': None,
                        'Campo10': None,
                        'contadorcar': None,
                        'contadordescar': None,
                        'Enganche': None,
                        'PuntoIntermedio': None,
                        'FechaFinalizacionCarDes': None,
                        'LatitudFin': None,
                        'longitudFin': None,
                        'lineaoculto': None,
                        'firma': None,
                        'DNIFirma': None,
                        'nombreFirma': None,
                        'enCargaDescarga': None,
                        'latitudEnCargaDescarga': None,
                        'longitudEnCargaDescarga': None,
                        'fechaEnCargaDescarga': None,
                        'cargadoDescargado': None,
                        'latitudCargadoDescargado': None,
                        'longitudCargadoDescargado': None,
                        'fechaCargadoDescargado': None,
                        'incidencias': None,
                        'cancelada': None,
                        'fechaCancelada': None,
                        'kilometros_previos': None,
                        'kilometros_siguientes': None
                      }
                    ]
                  }
        url = 'https://portal.kaleidotrans.com/api/GestionTrafico/Pedidos/insertar.php?licencia='+licencia_code
        headers = {'Authorization': token_kaleidotrans}
        request = requests.post(url, data=json.dumps(values), headers=headers)
        response = request.json()
        return response
