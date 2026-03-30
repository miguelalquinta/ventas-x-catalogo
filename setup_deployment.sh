#!/bin/bash

# Setup Script para Deployment
# Este script configura todo lo necesario para ejecutar la aplicación en producción

echo "🚀 Iniciando setup de deployment..."

# 1. Crear variables de entorno si no existen
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env y cambia SECRET_KEY y otros valores sensibles"
fi

# 2. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# 3. Crear directorio de archivos estáticos
echo "📁 Creando directorios necesarios..."
mkdir -p staticfiles
mkdir -p media

# 4. Recolectar archivos estáticos
echo "📊 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 5. Ejecutar migraciones
echo "🔄 Ejecutando migraciones de base de datos..."
python manage.py migrate

# 6. Crear superusuario (opcional)
echo ""
echo "👤 ¿Deseas crear un superusuario? (s/n)"
read -r create_user

if [ "$create_user" = "s" ] || [ "$create_user" = "S" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup completado correctamente!"
echo ""
echo "📝 Para ejecutar en desarrollo:"
echo "   python manage.py runserver"
echo ""
echo "🚀 Para ejecutar en producción:"
echo "   gunicorn ventas_catalogos.wsgi:application --config gunicorn_config.py"
