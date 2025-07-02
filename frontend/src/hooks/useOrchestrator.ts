import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

interface FlowUpdate {
  currentStep: string;
  routing?: any;
  processing?: string;
  complete?: boolean;
}

export function useOrchestrator() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processQuery = async (
    question: string,
    onFlowUpdate?: (flow: FlowUpdate) => void
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Route the query
      onFlowUpdate?.({ currentStep: 'router', processing: 'Analyzing query...' });
      
      const routeResponse = await axios.post(`${API_BASE_URL}/route`, { question });
      const routing = routeResponse.data.decision;
      
      onFlowUpdate?.({ 
        currentStep: 'router', 
        routing,
        processing: `Routing to ${routing.agent.toUpperCase()}...` 
      });

      // If out of scope, return early
      if (routing.agent === 'out_of_scope') {
        return {
          success: false,
          response: "❌ Esta consulta está fuera del alcance del sistema. Por favor, realiza preguntas sobre regulaciones argentinas (BCRA, Comex, Senasa).",
          totalCost: routeResponse.data.cost || 0
        };
      }

      // Step 2: Call the selected agent
      await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause for UX
      
      const agentPort = {
        bcra: 8002,
        comex: 8003,
        senasa: 8004
      }[routing.agent] || 8002;

      onFlowUpdate?.({ 
        currentStep: routing.agent,
        routing,
        processing: 'Consultando regulaciones...' 
      });

      const agentResponse = await axios.post(
        `http://localhost:${agentPort}/answer`,
        { question }
      );

      // Step 3: Audit the response
      await new Promise(resolve => setTimeout(resolve, 500));
      
      onFlowUpdate?.({ 
        currentStep: 'auditor',
        routing,
        processing: 'Validando respuesta...' 
      });

      const auditResponse = await axios.post('http://localhost:8005/audit', {
        user_question: question,
        agent_response: agentResponse.data.answer,
        agent_name: routing.agent
      });

      // Step 4: Format the response
      const formatResponse = await axios.post('http://localhost:8005/format', auditResponse.data);

      onFlowUpdate?.({ 
        currentStep: 'complete',
        routing,
        complete: true 
      });

      // Calculate total cost
      const totalCost = 
        (routeResponse.data.cost || 0) +
        (agentResponse.data.cost || 0) +
        (auditResponse.data.cost || 0);

      return {
        success: true,
        response: formatResponse.data.markdown,
        flow: {
          routing: routeResponse.data,
          agent: agentResponse.data,
          audit: auditResponse.data
        },
        totalCost
      };

    } catch (err: any) {
      console.error('Orchestrator error:', err);
      setError(err.message || 'Error processing query');
      
      return {
        success: false,
        response: `❌ Error: ${err.message || 'No se pudo procesar la consulta. Verifica que los servicios estén activos.'}`,
        totalCost: 0
      };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    processQuery,
    isLoading,
    error
  };
}