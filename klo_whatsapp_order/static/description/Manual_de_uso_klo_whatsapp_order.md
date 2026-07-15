# Manual de Uso — KLO WhatsApp Order con IA

## 1. Descripción General

El módulo **klo_whatsapp_order** permite recibir pedidos de clientes por WhatsApp de forma automatizada usando inteligencia artificial. Los mensajes de los clientes se procesan con un proveedor de IA (Xiaomi MiMo V2.5 o OpenAI) y se convierten en borradores de pedidos de venta en Odoo.

**Canales de WhatsApp soportados:**
- **Meta Cloud API** (WhatsApp Business): API oficial, requiere cuenta de negocio
- **OpenWA** (Self-Hosted): Gateway open source, usa WhatsApp Web, gratuito

**Proveedores de IA soportados:**
- **Xiaomi MiMo V2.5** (recomendado): API compatible con OpenAI, coste reducido
- **OpenAI** (fallback): Modelos GPT-4o, GPT-4o-mini

---

## 2. Configuración Paso a Paso

### 2.1. INSTALACIÓN DE OPENWA (Recomendado)

OpenWA es un gateway de API WhatsApp auto-hospedado. **No necesitas cuenta de negocio de Facebook** ni verificación especial. Usa tu WhatsApp normal.

#### Paso 1: Instalar Docker (si no lo tienes)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

#### Paso 2: Clonar e instalar OpenWA

```bash
# Clonar el repositorio
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA

# Iniciar con Docker (desarrollo)
docker compose -f docker-compose.dev.yml up -d
```

#### Paso 3: Acceder al dashboard

1. Abrir el navegador: **http://localhost:2785**
2. Verás el dashboard de OpenWA
3. La primera vez se genera una API Key automáticamente
4. Copiar la API Key (aparece en los logs o en el dashboard)

#### Paso 4: Crear sesión de WhatsApp

1. En el dashboard, ir a **Sessions**
2. Hacer clic en **Create Session**
3. Introducir un nombre (ej: "mi-bot-odoo")
4. Guardar el **Session ID** que se genera

#### Paso 5: Autenticar WhatsApp

1. En la sesión creada, hacer clic en **Start**
2. Aparecerá un código QR
3. Abrir WhatsApp en tu teléfono
4. Ir a **Dispositivos vinculados** > **Vincular dispositivo**
5. Escanear el código QR
6. Esperar a que diga "Conectado"

#### Paso 6: Configurar webhook en OpenWA

1. En el dashboard, ir a **Webhooks** de la sesión
2. Hacer clic en **Add Webhook**
3. Introducir:
   - **URL**: `https://tu-dominio-odoo.com/webhook/openwa`
   - **Events**: Seleccionar `message.received`
   - **Secret**: Introducir un secreto (ej: `mi_secreto_hmac_123`)
4. Guardar

#### Paso 7: Verificar conexión

1. Enviar un mensaje de WhatsApp al número autenticado
2. Verificar en los logs de OpenWA que llega el mensaje
3. Verificar en Odoo que se procesa correctamente

---

### 2.2. CONFIGURACIÓN DE OPENWA EN ODOO

1. Ir a **Ventas** > **Ajustes**
2. Buscar **"Pedidos por WhatsApp con IA"**
3. En **"Canal de WhatsApp"**, seleccionar: **OpenWA (Self-Hosted)**
4. Configurar la sección **OpenWA**:

**Campo: "URL base OpenWA"**
- Por defecto: `http://localhost:2785`
- Si OpenWA está en otro servidor: `https://openwa.tudominio.com`

**Campo: "API Key OpenWA"**
- Pegar la API Key generada por OpenWA
- Formato: `owa_k1_xxxxxxxxxxxxxxxxxxxxxxxx`

**Campo: "Session ID de OpenWA"**
- Pegar el ID de la sesión creada
- Ejemplo: `8f3c2b1a-9d4e-4c7a-8b2f-1e6d5a4c3b2a`

