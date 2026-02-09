# HTML Report Generation System

## Overview

Sistema de generación de reportes HTML visuales para el flujo multi-agente del Marketing Agent. Reemplaza los logs de consola con reportes interactivos estilo ChatGPT/Vercel.

## Arquitectura

### Componentes

1. **TraceLogger** (`src/shared/trace_logger.py`)
   - Singleton que captura todos los pasos del workflow
   - Almacena información de cada agente
   - Calcula métricas (duración, costos, éxito)

2. **HTMLReporter** (`src/shared/html_reporter.py`)
   - Genera reportes HTML desde TraceLogger
   - Usa Jinja2 para templating
   - Tailwind CSS (CDN) para estilos
   - Abre automáticamente en navegador

## Uso

### Ejemplo Básico

```python
from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest
from src.shared.html_reporter import generate_report
from src.shared.trace_logger import get_trace_logger

# Reset logger
trace = get_trace_logger()
trace.reset()

# Run workflow
agent = MarketingAgent(use_multi_agent=True)
result = await agent.generate_post(request)

# Generate report
generate_report(
    trace_logger=trace,
    output_path="report.html",
    auto_open=True  # Open in browser
)
```

### Demo Completo

```bash
# Single scenario with report
python examples/multi_agent_with_report.py

# Multiple scenarios (generates 3 reports)
python examples/multi_agent_with_report.py --multiple
```

## TraceLogger API

### Logging Steps

```python
from src.shared.trace_logger import (
    get_trace_logger,
    ActionType,
    StepStatus
)

trace = get_trace_logger()

# Log a step
trace.log_step(
    agent_name="PlannerAgent",
    action_type=ActionType.PLANNING,
    content="Creating outline for topic...",
    status=StepStatus.THINKING,
    duration=1.5,
    tokens=250,  # metadata
)
```

### Action Types

```python
class ActionType(Enum):
    PLANNING = "Planificación"
    TOOL_USE = "Uso de Herramienta"
    GENERATION = "Generación de Texto"
    CRITIQUE = "Crítica"
    ERROR = "Error"
    INFO = "Información"
    REWRITE = "Reescritura"
```

### Step Status (con colores)

```python
class StepStatus(Enum):
    SUCCESS = "success"    # Verde
    FAILURE = "failure"    # Rojo
    THINKING = "thinking"  # Azul
    TOOL = "tool"         # Amarillo
    WARNING = "warning"   # Naranja
```

### Workflow Lifecycle

```python
# Start workflow
trace.start_workflow(
    topic="AI in healthcare",
    threshold=8.0,
    max_rewrites=2
)

# ... log steps ...

# End workflow
trace.end_workflow(
    iterations=2,
    final_score=8.5,
    approved=True
)
```

## Diseño del Reporte HTML

### Características

1. **Header con Resumen**
   - Tiempo total de ejecución
   - Total de pasos
   - Tasa de éxito
   - Costo estimado

2. **Resultado Final**
   - Score final (/10)
   - Estado: APROBADO / RECHAZADO
   - Número de iteraciones

3. **Timeline Interactivo**
   - Cada paso como tarjeta
   - Íconos por estado (✓, ✕, 💭, 🔧)
   - Badges de agente
   - Duración por paso
   - Timestamps
   - Metadata expandible

### Paleta de Colores

- **Fondo**: Oscuro (`#0f172a`)
- **Tarjetas**: `#1e293b`
- **Bordes**: `#334155`
- **Success**: Verde (`text-green-400`)
- **Failure**: Rojo (`text-red-400`)
- **Thinking**: Azul (`text-blue-400`)
- **Tool**: Amarillo (`text-yellow-400`)
- **Warning**: Naranja (`text-orange-400`)

## Integración en Agentes

Los agentes ya están integrados con TraceLogger:

