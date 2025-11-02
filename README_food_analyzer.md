# Food Analyzer API

API para analizar imágenes de comida y obtener recetas y datos curiosos usando OpenAI Vision API.

## Requisitos

- Python 3.12+
- uv (gestor de paquetes)
- Clave API de OpenAI

## Instalación

1. Asegúrate de tener `uv` instalado
2. Navega al directorio del proyecto:

```powershell
cd h:\Andres\1Universidad\2025\topicos-ia\ai-topics-2-2025\2.tools
```

3. Sincroniza las dependencias con uv:

```powershell
uv sync
```

4. Crea un archivo `.env` en `2.tools/2.1.fastapi/` con tu clave de OpenAI:

```
OPENAI_API_KEY=sk-tu-clave-aqui
```

## Uso

### Ejecutar el servidor

Desde el directorio `2.tools`:

```powershell
uv run python 2.1.fastapi/food_analyzer_api.py
```

O usando uvicorn directamente:

```powershell
uv run uvicorn 2.1.fastapi.food_analyzer_api:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

### Documentación interactiva

Una vez que el servidor esté corriendo, puedes acceder a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Ejemplo de uso con curl

```powershell
curl -X POST "http://localhost:8000/analyze_food" `
  -F "file=@C:\ruta\a\tu\imagen.jpg"
```

### Ejemplo de uso con Python

```python
import requests

url = "http://localhost:8000/analyze_food"
files = {"file": open("mi_comida.jpg", "rb")}
response = requests.post(url, files=files)

if response.status_code == 200:
    result = response.json()
    print(f"Plato: {result['nombre_plato']}")
    print(f"\nIngredientes:")
    for ing in result['receta']['ingredientes']:
        print(f"  - {ing}")
    print(f"\nPasos:")
    for i, paso in enumerate(result['receta']['pasos'], 1):
        print(f"  {i}. {paso}")
    print(f"\nDatos curiosos:")
    for dato in result['datos_curiosos']:
        print(f"  • {dato}")
```

## Respuesta de la API

El endpoint `/analyze_food` devuelve un JSON con la siguiente estructura:

```json
{
  "nombre_plato": "Nombre del plato identificado",
  "receta": {
    "ingredientes": [
      "ingrediente 1",
      "ingrediente 2",
      "..."
    ],
    "pasos": [
      "paso 1",
      "paso 2",
      "..."
    ]
  },
  "datos_curiosos": [
    "dato curioso 1",
    "dato curioso 2",
    "dato curioso 3"
  ]
}
```

## Endpoints

### GET `/`
Información básica de la API.

### POST `/analyze_food`
Analiza una imagen de comida.

**Parámetros:**
- `file`: Archivo de imagen (multipart/form-data)

**Respuesta:** JSON con el análisis del plato

## Notas

- La API usa el modelo `gpt-4o-mini` de OpenAI con capacidades de visión
- Las imágenes se convierten a base64 antes de enviarlas a OpenAI
- Se valida que el archivo sea una imagen válida antes de procesarla
- Los costos de uso dependen de tu plan de OpenAI
