# Manual de Uso — KLO WhatsApp Order con IA

## 1. Descripción General

El módulo **klo_whatsapp_order** permite recibir pedidos de clientes por WhatsApp de forma automatizada usando inteligencia artificial. Los mensajes de los clientes se procesan con un proveedor de IA (Xiaomi MiMo V2.5 o OpenAI) y se convierten en borradores de pedidos de venta en Odoo.

**Proveedores de IA soportados:**
- **Xiaomi MiMo V2.5** (recomendado): API compatible con OpenAI, coste muy reducido
- **OpenAI** (fallback): Modelos GPT-4o, GPT-4o-mini

---

## 2. Configuración Paso a Paso

### 2.1. OPCIÓN A: Configurar Xiaomi MiMo V2.5 (Recomendado)

#### Paso 1: Crear cuenta en Xiaomi MiMo

1. Abrir el navegador y ir a: **https://platform.xiaomimimo.com**
2. Hacer clic en **"Sign Up"** o **"Log In"**
3. Si no tienes cuenta Xiaomi:
   - Hacer clic en **"Create Account"**
   - Introducir email o número de teléfono
   - Crear contraseña
   - Verificar la cuenta por email/SMS
4. Si ya tienes cuenta Xiaomi:
   - Iniciar sesión con tus credenciales
5. Aceptar los términos y condiciones

**Nota:** Al registrarte recibirás **$2 de crédito de prueba** automáticamente.

#### Paso 2: Obtener API Key de MiMo

1. Una vez dentro de la plataforma, ir a **"Console"** (consola)
2. En el menú lateral, buscar **"API Keys"**
3. Hacer clic en **"Create API Key"** o **"Generate New Key"**
4. Introducir un nombre descriptivo (ej: "WhatsApp Odoo")
5. Hacer clic en **"Create"** o **"Generate"**
6. **IMPORTANTE:** Copiar inmediatamente la API Key (formato `sk-xxxxx`)
   - La clave solo se muestra una vez
   - Guardarla en un lugar seguro
7. Hacer clic en **"Done"** o **"Close"**

#### Paso 3: Verificar créditos

1. En la consola, ir a **"Balance"** o **"Billing"**
2. Comprobar que aparece el crédito de $2
3. Los créditos se gastan automáticamente al usar la API

#### Paso 4: Configurar en Odoo

1. Abrir Odoo en el navegador
2. Ir a **Ventas** > **Ajustes** (icono de engranaje)
3. Buscar la sección **"Pedidos por WhatsApp con IA"**
4. Dentro de esa sección, buscar **"Xiaomi MiMo"**
5. Configurar cada campo:

**Campo: "Usar Xiaomi MiMo"**
- Marcar la casilla ✅
- Esto activa MiMo como proveedor principal

**Campo: "API Key MiMo"**
- Pegar la API Key copiada en el Paso 2
- Formato: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- Esta clave es secreta, no compartirla

**Campo: "Modelo MiMo"**
- Dejar por defecto: `mimo-v2.5`
- Opciones disponibles:
  - `mimo-v2.5` → Multimodal (recomendado para la mayoría de casos)
  - `mimo-v2.5-pro` → Razonamiento avanzado (más lento pero más preciso)
  - `mimo-v2-flash` → Ultra-rápido (para mensajes simples)

**Campo: "URL base API MiMo"**
- Dejar por defecto: `https://api.xiaomimimo.com/v1`
- No cambiarlo a menos que se sepa lo que se hace

6. Hacer clic en **"Guardar"** (botón azul arriba)

#### Paso 5: Probar la conexión

1. Enviar un mensaje de prueba por WhatsApp al número configurado
2. Ejemplo: "Hola, quiero hacer un pedido"
3. Verificar que se recibe respuesta automática
4. Si hay error, revisar la API Key en los ajustes

---

### 2.2. OPCIÓN B: Configurar OpenAI (Fallback)

Usar esta opción solo si no puedes usar MiMo o necesitas un proveedor alternativo.

#### Paso 1: Crear cuenta en OpenAI

1. Abrir el navegador y ir a: **https://platform.openai.com**
2. Hacer clic en **"Sign Up"**
3. Opciones de registro:
   - Con Google
   - Con Microsoft
   - Con email
4. Completar el registro y verificar la cuenta
5. Introducir datos de facturación (requerido aunque haya créditos gratis)

#### Paso 2: Obtener API Key de OpenAI

1. Una vez dentro, ir a **"API Keys"** en el menú lateral
2. Hacer clic en **"Create new secret key"**
3. Introducir un nombre (ej: "WhatsApp Odoo")
4. Hacer clic en **"Create secret key"**
5. **IMPORTANTE:** Copiar inmediatamente la clave (formato `sk-xxxxxxxxxxxx`)
   - La clave solo se muestra una vez
   - Guardarla en un lugar seguro
