# Multi-Agent Workflow Architecture

## Overview

El sistema ahora soporta dos modos de operación:

1. **Single-Agent Mode** (modo original): Generación directa de posts
2. **Multi-Agent Mode** (nuevo): Flujo colaborativo entre múltiples agentes especializados

## Multi-Agent Workflow

El flujo multi-agente involucra tres agentes especializados que colaboran secuencialmente:

### 1. Planner Agent 🎯
- **Rol**: Estratega de contenido
- **Función**: Crea un outline estructurado del post
- **Output**: 
  - Hook/Opening
  - Puntos principales (2-3 ideas clave)
  - Call-to-Action
  - Hashtags relevantes

### 2. Writer Agent ✍️
- **Rol**: Creador de contenido
- **Función**: Escribe el post basándose en el outline del Planner
- **Capacidades**:
  - Generación inicial
  - Reescritura basada en feedback del Critique
  - Adherencia a Brand Voice guidelines
- **Output**: Post completo de LinkedIn

### 3. Critique Agent 🔍
- **Rol**: Evaluador de calidad
- **Función**: Evalúa el post contra estándares de calidad y brand guidelines
- **Criterios de Evaluación**:
  - **Brand Adherence** (1-10): Cumplimiento de guías de marca
  - **Quality** (1-10): Estructura, hook, CTA
  - **Tone & Length** (1-10): Tono apropiado y longitud
- **Output**: 
  - Score general (0-10)
  - Aprobación (✅) o Rechazo (❌)
  - Feedback específico para mejoras

### Flujo de Ejecución

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PlannerAgent    │ → Genera outline estructurado
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ WriterAgent     │ → Escribe post basado en outline
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CritiqueAgent   │ → Evalúa (score 0-10)
└────────┬────────┘
         │
         ├─────────► Score ≥ Threshold? ──YES──► ✅ POST APROBADO
         │                                              │
         NO                                             ▼
         │                                       Return to User
         ▼
   Iteration < Max?
         │
         YES
         │
         ▼
┌─────────────────┐
│ WriterAgent     │ → Reescribe con feedback del Critique
└────────┬────────┘
         │
         └──────────► Vuelve a Critique (loop)
```

## Configuración

### Variables de Entorno

```bash
# Habilitar modo multi-agente
USE_MULTI_AGENT_FLOW=true

# Score mínimo para aprobar (0-10)
CRITIQUE_THRESHOLD=8.0

# Máximo número de reescrituras
MAX_REWRITES=2
```

### Código Python

```python
from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest

# Inicializar en modo multi-agente
agent = MarketingAgent(
    use_multi_agent=True,
    critique_threshold=8.0,
    max_rewrites=2,
)

# Generar post
request = GeneratePostRequest(
    topic="AI in healthcare",
    tone="professional",
    brand_id="techcorp",  # Optional
)

result = await agent.generate_post(request)

# Resultado incluye metadata del workflow
print(f"Iterations: {result.metadata['iterations']}")
print(f"Final Score: {result.metadata['final_score']}/10")
```

## Ventajas del Multi-Agent Mode

### 1. **Transparencia del Proceso**
- Logs detallados de cada paso
- Visibilidad del "pensamiento" de cada agente
- Trazabilidad completa del proceso de generación

### 2. **Control de Calidad Automatizado**
- Evaluación objetiva con scores numéricos
- Criterios de evaluación consistentes
- Feedback específico y accionable

### 3. **Mejora Iterativa**
- Reescrituras automáticas basadas en feedback
- Refinamiento progresivo del contenido
- Mayor adherencia a brand guidelines

### 4. **Modularidad**
- Agentes especializados e independientes
- Fácil de extender/modificar cada rol
- Testing más granular

## Comparación: Single vs Multi-Agent

| Aspecto | Single-Agent | Multi-Agent |
|---------|--------------|-------------|
| **Velocidad** | ⚡ Más rápido (1 LLM call) | 🐢 Más lento (3-5+ LLM calls) |
| **Calidad** | ✓ Buena | ✅ Excelente (con validación) |
| **Transparencia** | ❌ Caja negra | ✅ Proceso visible |
| **Control** | ⚠️ Limitado | ✅ Control fino |
| **Costo** | 💰 Menor (menos tokens) | 💰💰 Mayor (más tokens) |
| **Brand Adherence** | ✓ Depende del prompt | ✅ Validado automáticamente |
| **Debugging** | ❌ Difícil | ✅ Fácil (logs por agente) |

## Casos de Uso

### Usar Single-Agent cuando:
- Necesitas generación rápida
- El volumen de posts es alto
- La calidad "buena" es suficiente
- El costo por token es crítico

### Usar Multi-Agent cuando:
- La calidad es prioritaria
- Necesitas adherencia estricta a brand voice
- Quieres visibilidad del proceso
- El contenido es crítico/público
- Estás en fase de refinamiento de prompts

## Ejemplos

### Demo Completo
```bash
python examples/multi_agent_demo.py
```

Ver:
- `examples/multi_agent_demo.py` - Demostración de los 3 agentes
- `examples/compare_workflows.py` - Comparación lado a lado
- `tests/unit/test_multi_agent.py` - Tests unitarios

## Logs de Ejemplo

### Consola Output

```
################################################################################
🚀 MULTI-AGENT WORKFLOW STARTED
################################################################################
Topic: The future of AI in software development
Critique Threshold: 8.0/10
Max Rewrites: 2
################################################################################

