// Bureaucrat personality message variations
// Inspired by a disgruntled Rioplatense bureaucrat (like the sloth from Zootopia)

interface MessageVariations {
  [key: string]: string[];
}

// Keep track of last used index for each message type to avoid repetition
const lastUsedIndex: { [key: string]: number } = {};

// Get a random message from variations, truly random but avoiding immediate repetition
export function getBureaucratMessage(messageType: string, replacements?: { [key: string]: string }): string {
  const variations = messages[messageType];
  if (!variations || variations.length === 0) {
    return messageType; // Fallback to message type if not found
  }

  let nextIndex: number;
  const lastIndex = lastUsedIndex[messageType];
  
  if (variations.length === 1) {
    nextIndex = 0;
  } else if (lastIndex === undefined) {
    // First time, pick random
    nextIndex = Math.floor(Math.random() * variations.length);
  } else {
    // Pick a different random index than the last one
    do {
      nextIndex = Math.floor(Math.random() * variations.length);
    } while (nextIndex === lastIndex);
  }
  
  lastUsedIndex[messageType] = nextIndex;

  let message = variations[nextIndex];

  // Replace placeholders
  if (replacements) {
    Object.keys(replacements).forEach(key => {
      message = message.replace(new RegExp(`\\$\\{${key}\\}`, 'g'), replacements[key]);
    });
  }

  return message;
}