```python
# PlannerAgent
trace.log_step(
    agent_name="PlannerAgent",
    action_type=ActionType.PLANNING,
    content=f"Outline created:\n{outline}",
    status=StepStatus.SUCCESS,
    duration=duration,
    tokens=response.usage.total_tokens
)

# WriterAgent
trace.log_step(
    agent_name="WriterAgent",
    action_type=ActionType.GENERATION,
    content=f"Post written:\n{content}",
    status=StepStatus.SUCCESS,
    duration=duration,
    length=len(content)
)

# CritiqueAgent
trace.log_step(
    agent_name="CritiqueAgent",
    action_type=ActionType.CRITIQUE,
    content=f"Score: {score}/10\nStatus: {status}",
    status=StepStatus.SUCCESS if approved else StepStatus.WARNING,
    score=score,
    approved=approved
)
```

## Estructura del Reporte

```html
<!DOCTYPE html>
<html class="dark">
<head>
  <title>Agent Execution Report</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950">
  <div class="container">
    <!-- Header -->
    <header>
      <h1>🤖 Agent Execution Report</h1>
      
      <!-- Summary Cards -->
      <div class="grid">
        <div>⏱️ Tiempo Total</div>
        <div>📊 Total Pasos</div>
        <div>✅ Tasa de Éxito</div>
        <div>💰 Costo Estimado</div>
      </div>
      
      <!-- Final Result -->
      <div>
        🎯 Resultado: ✅ APROBADO
        Score: 8.5/10
      </div>
    </header>
    
    <!-- Timeline -->
    <div class="timeline">
      <!-- Step Card 1 -->
      <div class="step-card">
        <div class="icon">✓</div>
        <div class="content">
          <span class="badge">PlannerAgent</span>
          <span>Planificación</span>
          <div class="step-content">...</div>
        </div>
      </div>
      
      <!-- More steps... -->
    </div>
  </div>
</body>
</html>
```

## Ventajas

1. **Visualización Clara**: Timeline interactivo tipo ChatGPT
2. **Información Completa**: Todos los pasos capturados con metadata
3. **Métricas Automáticas**: Duración, costos, tasa de éxito
4. **Compartible**: HTML estático, fácil de compartir
5. **Sin Dependencias**: Tailwind via CDN, no requiere build
6. **Diseño Moderno**: Dark mode, animaciones, responsive

## Comparación: Console vs HTML Report

| Aspecto | Console Logs | HTML Report |
|---------|--------------|-------------|
| **Visualización** | Lineal, difícil de seguir | Timeline interactivo |
| **Navegación** | Scroll infinito | Tarjetas organizadas |
| **Métricas** | Manual | Automáticas |
| **Compartir** | Copiar/pegar | Archivo HTML |
| **Búsqueda** | Ctrl+F básico | Estructura clara |
| **Diseño** | Texto plano | Moderno, colores |
| **Persistencia** | Se pierde al cerrar | Archivo guardado |

## Personalización

### Cambiar colores

Editar `HTML_TEMPLATE` en `src/shared/html_reporter.py`:

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        // Tu paleta personalizada
      }
    }
  }
}
```

### Agregar secciones

Extender el template Jinja2:

```html
<!-- Nueva sección -->
{% if metadata.custom_data %}
<div class="custom-section">
  {{ metadata.custom_data }}
</div>
{% endif %}
```

### Modificar métricas

En `TraceLogger.estimate_cost()`:

```python
def estimate_cost(self, tokens_per_step=500, cost_per_1k=0.002):
    # Tu lógica personalizada
    return calculated_cost
```

## Archivos

```
src/shared/
├── trace_logger.py       # TraceLogger singleton
└── html_reporter.py      # HTMLReporter con template

examples/
└── multi_agent_with_report.py  # Demo con reportes

# Reportes generados
agent_execution_report.html
report_no_brand.html
report_techcorp.html
report_ecolife.html
```

## Próximos Pasos

- [ ] Agregar filtros por agente
- [ ] Gráficas de tiempo/costos (Chart.js)
- [ ] Exportar a PDF
- [ ] Comparar múltiples ejecuciones
- [ ] Dashboard con histórico
- [ ] Integración con Prometheus/Grafana

## Referencias

- Tailwind CSS: https://tailwindcss.com/
- Jinja2: https://jinja.palletsprojects.com/
- Design inspirado en: ChatGPT, Vercel Logs, Linear