**Campo: "Secret HMAC (webhook OpenWA)"**
- Introducir el mismo secreto configurado en el webhook de OpenWA
- Este secreto verifica que los mensajes vienen de OpenWA

5. Hacer clic en **"Guardar"**

---

### 2.3. CONFIGURACIÓN DE META CLOUD API (Alternativa)

Usa esta opción si prefieres la API oficial de WhatsApp Business.

#### Paso 1: Crear aplicación en Meta

1. Ir a: **https://developers.facebook.com**
2. Iniciar sesión con tu cuenta de Facebook
3. Ir a **"My Apps"** > **"Create App"**
4. Seleccionar **"Business"** como tipo
5. Crear la aplicación

#### Paso 2: Configurar WhatsApp Business

1. En la aplicación, ir a **"WhatsApp"**
2. Hacer clic en **"Start Using the WhatsApp Business API"**
3. Seleccionar o crear una cuenta de negocios
4. Agregar un número de teléfono
5. Verificar el número

#### Paso 3: Obtener credenciales

1. Ir a **"WhatsApp"** > **"API Setup"**
2. Copiar:
   - **Phone Number ID**
   - **Permanent Access Token** (en System Users)

#### Paso 4: Configurar en Odoo

1. En **"Canal de WhatsApp"**, seleccionar: **Meta Cloud API**
2. Configurar:
   - **Token de verificación webhook**: Token personalizado
   - **Access Token Meta**: Token permanente copiado
   - **Phone Number ID**: ID del teléfono copiado
   - **Versión API Meta**: `v19.0`

#### Paso 5: Configurar webhook en Meta

1. En Meta Developers, ir a **"WhatsApp"** > **"Configuration"**
2. Webhook > **"Edit"**
3. Introducir:
   - **Callback URL**: `https://tu-dominio-odoo.com/webhook/whatsapp`
   - **Verify Token**: El mismo token configurado en Odoo
4. Guardar y suscribirse a `messages`

---

### 2.4. CONFIGURACIÓN DEL PROVEEDOR DE IA (MiMo V2.5)

#### Paso 1: Crear cuenta en Xiaomi MiMo

1. Ir a: **https://platform.xiaomimimo.com**
2. Registrarse con cuenta Xiaomi
3. Al registrarte recibes **$2 de crédito gratis**

#### Paso 2: Obtener API Key

1. Ir a **Console** > **API Keys**
2. Crear nueva API Key (formato `sk-xxxxx`)
3. Copiar y guardar de forma segura

#### Paso 3: Configurar en Odoo

1. En **"Xiaomi MiMo"**:
   - **Usar Xiaomi MiMo**: ✅ Activado
   - **API Key MiMo**: Pegar la API Key
   - **Modelo MiMo**: `mimo-v2.5`
   - **URL base API MiMo**: `https://api.xiaomimimo.com/v1`

2. En **"OpenAI (fallback)"** (opcional):
   - Solo si MiMo no está disponible
   - Introducir API Key de OpenAI

---

## 3. Comparativa de Proveedores

### Canales de WhatsApp

| Característica | Meta Cloud API | OpenWA |
|---|---|---|
| Coste | Gratuito (con límites) | Gratuito |
| Cuenta de negocio | Sí requerida | No necesaria |
| Verificación Facebook | Sí | No |
| Hospedaje | Cloud de Meta | Self-hosted (Docker) |
| API | Oficial WhatsApp Business | Compatible WhatsApp Web |
| Multi-sesión | No | Sí |
| Webhooks | Sí | Sí |
| Dashboard | No | Sí |

### Proveedores de IA

| Modelo | Coste (1M tokens) | Velocidad | Calidad |
|---|---|---|---|
| MiMo V2.5 | $0.14 / $0.28 | Rápida | Muy buena |
| MiMo V2.5 Pro | $0.14 / $0.28 | Media | Excelente |
| MiMo V2.5 Flash | $0.05 / $0.10 | Muy rápida | Buena |
| GPT-4o | $2.50 / $10.00 | Rápida | Excelente |
| GPT-4o Mini | $0.15 / $0.60 | Muy rápida | Buena |

