# 🐾 Zoonosis API Demo (Backend)

⚠️ **NOTA IMPORTANTE DE SEGURIDAD**
Para garantizar la protección de la información sensible y cumplir con las normativas de privacidad, esta versión de la API publicada es una **demostración simplificada**. No contiene datos reales de producción ni credenciales activas.

---

## 📚 Índice

1. [📌 Visión General del Proyecto](#-visión-general-del-proyecto)
2. [✨ Funcionalidades Clave y Roles](#-funcionalidades-clave-y-roles)

   * [👤 Rol: Ciudadano](#-rol-ciudadano)
   * [🛡️ Rol: Administrador](#️-rol-administrador)
3. [💻 Stack Tecnológico](#-stack-tecnológico)
4. [⚙️ Arquitectura del Código](#️-arquitectura-del-código)
5. [💾 Modelo de Base de Datos](#-modelo-de-base-de-datos)
6. [🚀 Despliegue en Producción (Docker)](#-despliegue-en-producción-docker)
7. [🛠️ Inicio Rápido (Desarrollo Local)](#️-inicio-rápido-desarrollo-local)

---

## 📌 Visión General del Proyecto

Esta es la **API RESTful central del sistema de gestión de zoonosis y bienestar animal**. Construida como un **Monolito Modular** con **Python** y el micro-framework **Flask**, proporciona los endpoints necesarios para la administración de usuarios, mascotas, turnos, denuncias y la generación de reportes detallados.

El frontend, desarrollado con **React** y **Tailwind CSS**, consume esta API para ofrecer una interfaz de usuario fluida tanto para ciudadanos como para administradores.

---

## ✨ Funcionalidades Clave y Roles

El sistema ofrece un conjunto de herramientas bien definidas para dos roles principales: **Ciudadano** y **Administrador**.

---

## 👤 Rol: Ciudadano

El usuario ciudadano es el principal interactuador con las mascotas y los servicios, pudiendo:

### **Carga y Gestión de Datos:**

* Registrar su perfil y actualizar sus datos personales.
* **Cargar Animales:** Registrar sus mascotas.
* **Libreta Sanitaria Digital:** Ver el historial de vacunas y tratamientos de sus animales.

### **Servicios y Trámites:**

* **Denuncias:** Realizar y enviar denuncias.
* **Seguimiento:** Ver el estado de la denuncia (pendiente, en curso, resuelta, etc.).
* **Turnos:** Solicitar un turno médico (castración, vacunación, etc.) y visualizar la fecha asignada e instrucciones enviadas por el administrador.
* **Adopciones:** Explorar el listado de animales disponibles para adopción en la landing page.

---

## 🛡️ Rol: Administrador

El administrador tiene acceso a un panel integral para la gestión, mantenimiento y generación de informes del sistema.

### 🐕 **Gestión de Animales**

* Visualización de toda la información del animal, incluyendo su dueño.
* Control del Estado (activo/inactivo/fallecido).
* **Gestión de Patentes:** Ver el estado de la patente y realizar el proceso de patentamiento.
* **Libreta Sanitaria:** Añadir y ver registros.
* Inhabilitar animal por fallecimiento.
* Edición completa de los datos del animal.

### 👥 **Gestión de Usuarios**

* Métricas: Total de usuarios, activos, inactivos.
* Listado completo con filtros por estado y categoría.
* Edición de datos y roles.

### 🚨 **Gestión de Denuncias**

* Panel con identificación del denunciante, ubicación, estado y acciones.
* Ver detalle completo con archivos adjuntos.
* Cambiar estado (pendiente, en curso, resuelta).

### 🗓️ **Gestión de Turnos**

* Visualización de todas las solicitudes.
* Asignación de fecha e instrucciones.
* Notificaciones automáticas vía email.

### 🏡 **Gestión de Adopciones**

* Publicar animales con múltiples imágenes.
* Editar publicaciones.
* Cambiar estado a "Adoptado".

### 📈 **Reportes e Informes (PDF)**

* Generación de reportes administrativos.
* Información sobre animales, adopciones, denuncias y turnos.
* Reportes por fecha, mes, año o rango.
* Exportación a PDF lista para impresión.

---

## 💻 Stack Tecnológico

El proyecto utiliza una pila robusta.

### **Backend & Base de Datos**

* **Lenguaje:** Python
* **Framework:** Flask
* **Modularidad:** Blueprints (auth_routes, animal_routes, etc.)
* **ORM:** Flask-SQLAlchemy
* **Validación:** Marshmallow
* **Autenticación:** JWT
* **Base de Datos:** PostgreSQL

### **Servicios Externos**

* **Cloudinary:** Gestión de imágenes/archivos
* **Resend:** Emails transaccionales

### **Frontend (Repositorio Separado)**

* **React**
* **Tailwind CSS**

---

## ⚙️ Arquitectura del Código

Estructura modular para mantener claridad y escalabilidad.

```
app/models/   -> Tablas de la base de datos (SQLAlchemy)
app/routes/   -> Endpoints organizados por Blueprints
app/schemas/  -> Validación con Marshmallow
app/utils/    -> Servicios auxiliares (Cloudinary, email, reportes, etc.)
```

---

## 💾 Modelo de Base de Datos

Relaciones principales:

* **Usuario ↔ Animal** (Uno a Muchos)
* **Animal ↔ HistorialLibreta, FotoAnimal, Turno** (Uno a Muchos)
* **Animal ↔ Adopcion** (Uno a Uno)
* **Denuncia ↔ ArchivoDenuncia** (Uno a Muchos)

---

## 🚀 Despliegue en Producción (Docker)

La aplicación está completamente dockerizada para desplegar fácilmente en AWS u otro VPS.

### 🐳 Arquitectura de Despliegue

* Contenedor Backend (Flask)
* Contenedor PostgreSQL
* Contenedor Nginx (reverse proxy)

### **Pasos para Desplegar**

1. Crear archivo **.env** con claves y URLs (DB, Cloudinary, Resend, JWT, etc.).
2. Construir e inicializar servicios:

```bash
docker-compose up --build -d
```

La aplicación quedará disponible mediante Nginx.

---

## 🛠️ Inicio Rápido (Desarrollo Local)

Para ejecutar la API sin Docker:

### **1. Clonar repositorio:**

```bash
git clone https://github.com/Ezesnt/Zoonosis_api_demo.git
cd Zoonosis_api_demo
```

### **2. Crear archivo .env**

Completar variables necesarias.

### **3. Crear y activar entorno virtual:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
```

### **4. Instalar dependencias:**

```bash
pip install -r requirements.txt
```

### **5. Ejecutar la aplicación:**

```bash
python run.py
```

La API estará disponible en: **[http://localhost:5000](http://localhost:5000)**.

---

## 🐾 Gracias por visitar este proyecto

Si te interesa la arquitectura, el flujo de trabajo o querés colaborar, ¡estoy abierto a sugerencias y mejoras!

## 🚀 Despliegue en Producción

* **Frontend:** Hostinger
* **Backend API:** AWS VPS
* **Base de Datos:** PostgreSQL en producción

### 📡 Notificaciones

* 📧 Email vía Resend

### 🔒 Seguridad

* JWT con expiración
* Encriptación de contraseñas
* Validaciones con Marshmallow

### 🗂️ Manejo de Archivos

* Upload de imágenes y documentos

### 📊 Logs / Monitoreo

* Logs de accesos y errores
* Reportes mensuales integrados

### 💾 Backups

* Copias de la base

### 🌐 Dominio real

* [https://sanidadanimalbariloche.com/](https://sanidadanimalbariloche.com/)

### 🌐 Dominio demo 
* [https://zoonosis-api-front-demo.vercel.app/)
  
* Cliente
Email: prueba@gmail.com
Pass: Prueba1234?

Admin
Email: admin@gmail.com
Pass: Prueba1234?

## 🔟 Créditos / Autor

* **Desarrollado por:** Ezequiel Santillán
* **📧 Email:** [ezesnt@gmail.com](mailto:ezesnt@gmail.com)
* **💼 Portfolio:** [https://santillandev.vercel.app/](https://santillandev.vercel.app/)
* **🔗 LinkedIn:** [https://www.linkedin.com/in/ezesnt/](https://www.linkedin.com/in/ezesnt/)

## 📸 Capturas

<img width="1578" height="764" alt="image" src="https://github.com/user-attachments/assets/f5f3e2a8-b467-4a94-9ff1-ff5ba43e72d8" />
<img width="1572" height="763" alt="image" src="https://github.com/user-attachments/assets/2860e9db-c70d-4c52-ad6b-6dce08208c4d" />
<img width="1573" height="755" alt="image" src="https://github.com/user-attachments/assets/dfab6c44-887c-4830-8241-edd0e31b4d92" />
<img width="1575" height="762" alt="image" src="https://github.com/user-attachments/assets/fd679351-0300-49c8-8def-faf14e0be44f" />
<img width="1575" height="757" alt="image" src="https://github.com/user-attachments/assets/f9d72df9-d802-415f-a97c-34c6bfdce6d9" />
<img width="1573" height="766" alt="image" src="https://github.com/user-attachments/assets/71372982-4d77-425f-9e70-de6ebecb3391" />
<img width="1575" height="766" alt="image" src="https://github.com/user-attachments/assets/346f52bb-b988-447e-89a5-446e4d8c47e7" />
<img width="1582" height="766" alt="image" src="https://github.com/user-attachments/assets/213a71d7-736c-4ef2-8335-67be0afa80b4" />
<img width="1583" height="760" alt="image" src="https://github.com/user-attachments/assets/5a1d880a-51a3-4a52-b7b0-e5a8dbb9d11b" />
<img width="1573" height="766" alt="image" src="https://github.com/user-attachments/assets/ac0df849-7961-4114-8970-2822d5ec350c" />
<img width="1582" height="764" alt="image" src="https://github.com/user-attachments/assets/3eeb4fb9-1956-44cf-b311-dcb3abc75079" />