6. Hacer clic en **"Done"**

#### Paso 3: Configurar créditos

1. En el menú, ir a **"Settings"** > **"Billing"**
2. Opciones:
   - **Free tier**: Créditos limitados ($5 al inicio)
   - **Pay-as-you-go**: Recargar saldo según necesidad
3. Para empezar, el free tier es suficiente para pruebas

#### Paso 4: Configurar en Odoo

1. Abrir Odoo en el navegador
2. Ir a **Ventas** > **Ajustes**
3. Buscar **"Pedidos por WhatsApp con IA"**
4. **IMPORTANTE:** Primero desactivar MiMo:
   - Buscar **"Xiaomi MiMo"**
   - Desmarcar **"Usar Xiaomi MiMo"** ❌
5. Buscar **"OpenAI (fallback)"**
6. Configurar cada campo:

**Campo: "API Key OpenAI (fallback)"**
- Pegar la API Key copiada en el Paso 2
- Formato: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Campo: "Modelo OpenAI (fallback)"**
- Opciones:
  - `gpt-4o` → Más capaz (recomendado)
  - `gpt-4o-mini` → Más barato
  - `gpt-4-turbo` → Más rápido

7. Hacer clic en **"Guardar"**

---

### 2.3. Configurar WhatsApp Business API (Meta)

Esta configuración es necesaria independientemente del proveedor de IA.

#### Paso 1: Crear aplicación en Meta

1. Ir a: **https://developers.facebook.com**
2. Iniciar sesión con tu cuenta de Facebook
3. Ir a **"My Apps"** > **"Create App"**
4. Seleccionar **"Business"** como tipo de aplicación
5. Introducir nombre de la aplicación (ej: "WhatsApp Odoo")
6. Crear la aplicación

#### Paso 2: Configurar WhatsApp Business

1. En la nueva aplicación, ir a **"WhatsApp"** en el menú
2. Hacer clic en **"Start Using the WhatsApp Business API"**
3. Seleccionar o crear una cuenta de negocios
4. Agregar un número de teléfono nuevo o existente
5. Verificar el número por SMS o llamada

#### Paso 3: Obtener credenciales

1. Ir a **"WhatsApp"** > **"API Setup"**
2. Copiar los siguientes valores:

**Phone Number ID:**
- Se encuentra en "Phone numbers"
- Copiar el ID numérico (ej: `1234567890`)

**Permanent Access Token:**
1. Ir a **"System Users"**
2. Seleccionar o crear un usuario del sistema
3. Hacer clic en **"Generate new token"**
4. Seleccionar los permisos:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. Copiar el token (formato: `EAAxxxxx`)

#### Paso 4: Configurar en Odoo

1. Ir a **Ventas** > **Ajustes**
2. Buscar **"Meta Cloud API"**
3. Configurar:

**Campo: "Token de verificación webhook"**
- Introducir un token personalizado (ej: `mi_token_secreto_123`)
- Este token se usará para verificar el webhook
- Recordar este valor para el siguiente paso

**Campo: "Access Token Meta (permanente)"**
- Pegar el Permanent Access Token copiado

**Campo: "Phone Number ID (Meta)"**
- Pegar el Phone Number ID copiado

**Campo: "Versión API Meta"**
- Dejar por defecto: `v19.0`

4. Hacer clic en **"Guardar"**

#### Paso 5: Configurar Webhook en Meta

1. En Meta Developers, ir a **"WhatsApp"** > **"Configuration"**
2. Buscar **"Webhook"**
3. Hacer clic en **"Edit"** o **"Configure"**
4. Introducir:

**Callback URL:**
```
https://tu-dominio-odoo.com/webhook/whatsapp
```
- Reemplazar `tu-dominio-odoo.com` con tu dominio real
- Debe ser HTTPS (obligatorio para Meta)

**Verify Token:**
- Introducir el mismo token configurado en Odoo (Paso 4)
- Ejemplo: `mi_token_secreto_123`

5. Hacer clic en **"Verify and Save"**
6. Suscribirse a los eventos:
   - Marcar **"messages"**
   - Guardar

#### Paso 6: Probar el webhook

1. En la configuración del webhook, hacer clic en **"Test"**
2. Debería aparecer "Verified" si está correcto
3. Si falla, verificar:
   - La URL sea accesible desde internet
   - El token coincida con el de Odoo
   - El certificado SSL esté instalado

---

## 3. Configuración de Contactos

### 3.1. Habilitar un contacto para WhatsApp