const messages: MessageVariations = {
  // Initial greeting
  initialGreeting: [
    "SISTEMA DE CONSULTAS REGULATORIAS v1.0 - BCRA • COMEX • SENASA",
    "SISTEMA DE CONSULTAS REGULATORIAS v1.0 - BCRA • COMEX • SENASA", 
    "SISTEMA DE CONSULTAS REGULATORIAS v1.0 - BCRA • COMEX • SENASA",
    "SISTEMA DE CONSULTAS REGULATORIAS v1.0 - BCRA • COMEX • SENASA"
  ],

  // Initial instruction
  initialInstruction: [
    "Escribí tu consulta",
    "Escribí tu consulta",
    "Escribí tu consulta",
    "Escribí tu consulta"
  ],

  // Analyzing query (router step)
  analyzingQuery: [
    "Uy... a ver qué me traés ahora... *revisando papeles*",
    "Esperá que busco los anteojos... ah, ahí está tu consulta...",
    "Dejame ver... *ruido de papeles* ...dónde habré puesto eso...",
    "Ay, otra consulta... bueno, vamos a ver de qué se trata...",
    "A ver, a ver... *tomando mate* ...qué tenemos acá...",
    "*Suspiro profundo* Dale, veamos qué necesitás...",
    "Mmm... esperá que proceso esto... despacio...",
    "Bueno, bueno... *acomodando escritorio* ...a ver tu problema..."
  ],

  // Routing to multiple agents
  routingMultiple: [
    "Uf, esto es para varios departamentos... llamá a ${agents}... qué lío...",
    "Mirá vos, tengo que molestar a ${agents}... como si no tuviera nada que hacer...",
    "Che, esto es un quilombo... necesito a ${agents} para esto...",
    "Ay no, tengo que coordinar con ${agents}... va a ser largo esto...",
    "*Resoplido* Tengo que llamar a ${agents}... todos al mismo tiempo...",
    "Esto necesita a ${agents}... preparate para esperar...",
    "Apa, consulta múltiple... ${agents} van a tener que laburar..."
  ],

  // Routing to single agent
  routingSingle: [
    "Ah, esto es para ${agent} nomás... menos mal...",
    "Bueno, le paso tu problema a ${agent}... esperá sentado, eh...",
    "Dale, voy arrastrándome hasta ${agent} con tu consulta...",
    "Esto le corresponde a ${agent}... ahí voy, ahí voy..."
  ],

  // Consulting multiple agents
  consultingMultiple: [
    "Esperá que llamo a los ${count} departamentos... *bostezo*",
    "Uy, tengo que coordinar con ${count} oficinas... qué pereza...",
    "Mandando palomas mensajeras a ${count} ventanillas...",
    "Convocando a ${count} departamentos... esto va a demorar...",
    "Llamando a ${count} internos... si atienden...",
    "*Marcando teléfonos* Consultando ${count} oficinas... paciencia...",
    "Activando ${count} departamentos... como en cámara lenta..."
  ],

  // Consulting single agent
  consultingSingle: [
    "Ahí voy... caminando... consultando con ${agent}...",
    "*Arrastrando papeles* Consultando en ${agent}...",
    "Esperá que ${agent} me atiende... si no está en el descanso...",
    "Tocando la puerta de ${agent}... esperemos que esté...",
    "Buscando a alguien de ${agent}... *pasos lentos*",
    "Llevando tu consulta a ${agent}... ya casi llego...",
    "Molestando a los de ${agent}... perdón, 'consultando'...",
    "*Golpeando ventanilla* ${agent}... ¿hay alguien?",
    "Rastreando a ${agent}... debe andar por ahí...",
    "Interrumpiendo el mate en ${agent}... qué remedio..."
  ],

  // Integrating responses (multi-agent)
  integratingResponses: [
    "Ahora tengo que juntar todo este papelerío... dame un segundo...",
    "Uf, consolidando las respuestas... no me apures...",
    "Revisando que todo coincida... siempre hay algo que no cierra...",
    "Juntando todos los sellos y formularios... qué desorden..."
  ],

  // Validating response (single agent)
  validatingResponse: [
    "Dejame chequear que esté todo en orden... *sello*",
    "Verificando... sellando... firmando... ¿dónde dejé el sello?",
    "A ver si está todo completo... *revisando con lupa*",
    "Controlando que no falte nada... uno nunca sabe..."
  ],

  // Out of scope error
  outOfScope: [
    "Che, eso no es de acá... andá a otra ventanilla...",
    "No, no, no... eso no me corresponde a mí... siguiente!",
    "Mirá, yo de eso no sé nada... probá en el edificio de enfrente...",
    "¿Eso me preguntás? Acá solo vemos BCRA, Comex y Senasa, nada más..."
  ],

  // Input placeholder - normal
  inputPlaceholder: [
    "Ingrese su consulta",
    "Ingrese su consulta",
    "Ingrese su consulta",
    "Ingrese su consulta"
  ],

  // Input placeholder - processing
  processingPlaceholder: [
    "Procesando... no cuelgues que ya vuelvo...",
    "Trabajando... o algo así...",
    "Esperá un cachito... estoy en eso...",
    "Dale que ya termino... paciencia..."
  ],

  // Clear button was pressed
  clearingChat: [
    "Ah, ¿empezamos de nuevo? Bueno...",
    "Borrando todo... como si no hubiera trabajado...",
    "¿Otra vez? Dale, limpiemos todo...",
    "Tirando todos los papeles... total, para qué..."
  ]
};

// Export individual message getters for convenience
export const getInitialGreeting = () => getBureaucratMessage('initialGreeting');
export const getInitialInstruction = () => getBureaucratMessage('initialInstruction');
export const getAnalyzingQuery = () => getBureaucratMessage('analyzingQuery');
export const getRoutingMultiple = (agents: string) => 
  getBureaucratMessage('routingMultiple', { agents });
export const getRoutingSingle = (agent: string) => 
  getBureaucratMessage('routingSingle', { agent: agent.toUpperCase() });
export const getConsultingMultiple = (count: string) => 
  getBureaucratMessage('consultingMultiple', { count });
export const getConsultingSingle = (agent: string) => 
  getBureaucratMessage('consultingSingle', { agent: agent.toUpperCase() });
export const getIntegratingResponses = () => getBureaucratMessage('integratingResponses');
export const getValidatingResponse = () => getBureaucratMessage('validatingResponse');
export const getOutOfScope = () => getBureaucratMessage('outOfScope');
export const getInputPlaceholder = () => getBureaucratMessage('inputPlaceholder');
export const getProcessingPlaceholder = () => getBureaucratMessage('processingPlaceholder');
export const getClearingChat = () => getBureaucratMessage('clearingChat');