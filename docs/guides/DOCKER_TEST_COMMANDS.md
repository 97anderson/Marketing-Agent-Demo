# 🚀 Comandos de Prueba Docker - Marketing Agent Demo

## 📋 Prerequisitos
```powershell
# Verificar que Docker esté corriendo
docker ps

# Verificar que los contenedores estén up
docker-compose ps
```

---

## 🧪 Suite de Pruebas Completa

### 1️⃣ Health Check
```powershell
curl http://localhost:8000/health | python -m json.tool
```

**Resultado Esperado:**
```json
{
    "status": "healthy",
    "agent_mode": "multi-agent",
    "multi_agent_config": {
        "enabled": true,
        "critique_threshold": 8.0,
        "max_rewrites": 2
    }
}
```

---

### 2️⃣ Listar Brands Disponibles
```powershell
curl http://localhost:8000/brands | python -m json.tool
```

**Resultado Esperado:**
```json
{
    "available_brands": ["techcorp", "ecolife", "financewise"]
}
```

---

### 3️⃣ Generar Post con TechCorp Brand
```powershell
$postData = '{"topic": "AI-powered development tools", "tone": "professional", "brand_id": "techcorp"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData | python -m json.tool
```

**Características:**
- ✅ Workflow multi-agent
- ✅ Brand voice: TechCorp (Bold, innovative, forward-thinking)
- ✅ 2-3 iteraciones típicas

---

### 4️⃣ Generar Post con EcoLife Brand
```powershell
$postData = '{"topic": "Sustainable living in 2026", "tone": "inspirational", "brand_id": "ecolife"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData | python -m json.tool
```

**Características:**
- ✅ Brand voice: EcoLife (Warm, nurturing, earth-conscious)
- ✅ Tono inspiracional

---

### 5️⃣ Generar Post con FinanceWise Brand
```powershell
$postData = '{"topic": "Smart investing strategies", "tone": "authoritative", "brand_id": "financewise"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData | python -m json.tool
```

**Características:**
- ✅ Brand voice: FinanceWise (Professional, trustworthy, data-driven)
- ✅ Tono autoritativo

---

### 6️⃣ Generar Post SIN Brand Voice
```powershell
$postData = '{"topic": "Future of work", "tone": "casual"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData | python -m json.tool
```

**Características:**
- ✅ Sin brand_id (usa prompts genéricos)
- ✅ Tono casual

---

### 7️⃣ Descargar HTML Report
```powershell
curl -o my_report.html http://localhost:8000/report/download
Start-Process my_report.html
```

**Contenido del Report:**
- Timeline completo del workflow
- Métricas (tiempo, pasos, score)
- Feedback de cada iteración
- Diseño dark mode con Tailwind CSS

---

### 8️⃣ Ver Métricas Acumuladas
```powershell
curl http://localhost:8000/metrics | python -m json.tool
```

**Resultado Esperado:**
```json
{
    "total_posts_generated": 3,
    "posts_by_brand": {
        "techcorp": 1,
        "ecolife": 1,
        "financewise": 1
    },
    "available_brands": 3,
    "status": "operational"
}
```

---

## 🔄 Flujo Completo de Demostración

```powershell
# 1. Health check
Write-Host "`n[1/6] Health check..." -ForegroundColor Cyan
curl http://localhost:8000/health | python -m json.tool

# 2. Listar brands
Write-Host "`n[2/6] Listing brands..." -ForegroundColor Cyan
curl http://localhost:8000/brands | python -m json.tool

# 3. Generar con TechCorp
Write-Host "`n[3/6] Generating TechCorp post..." -ForegroundColor Cyan
$postData = '{"topic": "AI in software development", "tone": "professional", "brand_id": "techcorp"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData | python -m json.tool

# 4. Generar con EcoLife
Write-Host "`n[4/6] Generating EcoLife post..." -ForegroundColor Cyan
$postData = '{"topic": "Sustainable living", "tone": "inspirational", "brand_id": "ecolife"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData | python -m json.tool