1. Ir a **Contactos**
2. Seleccionar o crear un contacto
3. Ir a la pestaña **"Ventas y Compra"**
4. Buscar los campos de WhatsApp:

**Campo: "Teléfono WhatsApp"**
- Introducir el número en formato internacional
- Ejemplo: `+34612345678` (España)
- Ejemplo: `+521234567890` (México)
- IMPORTANTE: Incluir el código de país

**Campo: "Pedidos por WhatsApp activos"**
- Marcar la casilla ✅ para habilitar
- Solo los contactos habilitados pueden hacer pedidos

5. Guardar el contacto

### 3.2. Verificar configuración

1. Enviar un mensaje de WhatsApp al número configurado en Meta
2. Debería llegar una respuesta automática
3. Si no llega respuesta, revisar:
   - Que el contacto esté habilitado
   - Que el número coincida exactamente
   - Los logs en **Ventas > WhatsApp IA > Mensajes**

---

## 4. Flujo de Pedidos

### 4.1. Proceso completo

```
┌─────────────────────────────────────────────────────────────┐
│  1. CLIENTE ENVÍA MENSAJE POR WHATSAPP                      │
│     "Hola, quiero 20 cajas de producto A"                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. SISTEMA RECIBE Y AUTENTICA                              │
│     - Verifica número en res.partner                         │
│     - Comprueba que esté habilitado                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. IA INTERPRETA EL MENSAJE                                │
│     - Extrae productos y cantidades                          │
│     - Identifica intención (pedido, consulta, cancelación)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SE CREA/ACTUALIZA PEDIDO BORRADOR                       │
│     - Sale.order con líneas de producto                      │
│     - Precios según tarifa del cliente                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. CLIENTE RECIBE RESUMEN Y CONFIRMA                       │
│     "He preparado: 20x Producto A = 100€. ¿Confirmas?"     │
│     Cliente responde "SÍ" o "NO"                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. PEDIDO SE CONFIRMA (automático o manual)                │
│     - Se crea la venta en Odoo                               │
│     - Se notifica al cliente                                 │
└─────────────────────────────────────────────────────────────┘
```

### 4.2. Ejemplos de mensajes

**Realizar un pedido:**
```
Cliente: "Buenos días, necesito 30 cajas del producto XYZ y 15 del ABC"
Sistema: "He preparado tu pedido:
- 30 x Producto XYZ: 150€
- 15 x Producto ABC: 75€
Total: 225€
¿Confirmas? Responde SÍ para confirmar o NO para cancelar."
```

**Consultar precio:**
```
Cliente: "¿Cuánto cuesta el producto XYZ?"
Sistema: "El precio del Producto XYZ es 5€ por caja.
¿Te gustaría hacer un pedido?"
```

**Cancelar pedido:**
```
Cliente: "Cancelo el pedido anterior"
Sistema: "Pedido cancelado correctamente. ¡Hasta pronto!"
```

---

## 5. Monitoreo y Administración

### 5.1. Sesiones de WhatsApp

**Ubicación:** Ventas > WhatsApp IA > Sesiones

Información disponible:
- **Cliente**: Contacto asociado
- **Número WhatsApp**: Origen de la conversación
- **Estado**: Abierta / Esperando confirmación / Completada / Cancelada
- **Nº mensajes**: Total de mensajes intercambiados
- **Tokens totales**: Consumo de IA en la sesión
- **Pedido borrador**: Venta generada

### 5.2. Mensajes

**Ubicación:** Ventas > WhatsApp IA > Mensajes

Información disponible:
- **Sesión**: Conversación asociada
- **Dirección**: Entrante (cliente) / Saliente (sistema)
- **Cuerpo**: Texto del mensaje
- **ID mensaje Meta**: Identificador único
- **Error de procesamiento**: Si hubo algún problema

### 5.3. Uso de IA

**Ubicación:** Ventas > WhatsApp IA > Uso IA

Información disponible:
- **Sesión**: Conversación asociada
- **Modelo IA**: Modelo utilizado (mimo-v2.5, gpt-4o, etc.)
- **Tokens de entrada**: Tokens consumidos por el prompt
- **Tokens de salida**: Tokens consumidos por la respuesta
- **Coste estimado (€)**: Coste calculado automáticamente

---

## 6. Modelos de IA Disponibles

### 6.1. Xiaomi MiMo V2.5

| Modelo | Uso ideal | Ventajas | Coste (1M tokens) |
|---|---|---|---|
| `mimo-v2.5` | Uso general | Multimodal, buen balance | $0.14 input / $0.28 output |
| `mimo-v2.5-pro` | Análisis complejo | Mayor precisión | $0.14 input / $0.28 output |
| `mimo-v2-flash` | Mensajes simples | Ultra-rápido | $0.05 input / $0.10 output |

