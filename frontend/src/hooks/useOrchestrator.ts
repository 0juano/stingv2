import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

const agentPorts = {
  bcra: 8002,
  comex: 8003,
  senasa: 8004
};

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
      
      // Handle both old and new routing formats
      const agents = routing.agents || (routing.agent ? [routing.agent] : []);
      const primaryAgent = routing.primary_agent || routing.agent || 'out_of_scope';
      
      onFlowUpdate?.({ 
        currentStep: 'router', 
        routing: {
          ...routing,
          agents: agents,
          primary_agent: primaryAgent
        },
        processing: agents.length > 1 
          ? `Routing to ${agents.length} agents: ${agents.map((a: string) => a.toUpperCase()).join(', ')}...`
          : `Routing to ${primaryAgent.toUpperCase()}...`
      });

      // If out of scope, return early
      if (!agents.length || primaryAgent === 'out_of_scope') {
        return {
          success: false,
          response: "❌ Esta consulta está fuera del alcance del sistema. Por favor, realiza preguntas sobre regulaciones argentinas (BCRA, Comex, Senasa).",
          totalCost: routeResponse.data.cost || 0
        };
      }

      // Step 2: Call agents (single or multiple)
      await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause for UX
      
      let agentResponses: any = {};
      let totalAgentCost = 0;
      
      if (agents.length > 1) {
        // Multi-agent case - call all agents in parallel
        onFlowUpdate?.({ 
          currentStep: 'agents',
          routing,
          processing: `Consultando ${agents.length} agentes en paralelo...` 
        });
        
        const agentPromises = agents.map(async (agent: string) => {
          const agentPort = {
            bcra: 8002,
            comex: 8003,
            senasa: 8004
          }[agent] || 8002;
          
          try {
            const response = await axios.post(
              `http://localhost:${agentPort}/answer`,
              { question }
            );
            return { agent, response: response.data };
          } catch (error) {
            console.error(`Error calling ${agent}:`, error);
            return { agent, response: { answer: { error: `Failed to contact ${agent}` }, cost: 0 } };
          }
        });
        
        const results = await Promise.all(agentPromises);
        results.forEach(({ agent, response }) => {
          agentResponses[agent] = response;
          totalAgentCost += response.cost || 0;
        });
      } else {
        // Single agent case - backwards compatibility
        const singleAgent = agents[0];
        const agentPort = {
          bcra: 8002,
          comex: 8003,
          senasa: 8004
        }[singleAgent as keyof typeof agentPorts] || 8002;

        onFlowUpdate?.({ 
          currentStep: singleAgent,
          routing,
          processing: 'Consultando regulaciones...' 
        });

        const agentResponse = await axios.post(
          `http://localhost:${agentPort}/answer`,
          { question }
        );
        
        agentResponses[singleAgent] = agentResponse.data;
        totalAgentCost = agentResponse.data.cost || 0;
      }

      // Step 3: Audit the response(s)
      await new Promise(resolve => setTimeout(resolve, 500));
      
      onFlowUpdate?.({ 
        currentStep: 'auditor',
        routing,
        processing: agents.length > 1 ? 'Integrando respuestas...' : 'Validando respuesta...' 
      });

      let auditResponse;
      if (agents.length > 1) {
        // Multi-agent audit
        try {
          auditResponse = await axios.post('http://localhost:8005/audit-multi', {
            user_question: question,
            agent_responses: agentResponses,
            primary_agent: primaryAgent
          });
        } catch (error: any) {
          if (error.response?.status === 404) {
            // Fallback to single agent audit for primary agent
            console.warn('Multi-agent audit not available, using primary agent only');
            auditResponse = await axios.post('http://localhost:8005/audit', {
              user_question: question,
              agent_response: agentResponses[primaryAgent]?.answer || {},
              agent_name: primaryAgent
            });
          } else {
            throw error;
          }
        }
      } else {
        // Single agent audit
        const singleAgent = agents[0];
        auditResponse = await axios.post('http://localhost:8005/audit', {
          user_question: question,
          agent_response: agentResponses[singleAgent]?.answer || {},
          agent_name: singleAgent
        });
      }

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
        totalAgentCost +
        (auditResponse.data.cost || 0);

      return {
        success: true,
        response: formatResponse.data.markdown,
        flow: {
          routing: routeResponse.data,
          agents: agentResponses,
          audit: auditResponse.data
        },
        agentsConsulted: agents,
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