# 5. Ver métricas
Write-Host "`n[5/6] Checking metrics..." -ForegroundColor Cyan
curl http://localhost:8000/metrics | python -m json.tool

# 6. Descargar report
Write-Host "`n[6/6] Downloading report..." -ForegroundColor Cyan
curl -o demo_report.html http://localhost:8000/report/download
Start-Process demo_report.html

Write-Host "`n[SUCCESS] Demo completado!" -ForegroundColor Green
```

---

## 🐛 Comandos de Debugging

### Ver logs en tiempo real
```powershell
docker-compose logs -f marketing-agent
```

### Ver últimos 50 logs
```powershell
docker-compose logs marketing-agent --tail=50
```

### Entrar al contenedor
```powershell
docker exec -it marketing-agent /bin/bash
```

### Verificar variables de entorno
```powershell
docker exec marketing-agent env | Select-String "MULTI_AGENT"
```

### Verificar knowledge base
```powershell
docker exec marketing-agent ls -la /app/knowledge_base
```

---

## 🔧 Comandos de Mantenimiento

### Reiniciar servicios
```powershell
docker-compose restart
```

### Rebuild completo
```powershell
docker-compose down
docker-compose up -d --build
```

### Ver estado de contenedores
```powershell
docker-compose ps
```

### Limpiar todo
```powershell
docker-compose down -v
docker system prune -a
```

---

## 📊 Análisis de Resultados

### Metadata del Post Generado

Cada respuesta incluye:

```json
{
  "post": {
    "id": "uuid-generado",
    "topic": "tema solicitado",
    "content": "contenido generado con brand voice",
    "tone": "tono aplicado",
    "brand_id": "brand usado",
    "metadata": {
      "workflow": "multi-agent",
      "iterations": 3,
      "final_score": 7.0,
      "workflow_summary": "[detalles de cada iteración]"
    }
  }
}
```

**Análisis de Metadata:**
- `iterations`: Número de rewrites (1-3)
- `final_score`: Score final (0-10)
- `workflow_summary`: Timeline completo
- Si `iterations > 1` → CritiqueAgent rechazó versiones anteriores
- Si `final_score < 8.0` → No alcanzó threshold pero llegó a max_rewrites

---

## 🎯 Casos de Prueba por Funcionalidad

### ✅ Multi-Agent Workflow
```powershell
# Prueba 1: Post que requiere rewrites
$postData = '{"topic": "Complex AI topic", "tone": "technical", "brand_id": "techcorp"}'
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData
# Espera: 2-3 iteraciones
```

### ✅ Brand Voice
```powershell
# Prueba 2: Diferentes brands
foreach ($brand in @("techcorp", "ecolife", "financewise")) {
    $postData = "{`"topic`": `"Test topic`", `"brand_id`": `"$brand`"}"
    curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d $postData
}
# Espera: 3 posts con estilos distintos
```

### ✅ HTML Reporting
```powershell
# Prueba 3: Report después de múltiples posts
# 1. Generar 3 posts
# 2. Descargar report
curl -o full_report.html http://localhost:8000/report/download
# Espera: Report con timeline completo de todos los posts
```

---

## 📝 Notas Importantes

1. **Mock Model**: El sistema usa un mock LLM para desarrollo. Para usar OpenAI real:
   ```yaml
   # docker-compose.yml
   environment:
     - USE_MOCK_MODEL=false
     - OPENAI_API_KEY=tu-api-key-real
   ```

2. **Thresholds**: Puedes ajustar los thresholds:
   ```yaml
   environment:
     - CRITIQUE_THRESHOLD=9.0  # Más estricto
     - MAX_REWRITES=3          # Más intentos
   ```

3. **Performance**: Con mock model: ~5-7 segundos. Con OpenAI real: ~15-30 segundos.

---

## 🎉 Resultado Esperado

Después de ejecutar el flujo completo deberías tener:

- ✅ Multiple posts generados con diferentes brands
- ✅ Archivo `demo_report.html` abierto en el navegador
- ✅ Métricas mostrando todos los posts generados
- ✅ Confirmación visual del workflow multi-agent

**¡El sistema está completamente funcional y validado!** 🚀