**Recomendación:** OpenWA + MiMo V2.5 = **100% gratuito + bajo coste de IA**

---

## 4. Configuración de Contactos

### Habilitar un contacto

1. Ir a **Contactos** > Seleccionar contacto
2. Pestaña **"Ventas y Compra"**:
   - **Teléfono WhatsApp**: Formato internacional sin `+` (ej: `34612345678`)
   - **Pedidos por WhatsApp activos**: ✅ Marcar

### Formato de números

- **Para OpenWA**: Solo dígitos, sin `+` ni espacios (ej: `34612345678`)
- **Para Meta**: Formato E.164 con `+` (ej: `+34612345678`)
- El módulo detecta automáticamente el canal y ajusta el formato

---

## 5. Flujo de Pedidos

```
1. CLIENTE ENVÍA MENSAJE
   "Hola, quiero 20 cajas de producto A"
        ↓
2. SISTEMA RECIBE Y AUTENTICA
   - Verifica número en res.partner
   - Comprueba que esté habilitado
        ↓
3. IA INTERPRETA EL MENSAJE
   - Extrae productos y cantidades
   - Identifica intención
        ↓
4. SE CREA PEDIDO BORRADOR
   - Sale.order con líneas
   - Precios según tarifa
        ↓
5. CLIENTE CONFIRMA
   "¿Confirmas? SÍ/NO"
        ↓
6. PEDIDO SE CONFIRMA
   - Se crea la venta en Odoo
```

---

## 6. Solución de Problemas

### OpenWA

**Error: "OpenWA no configurada"**
- Verificar que la API Key esté introducida
- Comprobar que la URL base sea correcta

**Error: "Firma HMAC inválida"**
- El Secret HMAC no coincide
- Verificar que sea el mismo en OpenWA y en Odoo

**Mensajes no llegan a Odoo**
- Verificar que el webhook esté configurado en OpenWA
- Comprobar que la URL del webhook sea accesible
- Revisar logs de OpenWA

**QR no aparece**
- Verificar que Docker esté corriendo
- Revisar logs: `docker logs openwa-api`

### Meta Cloud API

**Error: "Meta API no configurada"**
- Verificar Access Token y Phone Number ID
- Comprobar que el webhook esté verificado

### IA

**Error: "API Key de MiMo no configurada"**
- Ir a Ajustes > Xiaomi MiMo > Introducir API Key

**Error: "Límite de tokens alcanzado"**
- Revisar límites en Ajustes > Control de gasto
- Aumentar límites o desactivarlos (0 = sin límite)

---

## 7. Comandos Útiles

### Gestionar OpenWA

```bash
# Ver logs de OpenWA
docker logs -f openwa-api

# Reiniciar OpenWA
docker compose -f docker-compose.dev.yml restart

# Parar OpenWA
docker compose -f docker-compose.dev.yml down

# Actualizar OpenWA
cd OpenWA
git pull
docker compose -f docker-compose.dev.yml up -d --build
```

### Actualizar módulo Odoo

```bash
cd /opt/odoo18_desarrollo/odoo
/home/manolo/.local/bin/uv run /opt/odoo18_desarrollo/uv/.venv/bin/python3 \
    /opt/odoo18_desarrollo/odoo/odoo-bin \
    -c /opt/odoo18_desarrollo/config/odoo.conf \
    -d garridomontero_dev -u klo_whatsapp_order --stop-after-init
```

---

## 8. Soporte

**KLO Ingeniería Informática S.L.L.**
- Web: [https://www.klo.es](https://www.klo.es)

**Documentación OpenWA:**
- GitHub: [https://github.com/rmyndharis/OpenWA](https://github.com/rmyndharis/OpenWA)

**Xiaomi MiMo:**
- Plataforma: [https://platform.xiaomimimo.com](https://platform.xiaomimimo.com)

---

*Documento actualizado: Julio 2026*
*Versión del módulo: 18.0.3.0.0*
