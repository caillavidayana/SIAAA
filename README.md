# Sistema Integrado Administrativo (SIA) - EMI

Sistema integral de gestión de trámites administrativos, soporte técnico, compras por caja chica y mantenimiento preventivo/correctivo para la Escuela Militar de Ingeniería (EMI).

Incluye **Asistente Virtual Inteligente (IA Local)** con reconocimiento y síntesis de voz, sugerencias dinámicas por rol y soporte para el modelo institucional `sigta-ai` mediante Ollama.

---

## 🚀 Inicio Rápido para el Equipo

La base de datos SQLite (`backend/db.sqlite3`) ya viene incluida y configurada con todos los roles, usuarios y permisos necesarios. No requiere migraciones ni configuraciones complejas iniciales.

### 1. Levantar el Backend (Django)

Abre una terminal en la carpeta `backend`:

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py runserver 127.0.0.1:8000
```

> **Nota:** El backend escuchará en `http://127.0.0.1:8000/`.

---

### 2. Levantar el Frontend (Vue 3 + Vite)

Abre otra terminal en la carpeta `frontend`:

```bash
cd frontend
npm install
npm run dev
```

> **Listo:** Abre tu navegador en **`http://localhost:5173`**. Vite tiene un proxy configurado para redirigir automáticamente todas las peticiones `/api` al backend Django.

---

## 🤖 Asistente Virtual Inteligente (SIA-AI)

El sistema cuenta con un Asistente Virtual de IA integrado globalmente:
- **Identidad EMI**: Paleta institucional (Azul Marino y Dorado EMI).
- **Sugerencias Dinámicas por Rol**: Píldoras de preguntas frecuentes adaptadas al perfil activo (Técnico, Auxiliar, Jefe UTIC, DAF, Tesorería, Solicitante, etc.).
- **Modo Llamada Manos Libres**: Conversación bidireccional continua por voz sin necesidad de pulsar botones repetidamente.
- **Tolerante a Contingencias**: Si Ollama no está en ejecución, el asistente entrega respuestas informativas de contingencia sin interrumpir el funcionamiento del sistema.

### Para habilitar el modelo de IA local con Ollama (Opcional):
```powershell
ollama pull llama3.2:3b
ollama create sigta-ai -f .\Modelfile
ollama run sigta-ai
```

---

## 👥 Credenciales de Prueba (Entorno de Desarrollo)

> **Todas las cuentas usan la misma contraseña: `Hola123*`**

| Rol | Correo Electrónico | Contraseña | Ruta en el Sistema |
|:---|:---|:---|:---|
| **Superusuario** | `superuser@emi.edu.bo` | `Hola123*` | `/superuser/dashboard` |
| **Director / Admin** | `admin@emi.edu.bo` | `Hola123*` | `/admin/dashboard` |
| **Jefe UTIC** | `jefe.utic@emi.edu.bo` | `Hola123*` | `/jefe-utic/dashboard` |
| **Jefe Mantenimiento** | `servicios.generales@emi.edu.bo` | `Hola123*` | `/servicios-generales/dashboard` |
| **Especialista Soporte** | `especialista@emi.edu.bo` | `Hola123*` | `/especialista/dashboard` |
| **Auxiliar Mantenimiento** | `auxiliar.sg@emi.edu.bo` | `Hola123*` | `/auxiliar-servicios-generales/dashboard` |
| **DAF (Finanzas)** | `daf@emi.edu.bo` | `Hola123*` | `/daf/dashboard` |
| **Técnico Tesorería** | `tesoreria@emi.edu.bo` | `Hola123*` | `/tesoreria/dashboard` |
| **Almacén y Compras** | `almacen@emi.edu.bo` | `Hola123*` | `/almacen/dashboard` |
| **Usuario Solicitante** | `solicitante@emi.edu.bo` | `Hola123*` | `/usuario/dashboard` |

---

## 📁 Estructura del Repositorio

```text
├── backend/                  # API REST Django, modelos, vistas y asistente
│   ├── asistente/            # Lógica del asistente, servicios y contexto multi-rol
│   ├── config/               # Configuración WSGI, settings y URLs
│   ├── db.sqlite3            # Base de datos pre-sembrada con datos de prueba
│   └── requirements.txt      # Dependencias Python
├── frontend/                 # Aplicación SPA en Vue 3 con Vite
│   ├── src/                  # Vistas, componentes y router
│   │   └── components/       # AsistenteChat.vue, modales y barras
│   └── vite.config.js        # Configuración de proxy y rutas
├── docs/                     # Diagramas BPMN y documentación técnica
├── deploy/                   # Configuraciones de despliegue y servidores
├── Modelfile                 # Definición del modelo IA local sigta-ai
└── CREDENCIALES_PRUEBA.md    # Detalle de cuentas y permisos
```

---

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Libre para uso, modificación y distribución académica y profesional.
