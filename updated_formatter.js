// Final Response Formatter
const auditorOutput = $input.item.json;

// Parse the output if it's a string
let parsedOutput;
try {
  parsedOutput = typeof auditorOutput.output === 'string' 
    ? JSON.parse(auditorOutput.output) 
    : auditorOutput.output;
} catch (error) {
  return [{
    json: {
      response: "❌ Error al procesar la respuesta. Por favor, intente nuevamente.",
      error: true
    }
  }];
}

// Extract the final response
const finalResponse = parsedOutput.respuesta_final;
const status = parsedOutput.status;

// Build the formatted response
let formattedResponse = '';

if (status === 'Aprobado' && finalResponse) {
  // Title
  formattedResponse += `${finalResponse.titulo}\n\n`;
  
  // Direct response
  formattedResponse += `${finalResponse.respuesta_directa}\n\n`;
  
  // Key details
  if (finalResponse.detalles && finalResponse.detalles.length > 0) {
    formattedResponse += `**Información Clave:**\n`;
    finalResponse.detalles.forEach(detail => {
      formattedResponse += `${detail}\n`;
    });
    formattedResponse += '\n';
  }
  
  // Applicable regulations
  if (finalResponse.normativa_aplicable && finalResponse.normativa_aplicable.length > 0) {
    formattedResponse += `**Normativa Aplicable:**\n`;
    finalResponse.normativa_aplicable.forEach(norma => {
      formattedResponse += `${norma}\n`;
    });
    formattedResponse += '\n';
  }
  
  // Next action
  if (finalResponse.proxima_accion) {
    formattedResponse += `**¿Qué hacer ahora?**\n`;
    formattedResponse += `${finalResponse.proxima_accion}\n\n`;
  }
  
  // Warnings
  if (finalResponse.advertencias) {
    formattedResponse += `${finalResponse.advertencias}\n\n`;
  }
  
  // Footer with metadata
  formattedResponse += `---\n`;
  
  // Handle agent names (could be single or multiple)
  const agentesConsultados = parsedOutput.metadata?.agentes_consultados;
  const agenteConsultado = parsedOutput.metadata?.agente_consultado;
  let agentsText = 'Sistema';
  
  if (agentesConsultados && Array.isArray(agentesConsultados)) {
    agentsText = agentesConsultados.map(a => a.toUpperCase()).join(', ');
  } else if (agenteConsultado) {
    agentsText = agenteConsultado.toUpperCase();
  }
  
  formattedResponse += `*Consultado: ${agentsText}*\n`;
  
  // Only show confidence if it's available
  const confidence = parsedOutput.metadata?.confianza;
  if (confidence !== undefined && confidence !== null) {
    const confidencePercent = Math.round(confidence * 100);
    const breakdown = parsedOutput.metadata?.confidence_breakdown;
    
    // Embed confidence data in a special format for frontend parsing
    if (breakdown) {
      // Create a special marker that the frontend can parse
      formattedResponse += `*<confidence-score data='${JSON.stringify({
        score: confidencePercent,
        breakdown: breakdown
      })}'>Confianza: ${confidencePercent}%</confidence-score>*`;
    } else {
      // Fallback to simple display
      formattedResponse += `*Confianza: ${confidencePercent}%`;
      
      // Add explanation for low confidence
      if (confidencePercent < 80) {
        const factors = parsedOutput.metadata?.confidence_factors;
        if (factors) {
          if (factors.contains_insufficient_context) {
            formattedResponse += ` (información limitada disponible)`;
          } else if (!factors.has_specific_regulations) {
            formattedResponse += ` (sin regulaciones específicas)`;
          }
        }
      }
      formattedResponse += `*`;
    }
  }
  
} else if (status === 'Observado') {
  formattedResponse = `⚠️ **Respuesta con Observaciones**\n\n`;
  formattedResponse += `La consulta fue procesada pero requiere aclaraciones:\n`;
  formattedResponse += `${parsedOutput.motivo_auditoria}\n\n`;
  formattedResponse += `Por favor, reformule su consulta con más detalles.`;
  
} else if (status === 'Rechazado') {
  formattedResponse = `❌ **No se pudo procesar la consulta**\n\n`;
  formattedResponse += `Motivo: ${parsedOutput.motivo_auditoria}\n\n`;
  formattedResponse += `Por favor, verifique su consulta e intente nuevamente.`;
  
} else {
  // Handle out of scope or insufficient context
  formattedResponse = parsedOutput.respuesta_final || 
    "Lo siento, no puedo procesar esta consulta. Por favor, realice una pregunta sobre regulaciones argentinas de BCRA, Comercio Exterior o Senasa.";
}

// Return the formatted response
return [{
  json: {
    response: formattedResponse,
    status: status,
    metadata: parsedOutput.metadata || {}
  }
}];