**Recomendación:** Usar `mimo-v2.5` para la mayoría de casos.

### 6.2. OpenAI (Fallback)

| Modelo | Uso ideal | Ventajas | Coste (1M tokens) |
|---|---|---|---|
| `gpt-4o` | Uso general | Muy capaz | $2.50 input / $10.00 output |
| `gpt-4o-mini` | Uso ligero | Más barato | $0.15 input / $0.60 output |
| `gpt-4-turbo` | Velocidad | Rápido | $10.00 input / $30.00 output |

**Comparativa:** MiMo es ~18x más barato que GPT-4o.

---

## 7. Control de Gasto

### 7.1. Configurar límites

1. Ir a **Ventas > Ajustes > Pedidos por WhatsApp con IA**
2. Buscar **"Control de gasto de IA"**
3. Configurar:

**Límite diario de tokens:**
- Valor `0` = sin límite
- Ejemplo: `100000` = máximo 100,000 tokens por día
- Se reinicia automáticamente cada día

**Límite mensual de coste IA (€):**
- Valor `0` = sin límite
- Ejemplo: `10` = máximo 10€ por mes
- Se reinicia el primer día de cada mes

4. Guardar los cambios

### 7.2. Monitorear consumo

1. Ir a **Ventas > WhatsApp IA > Uso IA**
2. Usar filtros para ver consumo por:
   - Fecha
   - Sesión
   - Modelo
3. El coste se calcula automáticamente según el modelo usado

---

## 8. Solución de Problemas

### 8.1. Errores de configuración

**Error: "La API Key de Xiaomi MiMo no está configurada"**
- Causa: Falta la API Key de MiMo
- Solución: Ir a Ajustes > Xiaomi MiMo > Introducir API Key

**Error: "La API Key de OpenAI no está configurada"**
- Causa: MiMo desactivado y falta API Key de OpenAI
- Solución: Activar MiMo o configurar OpenAI

**Error: "Meta API no configurada (token o phone_id ausentes)"**
- Causa: Faltan credenciales de Meta
- Solución: Ir a Ajustes > Meta Cloud API > Completar campos

### 8.2. Errores de mensajes

**Error: "Tu número no está autorizado"**
- Causa: El contacto no está habilitado
- Solución: Ir al contacto > Marcar "Pedidos por WhatsApp activos"

**Error: "Ha ocurrido un error al procesar tu mensaje"**
- Causa: Error en la IA o timeout
- Solución: Revisar logs en WhatsApp IA > Mensajes

**Error: "Límite diario de tokens alcanzado"**
- Causa: Se superó el límite configurado
- Solución: Aumentar límites o esperar al día siguiente

### 8.3. Errores de webhook

**Webhook no verifica con Meta**
- Causas posibles:
  - URL no accesible desde internet
  - Token no coincide
  - Certificado SSL no válido
- Soluciones:
  - Verificar que la URL sea HTTPS
  - Comprobar el token en Ajustes
  - Instalar certificado SSL válido

**Mensajes no llegan a Odoo**
- Causas posibles:
  - Webhook no configurado
  - Evento "messages" no suscrito
  - Error en el endpoint
- Soluciones:
  - Verificar webhook en Meta Developers
  - Revisar logs de Odoo
  - Comprobar suscripción a eventos

---

## 9. Consejos y Buenas Prácticas

### 9.1. Uso de la IA

- **Sé específico**: "Quiero 20 cajas de Producto A" mejor que "quiero cosas"
- **Usa nombres claros**: Si el cliente conoce los nombres de producto, mejor
- **Confirma antes de cancelar**: Evitar cancelaciones accidentales

### 9.2. Gestión de contactos

- **Mantener números actualizados**: Verificar formatos internacionales
- **Un contacto por cliente**: Evitar duplicados
- **Deshabilitar contactos inactivos**: Reducir uso innecesario de IA

### 9.3. Optimización de costes

- **Usar mimo-v2-flash** para mensajes simples
- **Configurar límites** según el uso esperado
- **Monitorear consumo** periódicamente
- **Ajustar límites** según necesidades reales

---

## 10. Soporte y Contacto

Para problemas o consultas:

**KLO Ingeniería Informática S.L.L.**
- Web: [https://www.klo.es](https://www.klo.es)
- Email: soporte@klo.es

**Soporte técnico de Xiaomi MiMo:**
- Documentación: [https://mimo.mi.com/docs](https://mimo.mi.com/docs)
- Plataforma: [https://platform.xiaomimimo.com](https://platform.xiaomimimo.com)

---

*Documento actualizado: Julio 2026*
*Versión del módulo: 18.0.2.0.0*
*Última revisión: 10 de julio de 2026*
