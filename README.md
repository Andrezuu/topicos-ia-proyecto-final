# 🍽️ Food Analyzer Agent

API inteligente para análisis de comida usando **DSPy Agents** + **OpenAI Vision API**. 

Combina la potencia de agentes inteligentes con razonamiento Chain-of-Thought para analizar imágenes de comida, calcular información nutricional y comparar platos desde perspectivas culinarias, nutricionales y culturales.

## ✨ Características

- 🤖 **Agente DSPy inteligente** con razonamiento Chain-of-Thought
- 🔧 **Sistema de Tools modular** para análisis, nutrición y comparación
- 👁️ **Análisis de imágenes** usando OpenAI Vision API
- 🥗 **Cálculo nutricional** inteligente con estimaciones realistas
- ⚖️ **Comparación de platos** desde múltiples perspectivas
- 💾 **Base de datos SQLite** para persistencia de análisis
- 🌐 **API REST** con FastAPI y validación Pydantic
- 📊 **UI interactiva** con tabs para diferentes funciones

## 🏗️ Arquitectura

### Patrón de Tools

El agente utiliza un sistema modular de **Tools** separados de las **Signatures**:

```python
# Tools = Ejecución técnica
AnalyzeFoodTool       # Llama Vision API y procesa JSON
NutritionCalculatorTool  # Calcula valores nutricionales
DishComparisonTool    # Compara dos platos

# Signatures = Estructura de entrada/salida para razonamiento DSPy
AnalyzeFoodImageSignature
CalculateNutritionSignature
CompareDishesSignature

# Agent = Orquestación
FoodAnalyzerAgent
├── Ejecuta Tools para obtener datos crudos
└── Aplica Signatures para añadir razonamiento inteligente
```

### Flujo de trabajo

```
Usuario → API Endpoint → Agent → Tool (ejecuta acción)
                          ↓
                    Signature (razona sobre resultado)
                          ↓
                    Respuesta estructurada con razonamiento
```

## 📋 Requisitos

- Python 3.12+
- uv (gestor de paquetes)
- Clave API de OpenAI

## Instalación

1. Asegúrate de tener `uv` instalado
2. Clona el proyecto

```powershell
git clone https://github.com/Andrezuu/topicos-ia-proyecto-final.git
```

3. Sincroniza las dependencias con uv:

```powershell
uv sync
```

4. Crea un archivo `.env` en la raiz del proyecto con tu clave de OpenAI:

```
OPENAI_API_KEY=sk-tu-clave-aqui
```

## Uso

### Ejecutar el servidor

Desde la raíz del proyecto:

```powershell
uv run python food_analyzer_api.py
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

## 🔌 Endpoints

### `GET /`
Información básica de la API y endpoints disponibles.

### `POST /analyze_food`
Analiza una imagen de comida usando el agente inteligente.

**Tool usado:** `AnalyzeFoodTool`  
**Parámetros:**
- `file`: Archivo de imagen (multipart/form-data)

**Respuesta:**
```json
{
  "nombre_plato": "string",
  "receta": {
    "ingredientes": ["string"],
    "pasos": ["string"]
  },
  "datos_curiosos": ["string"]
}
```

**Guarda automáticamente el análisis en la base de datos.**

### `GET /nutrition/{dish_name}`
Calcula información nutricional para un plato.

**Tool usado:** `NutritionCalculatorTool`  
**Parámetros:**
- `dish_name`: Nombre del plato (path parameter)
- `ingredients`: Ingredientes separados por coma (query parameter, opcional)

**Respuesta:**
```json
{
  "dish_name": "string",
  "nutrition": {
    "serving_size": "string",
    "calories": number,
    "proteins": number,
    "carbs": number,
    "fats": number,
    "fiber": number,
    "notes": "string"
  },
  "agent_reasoning": "string"
}
```

### `GET /compare`
Compara dos platos guardados en la base de datos.

**Tool usado:** `DishComparisonTool`  
**Parámetros:**
- `analysis_id1`: ID del primer análisis (query parameter)
- `analysis_id2`: ID del segundo análisis (query parameter)

**Respuesta:**
```json
{
  "dish1": {
    "id": number,
    "name": "string",
    "ingredients": ["string"]
  },
  "dish2": {
    "id": number,
    "name": "string",
    "ingredients": ["string"]
  },
  "comparison": {
    "similarity_score": number,
    "common_ingredients": ["string"],
    "unique_to_dish1": ["string"],
    "unique_to_dish2": ["string"],
    "culinary_relationship": "string",
    "cultural_context": "string",
    "key_differences": ["string"]
  },
  "agent_reasoning": "string"
}
```

### `GET /history`
Obtiene el historial de análisis guardados.

**Parámetros:**
- `limit`: Número máximo de registros (query parameter, default: 10)

### `GET /analysis/{id}`
Obtiene un análisis específico por ID.

## 🧠 Ventajas del Sistema de Tools

### ✅ **Separación de responsabilidades**
- **Tools**: Ejecución técnica (llamadas API, procesamiento)
- **Signatures**: Estructura y razonamiento DSPy
- **Agent**: Orquestación y lógica de negocio

### ✅ **Escalabilidad**
- Agregar nuevos tools es trivial
- Cada tool es independiente y testeable
- Fácil migrar a ReAct agent para selección automática de tools

### ✅ **Reutilización**
- Tools pueden usarse en diferentes módulos
- Código limpio y mantenible
- Fácil de debugear por componente

### ✅ **Razonamiento inteligente**
- DSPy ChainOfThought añade contexto a cada respuesta
- `agent_reasoning` muestra el proceso mental del agente
- Respuestas más ricas y explicables

## 📁 Estructura del proyecto

```
proyecto-final/
├── agent.py              # Agente DSPy con Tools y Signatures
├── food_analyzer_api.py  # API FastAPI
├── database.py           # Gestión SQLite
├── tools.py              # Wrappers para API
├── food_analyzer_ui.html # UI principal
├── style.css             # Estilos
├── pyproject.toml        # Dependencias
└── .env                  # Variables de entorno
```

## 🔧 Stack Tecnológico

- **Backend**: FastAPI 3.0.0
- **Agente**: DSPy con ChainOfThought
- **LLM**: OpenAI GPT-4o-mini (visión + texto)
- **Base de datos**: SQLite con índices
- **Frontend**: HTML/CSS/JS vanilla
- **Gestor**: uv para dependencias

## 📝 Notas

- La API usa el modelo `gpt-4o-mini` de OpenAI con capacidades de visión
- Cada endpoint incluye `tool_used` para rastrear qué tool se ejecutó
- El campo `agent_reasoning` muestra el razonamiento Chain-of-Thought
- Base de datos SQLite persiste todos los análisis con timestamp
- Los costos de uso dependen de tu plan de OpenAI

## 🚀 Próximas mejoras

- [ ] Fine-tune de modelo local para clasificación de comida
- [ ] Sistema RAG con ChromaDB para búsqueda semántica de recetas
- [ ] Frontend React + TypeScript
- [ ] Sistema de caché con Redis
- [ ] Tests automatizados con pytest
- [ ] CI/CD con GitHub Actions
