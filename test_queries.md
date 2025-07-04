# 🧪 Test Queries for Bureaucracy Oracle

Use these queries to test each agent after deployment:

## BCRA Agent Tests
```
1. ¿Cuál es el límite mensual para comprar dólares?
2. ¿Cómo pago un servicio de AWS desde Argentina?
3. ¿Qué documentación necesito para transferir USD 5000 al exterior?
```

## Comex Agent Tests
```
1. ¿Cuáles son los requisitos para importar notebooks desde China?
2. ¿Qué arancel paga la importación de smartphones?
3. ¿Cómo obtengo una licencia de importación para productos electrónicos?
```

## Senasa Agent Tests
```
1. ¿Qué certificados necesito para exportar carne a Brasil?
2. ¿Cuáles son los requisitos fitosanitarios para importar semillas?
3. ¿Cómo registro un establecimiento elaborador de alimentos?
```

## Multi-Agent Tests (Router should select multiple)
```
1. ¿Puedo importar alimentos desde USA y cuánto puedo gastar en dólares?
2. Quiero exportar software y cobrar en dólares, ¿qué necesito?
3. ¿Qué impuestos pago al importar insumos agrícolas y pagar con tarjeta?
```

## Out of Scope Tests (Should reject politely)
```
1. ¿Cuál es el precio del dólar blue hoy?
2. ¿Cómo está el clima en Buenos Aires?
3. ¿Cuánto cuesta un iPhone 15 en Argentina?
```

## Expected Behavior

✅ **Good Response:**
- Clear section headers with emojis
- Bullet points for requirements
- Legal citations [Resolución XXX/2024]
- Next steps section
- Response time < 10 seconds (after warm-up)

❌ **Issues to Watch:**
- Timeout errors (increase timeouts)
- CORS errors (check origins)
- 502/503 errors (service not started)
- Empty responses (check API keys)