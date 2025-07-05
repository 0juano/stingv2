import { useState } from 'react';
import axios from 'axios';
import { 
  getAnalyzingQuery, 
  getRoutingMultiple, 
  getRoutingSingle, 
  getConsultingMultiple, 
  getConsultingSingle,
  getIntegratingResponses,
  getValidatingResponse,
  getOutOfScope 
} from '../utils/bureaucratMessages';

// Detect if we're in production based on the current URL
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const baseHost = isProduction ? `http://${window.location.hostname}` : 'http://localhost';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `${baseHost}:8001`;

// For production (Render), we'll use full URLs. For local dev, construct from ports.
const agentUrls = {
  bcra: import.meta.env.VITE_BCRA_URL || `${baseHost}:8002`,
  comex: import.meta.env.VITE_COMEX_URL || `${baseHost}:8003`,
  senasa: import.meta.env.VITE_SENASA_URL || `${baseHost}:8004`
};

interface FlowUpdate {
  currentStep: string;
  routing?: any;
  processing?: string;
  complete?: boolean;
  stepData?: any;
}

export function useOrchestrator() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processQuery = async (
    question: string,
    onFlowUpdate?: (flow: FlowUpdate) => void
  ) => {
    // Enhanced logging with console group
    console.group('🚀 [useOrchestrator] New Query Request');
    console.log('📝 Question:', question);
    console.log('🌍 Environment:', isProduction ? 'PRODUCTION' : 'LOCAL');
    console.log('🏠 Base Host:', baseHost);
    console.log('🔗 API URLs:', {
      router: API_BASE_URL,
      auditor: `${baseHost}:8005`,
      agents: agentUrls
    });
    console.log('⏰ Started at:', new Date().toISOString());
    console.groupEnd();
    
    setIsLoading(true);
    setError(null);
    
    const startTime = Date.now(); // Track query start time

    try {
      // Step 1: Route the query
      console.group('📍 Step 1: Routing Query');
      console.log('🎯 Target URL:', `${API_BASE_URL}/route`);
      console.log('📤 Request payload:', { question });
      const routeStartTime = Date.now();
      
      onFlowUpdate?.({ currentStep: 'router', processing: getAnalyzingQuery() });
      
      const routeResponse = await axios.post(`${API_BASE_URL}/route`, { question }, { timeout: 10000 });
      
      console.log('✅ Route response received in', Date.now() - routeStartTime, 'ms');
      console.log('📥 Response data:', routeResponse.data);
      console.groupEnd();
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
          ? getRoutingMultiple(agents.map((a: string) => a.toUpperCase()).join(', '))
          : getRoutingSingle(primaryAgent),
        stepData: { agents, primaryAgent, confidence: routing.confidence }
      });

      // If out of scope, return early
      if (!agents.length || primaryAgent === 'out_of_scope') {
        const duration = (Date.now() - startTime) / 1000; // Duration in seconds
        console.warn('⚠️ Query is out of scope!');
        console.log('📊 Decision details:', {
          agents: agents,
          primaryAgent: primaryAgent,
          reason: routing.reason,
          confidence: routing.confidence
        });
        
        return {
          success: false,
          response: `❌ ${getOutOfScope()}`,
          totalCost: routeResponse.data.cost || 0,
          duration
        };
      }

      // Step 2: Call agents (single or multiple)
      // Removed artificial delay for better performance
      
      let agentResponses: any = {};
      let totalAgentCost = 0;
      
      if (agents.length > 1) {
        // Multi-agent case - call all agents in parallel
        onFlowUpdate?.({ 
          currentStep: 'agents',
          routing,
          processing: getConsultingMultiple(agents.length.toString()),
          stepData: { agentCount: agents.length, agents }
        });
        
        console.group('📡 Step 2: Calling Multiple Agents');
        console.log('🎯 Agents to call:', agents);
        
        const agentPromises = agents.map(async (agent: string) => {
          const agentUrl = agentUrls[agent as keyof typeof agentUrls];
          const agentStartTime = Date.now();
          console.log(`🔄 Calling ${agent.toUpperCase()} at: ${agentUrl}/answer`);
          
          try {
            const response = await axios.post(
              `${agentUrl}/answer`,
              { question },
              { timeout: 35000 } // 35 seconds timeout for agents
            );
            console.log(`✅ ${agent.toUpperCase()} responded in ${Date.now() - agentStartTime}ms`);
            return { agent, response: response.data };
          } catch (error: any) {
            console.error(`❌ ${agent.toUpperCase()} failed after ${Date.now() - agentStartTime}ms:`, {
              message: error.message,
              code: error.code,
              response: error.response?.data
            });
            return { agent, response: { answer: { error: `Failed to contact ${agent}` }, cost: 0 } };
          }
        });
        
        const results = await Promise.all(agentPromises);
        results.forEach(({ agent, response }) => {
          agentResponses[agent] = response;
          totalAgentCost += response.cost || 0;
        });
        
        console.log('📊 All agents completed. Total cost:', totalAgentCost);
        console.groupEnd();
        
        // Add completion notification for multi-agent flow
        onFlowUpdate?.({ 
          currentStep: 'agents',
          routing,
          processing: `✅ Los ${agents.length} agentes respondieron`,
          stepData: { agentCount: agents.length, agents, completed: true }
        });
      } else {
        // Single agent case - backwards compatibility
        const singleAgent = agents[0];
        const agentUrl = agentUrls[singleAgent as keyof typeof agentUrls];

        onFlowUpdate?.({ 
          currentStep: singleAgent,
          routing,
          processing: getConsultingSingle(singleAgent),
          stepData: { agent: singleAgent }
        });

        const agentResponse = await axios.post(
          `${agentUrl}/answer`,
          { question },
          { timeout: 35000 } // 35 seconds timeout for single agent
        );
        
        agentResponses[singleAgent] = agentResponse.data;
        totalAgentCost = agentResponse.data.cost || 0;
        
        // Add completion notification for single agent
        onFlowUpdate?.({ 
          currentStep: singleAgent,
          routing,
          processing: `✅ ${singleAgent.toUpperCase()} respondió`,
          stepData: { agent: singleAgent, completed: true }
        });
      }

      // Step 3: Audit the response(s)
      // Removed artificial delays for better performance
      
      onFlowUpdate?.({ 
        currentStep: 'auditor',
        routing,
        processing: agents.length > 1 ? getIntegratingResponses() : getValidatingResponse(),
        stepData: { isMultiAgent: agents.length > 1, agentCount: agents.length }
      });

      let auditResponse;
      const auditorUrl = import.meta.env.VITE_AUDITOR_URL || `${baseHost}:8005`;
      
      if (agents.length > 1) {
        // Multi-agent audit
        try {
          auditResponse = await axios.post(`${auditorUrl}/audit-multi`, {
            user_question: question,
            agent_responses: agentResponses,
            primary_agent: primaryAgent
          }, { timeout: 45000 }); // 45 seconds timeout for multi-agent audit
        } catch (error: any) {
          if (error.response?.status === 404) {
            // Fallback to single agent audit for primary agent
            console.warn('Multi-agent audit not available, using primary agent only');
            auditResponse = await axios.post(`${auditorUrl}/audit`, {
              user_question: question,
              agent_response: agentResponses[primaryAgent]?.answer || {},
              agent_name: primaryAgent
            }, { timeout: 30000 }); // 30 seconds timeout for fallback audit
          } else {
            throw error;
          }
        }
      } else {
        // Single agent audit
        const singleAgent = agents[0];
        auditResponse = await axios.post(`${auditorUrl}/audit`, {
          user_question: question,
          agent_response: agentResponses[singleAgent]?.answer || {},
          agent_name: singleAgent
        }, { timeout: 30000 }); // 30 seconds timeout for single agent audit
      }

      // Step 4: Format the response
      const formatResponse = await axios.post(`${auditorUrl}/format`, auditResponse.data, { timeout: 15000 }); // 15 seconds timeout for formatting

      onFlowUpdate?.({ 
        currentStep: 'complete',
        routing,
        complete: true,
        stepData: { finished: true }
      });

      // Calculate total cost and duration
      const totalCost = 
        (routeResponse.data.cost || 0) +
        totalAgentCost +
        (auditResponse.data.cost || 0);
      
      const duration = (Date.now() - startTime) / 1000; // Duration in seconds

      // Summary logging
      console.group('✅ Query Completed Successfully');
      console.log('⏱️ Total duration:', duration.toFixed(2), 'seconds');
      console.log('💰 Total cost: $', totalCost.toFixed(6));
      console.log('🤖 Agents consulted:', agents);
      console.log('📝 Response length:', formatResponse.data.markdown.length, 'characters');
      console.groupEnd();

      return {
        success: true,
        response: formatResponse.data.markdown,
        flow: {
          routing: routeResponse.data,
          agents: agentResponses,
          audit: auditResponse.data
        },
        agentsConsulted: agents,
        totalCost,
        duration
      };

    } catch (err: any) {
      console.group('❌ Query Failed with Error');
      console.error('🔴 Error type:', err.name);
      console.error('🔴 Error message:', err.message);
      console.error('🔴 Error code:', err.code);
      
      if (err.response) {
        console.error('🌐 API Error Details:', {
          status: err.response.status,
          statusText: err.response.statusText,
          data: err.response.data,
          headers: err.response.headers,
          config: {
            url: err.response.config?.url,
            method: err.response.config?.method,
            data: err.response.config?.data
          }
        });
      }
      
      console.error('📍 Stack trace:', err.stack);
      console.groupEnd();
      
      setError(err.message || 'Error processing query');
      
      const duration = (Date.now() - startTime) / 1000; // Duration in seconds
      
      // Provide more specific error messages
      let errorMessage = 'No se pudo procesar la consulta.';
      let debugHint = '';
      
      if (err.response?.status === 401) {
        errorMessage = 'Error de autenticación. Verifica la API key de OpenRouter.';
        debugHint = '🔑 Check OPENROUTER_API_KEY in .env file';
      } else if (err.code === 'ERR_NETWORK') {
        errorMessage = 'Error de conexión. Verifica que los servicios estén activos.';
        debugHint = `🌐 Failed to connect to: ${err.config?.url}`;
      } else if (err.response?.status >= 500) {
        errorMessage = 'Error del servidor. Intenta nuevamente.';
        debugHint = '🔥 Server error - check backend logs';
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'Timeout - La solicitud tardó demasiado.';
        debugHint = '⏱️ Request timed out after ' + (err.config?.timeout / 1000) + ' seconds';
      }
      
      if (debugHint) {
        console.log('💡 Debug hint:', debugHint);
      }
      
      return {
        success: false,
        response: `❌ Error: ${err.message || errorMessage}`,
        totalCost: 0,
        duration
      };
    } finally {
      console.log('🏁 Query processing finished. Duration:', ((Date.now() - startTime) / 1000).toFixed(2), 'seconds');
      setIsLoading(false);
    }
  };

  return {
    processQuery,
    isLoading,
    error
  };
}