# Uso de Entorno Virtual en Python con virtualenv

## ¿Por qué usar un entorno virtual?

En Python, los entornos virtuales se utilizan para aislar proyectos y sus dependencias. Esto permite evitar conflictos entre las versiones de los paquetes utilizados en diferentes proyectos.

## Instalar virtualenv

Si aún no tienes instalado `virtualenv`, puedes hacerlo utilizando el siguiente comando:

```bash
pip install virtualenv
```

## Crear un nuevo entorno virtual

1. Navega hasta el directorio de tu proyecto en la terminal.
2. Crea un nuevo entorno virtual con el siguiente comando:

```bash
virtualenv venv
```

Esto creará un directorio llamado `venv` que contendrá el entorno virtual.

## Activar el entorno virtual

En Windows:

```bash
venv\Scripts\activate
```

En sistemas basados en Unix (Linux/Mac):

```bash
source venv/bin/activate
```

Verás el nombre del entorno virtual en tu terminal, indicando que está activo.

## Instalar dependencias

Con el entorno virtual activado, puedes instalar las dependencias de tu proyecto:

```bash
pip install nombre_del_paquete1 nombre_del_paquete2
```

## Generar requirements.txt

Después de instalar los paquetes necesarios, puedes generar un archivo `requirements.txt` para compartir las dependencias:

```bash
pip freeze > requirements.txt
```

## Desactivar el entorno virtual

Cuando hayas terminado de trabajar en tu proyecto, desactiva el entorno virtual:

```bash
deactivate
```

Esto restaurará el entorno a su estado original.
¡Ahora estás listo para desarrollar tu proyecto Python en un entorno virtual!