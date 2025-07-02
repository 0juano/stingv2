# Test Queries for Bureaucracy Oracle

## BCRA Queries
1. "¿Puedo pagar Netflix desde Argentina?"
2. "¿Cuál es el límite para comprar dólares para ahorro?"
3. "Necesito pagar una factura de AWS de 800 dólares, ¿qué requisitos necesito?"
4. "¿Cómo hago para pagar un curso online en el exterior?"

## Comex Queries
1. "¿Qué necesito para importar notebooks desde China?"
2. "¿Cuál es el arancel para importar celulares?"
3. "¿Necesito licencia para exportar software?"
4. "¿Cómo clasifico arancelariamente repuestos de bicicleta?"

## Senasa Queries
1. "¿Qué certificados necesito para exportar carne a Brasil?"
2. "¿Puedo importar semillas de tomate desde España?"
3. "¿Cuáles son los requisitos sanitarios para un frigorífico?"
4. "¿Necesito permiso para traer mi mascota de Chile?"

## Multi-domain Queries (Should still route to primary agent)
1. "Quiero importar alimentos desde Brasil" (Primary: Senasa, might need Comex)
2. "¿Cómo pago la importación de insumos médicos?" (Primary: BCRA for payment)
3. "Necesito exportar software y cobrar en dólares" (Primary: BCRA for forex)

## Out of Scope Queries
1. "¿Cómo registro una marca?"
2. "¿Cuáles son los requisitos para abrir una SRL?"
3. "¿Qué impuestos paga un monotributista?"
4. "¿Cómo saco el registro de conducir?"

## Expected Responses Format

### Good Response Example (BCRA - Netflix payment):
```
🎯 Pagos al Exterior - Servicios Digitales

✅ Puede pagar hasta USD 500 mensuales sin conformidad previa del BCRA.

**Información Clave:**
📌 Límite: USD 500 por mes calendario por persona
📌 Concepto: Servicios digitales código S16
📌 Requiere: Declaración jurada en el banco

**Normativa Aplicable:**
📋 Comunicación A 7825 BCRA (2023)
📋 Comunicación A 7030 BCRA - Conceptos permitidos

**¿Qué hacer ahora?**
👉 Contacte a su banco con la factura de Netflix y solicite el pago bajo concepto S16

⚠️ El límite es compartido con todos los servicios digitales del mes

---
*Consultado: BCRA*
*Confianza: 95%*
```