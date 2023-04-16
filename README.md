# wh.gg - Estadísticas detalladas, perfiles de invocadores y tier list para League of Legends

wh.gg es una aplicación web inspirada en [op.gg](https://www.op.gg/), [u.gg](https://u.gg/) y [porofessor.gg](https://porofessor.gg/), diseñada para buscar datos de invocadores de League of Legends utilizando la API de Riot Games y mostrar información relevante, como las úiltimas partidas jugadas, los datos de los campeones jugados por el invocador en toda la temporada, su rango en clasificatorias, etc.


## Características

- Buscar datos de invocadores por nombre de usuario (summoner name)
- Mostrar información detallada del invocador:
    - Últimas partidas jugadas
    - Datos de los campeones jugados en la temporada actual
    - Rango en ambas colas clasificatorias
- Diseño responsive y fácil de usar


## Tecnologías utilizadas

- Flask (Python)
- SQLite
- Cachetools
- HTML
- CSS
- JavaScript
- API requests


## Requisitos

- Python 3.7 o superior
- Flask
- SQLite
- Riot Games API Key


## Instalación y configuración

1. Clone el repositorio:
```bash
git clone https://github.com/usuario/wh.gg.git
cd wh.gg
```
2. Active su entorno virtual:
```bash
source venv/bin/activate
```
3. Instale las dependencias del proyecto utilizando el archivo **requirements.txt**:
```bash
pip install -r requirements.txt
```
4. Configure su clave de API de Riot Games en un archivo de configuracion o como una variable de entorno:
```bash
export RIOT_API_KEY=your_api_key
```
5. Inicie la aplicación Flask:
```bash
export FLASK_APP=wh.gg
export FLASK_ENV=development
flask run
```


## Contribuciones

Las contribuciones al proyecto son bienvenidas. Por favor, cree un fork del repositorio y realice los cambios en una neuva rama. Envíe un pull request con una descripción detallada de los cambios realizados.

## Licencia

wp.gg está licenciado bajo la Licencia MIT.