================================================================================
🎯 PlannerAgent: Starting outline creation...
================================================================================
Topic: The future of AI in software development
Tone: professional
Max Length: 500 characters
Brand Voice: ✓ Applied

📋 PlannerAgent: Outline created!
--------------------------------------------------------------------------------
1. Hook: AI is transforming how we code...
2. Main Points:
   - Increased developer productivity
   - AI-assisted debugging and testing
   - Future: AI pair programmers
3. CTA: What's your experience with AI coding tools?
4. Hashtags: #AI #SoftwareDevelopment #DevTools
--------------------------------------------------------------------------------
Token usage: 245 tokens

================================================================================
✍️  WriterAgent: Writing post...
================================================================================

📄 WriterAgent: Post written!
--------------------------------------------------------------------------------
🚀 The future of software development is here...

AI is transforming how we code. From GitHub Copilot to ChatGPT...

[POST CONTENT]
--------------------------------------------------------------------------------
Length: 487 characters
Token usage: 356 tokens

================================================================================
🔍 CritiqueAgent: Evaluating post...
================================================================================
Pass threshold: 8.0/10

📊 CritiqueAgent: Evaluation complete!
--------------------------------------------------------------------------------
Overall Score: 9.2/10
Status: ✅ APPROVED

✓ Post meets all criteria!
Token usage: 198 tokens

================================================================================
✅ POST APPROVED after 1 iteration(s)!
================================================================================

################################################################################
🏁 MULTI-AGENT WORKFLOW COMPLETED
################################################################################
Total Iterations: 1
Final Score: 9.2/10
Status: ✅ Approved
Duration: 4.32 seconds
################################################################################
```

## Arquitectura de Código

```
src/agents/marketing/
├── agent.py              # MarketingAgent principal (soporta ambos modos)
├── multi_agent_flow.py   # Orquestador del flujo multi-agente
├── planner_agent.py      # PlannerAgent
├── writer_agent.py       # WriterAgent
├── critique_agent.py     # CritiqueAgent
└── ...
```

## API Endpoints

El API REST automáticamente usa el modo configurado en variables de entorno:

```bash
# Health check incluye modo actual
GET /health
{
  "status": "healthy",
  "agent_mode": "multi-agent",
  "multi_agent_config": {
    "enabled": true,
    "critique_threshold": 8.0,
    "max_rewrites": 2
  }
}

# Generate endpoint funciona igual
POST /generate
{
  "topic": "AI in healthcare",
  "tone": "professional",
  "brand_id": "techcorp"
}
```

## Testing

```bash
# Ejecutar tests de multi-agente
pytest tests/unit/test_multi_agent.py -v

# Ejecutar todos los tests
pytest tests/ -v
```

## Próximos Pasos

Posibles extensiones del sistema multi-agente:

1. **Research Agent**: Búsqueda y síntesis de información
2. **SEO Agent**: Optimización de hashtags y keywords
3. **Image Agent**: Generación/sugerencia de imágenes
4. **Schedule Agent**: Mejor momento para publicar
5. **Feedback Loop**: Aprendizaje de posts exitosos

## Referencias

- `BRAND_VOICE_GUIDE.md` - Guía del sistema de Brand Voice
- `ARCHITECTURE_SPEC.md` - Especificación de arquitectura original
- `README.md` - Documentación general del proyecto

