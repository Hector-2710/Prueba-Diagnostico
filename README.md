# Visualizador de Minería

Análisis en tiempo real de las palabras más usadas en nombres de funciones desde repositorios de GitHub.

## Inicio Rápido

```bash
docker-compose up --build
```

Abre http://localhost:8000

## Cómo Usar

1. **Configurar N**: Selecciona cuántas palabras mostrar (por defecto 10)
2. **Iniciar Minería**: Haz click en el botón "Detenido"
3. **Visualizar**: La tabla se actualiza en tiempo real

## Características

- Extrae nombres de funciones desde repositorios Python y Java
- Tabla en tiempo real con las palabras más frecuentes
- Control de inicio/parada de la minería desde la UI
- Selector configurable de N palabras

## Estructura

```
├── miner/              # Extrae funciones desde repos de GitHub
│   ├── Dockerfile
│   └── miner.py        # Lógica principal de minería
├── visualizer/         # Backend FastAPI + Frontend
│   ├── Dockerfile
│   ├── app.py          # Servidor FastAPI con WebSocket
│   └── static/
│       └── index.html  # Frontend HTML puro + CSS/JS
├── requirements.txt    # Dependencias de Python
├── docker-compose.yml  # Orquestación Docker
└── README.md
```

## Decisiones de Diseño

  - Comunicación directa HTTP POST + WebSocket por simplicidad
  - Reducción de dependencias y complejidad 
  - Usar tabla HTML pura en lugar de librerias como D3

  Miner (HTTP POST) → Visualizer (/api/data) → WebSocket → Frontend (HTML puro)
  ```

## Requisitos

### Localmente
- Python 3.11+
- Git
- `pip install -r requirements.txt`

### Con Docker
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM mínimo (para compilación)

## Flujo de Datos

```
1. Miner busca repositorios en GitHub API
   └─> Filtra: language:{Python/Java} stars:>100
   
2. Para cada repo:
   └─> git clone --depth=1 (descarga superficial)
   └─> Escanea archivos .py y .java
   
3. Extracción de funciones:
   ├─> Python: ast.parse() → FunctionDef/ClassDef
   └─> Java: javalang.parse() → Method
   
4. Procesamiento de nombres:
   └─> Divide snake_case y camelCase
   └─> Convierte a minúsculas
   
5. Envío de datos:
   └─> POST /api/data a Visualizer
   
6. Visualizer:
   ├─> Actualiza Counter (en memoria)
   ├─> Calcula top N palabras
   └─> Envía por WebSocket a clientes
   
7. Frontend (HTML/CSS/JS):
   └─> Actualiza tabla en tiempo real sin librerías externas
```


