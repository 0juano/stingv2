---

kanban-plugin: board

---

## 📖 In Progress Requirements

- [ ] **[Task Title]** - Brief one-line description
	  
	  **Problem Statement**
	  - Clear description of the issue
	  - User impact and symptoms
	  - Reference to screenshots/examples if applicable
	  
	  **Technical Analysis**
	  - Current implementation details
	  - Code locations (file:line_number)
	  - Root cause analysis
	  - Related components affected
	  
	  **Solution Approach**
	  - High-level strategy
	  - Step-by-step implementation plan
	  - Alternative approaches considered
	  - Chosen approach justification
	  
	  **Implementation Steps**
	  ```language
	  // Actual code examples
	  // Show before/after changes
	  // Include file paths
	  ```
	  
	  **Testing Requirements**
	  - Device/browser matrix
	  - Test cases to verify
	  - Edge cases to consider
	  - Performance impact tests
	  
	  **Deployment Process**
	  ```bash
	  # Specific commands for deployment
	  # Include Docker rebuild steps
	  # Environment variable considerations
	  ```
	  
	  **Success Criteria**
	  - Measurable outcomes
	  - How to verify the fix works
	  - User experience improvements
	  - Performance benchmarks if applicable
	  
	  **Risks & Mitigation**
	  - Risk: What could go wrong
	  - Mitigation: How to prevent/handle it
	  - Rollback plan if needed
	  - Dependencies on other systems


## 📋 Backlog

- [ ] **Add basic analytics** - Track queries, agent usage, visitor origins
- [x] **Add "Examples" button** - Show common queries users can try
- [ ] **Create landing page** - Explain what the oracle does
- [x] **Add share buttons** - Let users share helpful responses
- [ ] **Implement feedback system** - "¿Fue útil? 👍👎"
- [ ] **Make mobile PWA** - Add to home screen capability
- [ ] **Add visitor counter** - Show "X consultas respondidas"
- [ ] **Monitor API costs daily** - Add cron job for cost-monitor.py
- [ ] **Add error recovery** - Handle OpenRouter downtime gracefully
- [ ] **Cache common queries** - Save API costs on repeated questions
- [ ] **Improve error messages** - User-friendly messages in Spanish
- [ ] Add links to normativa documents when shared
- [ ] Implement real-time streaming responses
- [ ] Add conversation history
- [ ] Show agent selection reasoning in UI
- [ ] Response caching for common queries
- [ ] Query suggestions/autocomplete
- [ ] Export chat history
- [ ] Rate limiting
- [ ] User authentication (optional)
- [ ] **Add HTTPS with Let's Encrypt** 🔒
- [ ] Add comprehensive logging
- [ ] Implement monitoring (Prometheus/Grafana)
- [ ] Create automated deployment scripts
- [ ] Add health checks and auto-recovery
- [ ] Create comprehensive test suite
- [ ] Test multi-agent with 230 questions
- [ ] Performance benchmarking
- [ ] Test error handling scenarios
- [ ] Load testing
- [ ] Security audit
- [ ] **BCRA Agent Timeout** - Some payment queries may timeout
- [ ] **No Error Recovery** - Cascading failures in multi-agent queries
- [ ] **Search sometimes returns incorrect data** - Need prompt refinement
- [ ] Implement feedback mechanism
- [ ] Create specialized crypto regulation prompts
- [ ] Add follow-up question support
- [ ] Spanish/English language detection
- [ ] Create "learning mode" for regulations
- [ ] Add voice input/output
- [ ] Mobile app version


## 📝 To Do

- [ ] **Get a domain name** ($1-10) - oraculo.xyz or burocracia.app


## 🔍 Ready for Work



## 🚧 In Progress

- [ ] **Fix mobile copy button** - "Copiar" button on mobile answer screen is not working
	  
	  **Problem Statement**
	  - Copy button exists in TerminalSimple.tsx (lines 761-776) but doesn't work on mobile devices
	  - No visual feedback when copy action fails
	  - May be related to mobile browser clipboard API restrictions
	  
	  **Technical Analysis**
	  - Current implementation uses `navigator.clipboard.writeText()`
	  - Mobile Safari and some Android browsers have strict clipboard permissions
	  - No error handling for failed clipboard operations
	  
	  **Solution Approach**
	  1. Add try-catch block around clipboard operation
	  2. Implement fallback using document.execCommand('copy')
	  3. Add visual feedback (toast notification or button state change)
	  4. Consider using a clipboard library like clipboard.js for better compatibility
	  
	  **Implementation Steps**
	  ```typescript
	  // Add error handling and fallback
	  const handleCopy = async () => {
	try {
	  await navigator.clipboard.writeText(responseText);
	  setCopySuccess(true);
	} catch (err) {
	  // Fallback for mobile
	  const textArea = document.createElement('textarea');
	  textArea.value = responseText;
	  document.body.appendChild(textArea);
	  textArea.select();
	  document.execCommand('copy');
	  document.body.removeChild(textArea);
	}
	  };
	  ```
	  
	  **Testing Requirements**
	  - iOS Safari (iPhone/iPad)
	  - Chrome on Android
	  - Firefox on Android
	  - Test with both HTTP and HTTPS (clipboard API requires HTTPS)
	  
	  **Deployment Process**
	  ```bash
	  # SSH to server
	  cd /opt/proyecto-sting
	  
	  # Rebuild frontend with mobile fixes
	  docker build -t proyecto-sting_frontend \
	--build-arg VITE_API_BASE_URL=http://147.182.248.187:8001 \
	--no-cache ./frontend
	  
	  # Restart frontend container
	  docker-compose up -d frontend
	  ```
	  
	  **Success Criteria**
	  - Copy button works on all major mobile browsers
	  - User receives clear feedback (visual or haptic) when copy succeeds/fails
	  - Graceful fallback for browsers without clipboard API support
	  
	  **Risks & Mitigation**
	  - Risk: HTTPS requirement for clipboard API
	  - Mitigation: Implement fallback method and add HTTPS to production
- [ ] **Fix light mode display** - UI elements look wrong/unreadable in light mode
	  
	  **Problem Statement**
	  - App designed only for dark mode (black background #0a0a0a)
	  - Orange text (#ff6b35) becomes unreadable on light backgrounds
	  - No theme detection or switching capability
	  - Hardcoded colors throughout components
	  
	  **Technical Analysis**
	  - Colors hardcoded in TerminalSimple.tsx styles (lines 381-634)
	  - Background: #0a0a0a, Text: #fff, Accent: #ff6b35
	  - No CSS variables or theme system
	  - Tailwind classes assume dark background
	  
	  **Solution Approach**
	  1. Create CSS variables for all colors
	  2. Implement theme detection using prefers-color-scheme
	  3. Create light theme color palette
	  4. Update all hardcoded colors to use variables
	  5. Test every component in both themes
	  
	  **Implementation Steps**
	  ```css
	  /* Add to index.css */
	  :root {
	/* Dark theme (default) */
	--bg-primary: #0a0a0a;
	--bg-secondary: #1a1a1a;
	--text-primary: #ffffff;
	--text-secondary: #cccccc;
	--accent: #ff6b35;
	--border: #333333;
	  }
	  
	  @media (prefers-color-scheme: light) {
	:root {
	  --bg-primary: #ffffff;
	  --bg-secondary: #f5f5f5;
	  --text-primary: #0a0a0a;
	  --text-secondary: #333333;
	  --accent: #ff4500; /* Darker orange for contrast */
	  --border: #dddddd;
	}
	  }
	  ```
	  
	  **Components to Update**
	  - TerminalSimple.tsx (main container and mobile styles)
	  - QuestionScreen.tsx (input field and buttons)
	  - ExampleGrid.tsx (example buttons)
	  - FlowDiagramSimple.tsx (processing screen)
	  - All inline styles using color values
	  
	  **Testing Requirements**
	  - Toggle OS theme settings (macOS, iOS, Android)
	  - Check contrast ratios (WCAG AA compliance)
	  - Test all interactive states (hover, focus, active)
	  - Verify markdown rendering in light mode
	  - Check example buttons visibility
	  
	  **Deployment Process**
	  ```bash
	  # Same as copy button fix
	  cd /opt/proyecto-sting
	  docker build -t proyecto-sting_frontend \
	--build-arg VITE_API_BASE_URL=http://147.182.248.187:8001 \
	--no-cache ./frontend
	  docker-compose up -d frontend
	  ```
	  
	  **Success Criteria**
	  - App automatically adapts to system theme
	  - All text readable in both themes (contrast ratio ≥ 4.5:1)
	  - No hardcoded colors remain
	  - Smooth theme transitions
	  - Orange accent visible in both themes
	  
	  **Risks & Mitigation**
	  - Risk: Breaking existing dark theme design
	  - Mitigation: Implement incrementally, test thoroughly
	  - Risk: Performance impact from CSS variables
	  - Mitigation: Modern browsers handle this efficiently
- [ ] **Fix keyboard UI overlap** - Examples buttons get squished with "Consultar" button when keyboard appears
	  
	  **Problem Statement**
	  - Virtual keyboard pushes example buttons up
	  - Buttons overlap with "Consultar" button
	  - useKeyboardHeight hook exists but not properly applied
	  - Poor user experience when typing on mobile
	  
	  **Technical Analysis**
	  - useKeyboardHeight.ts hook already implemented
	  - QuestionScreen.tsx doesn't adjust layout based on keyboard height
	  - Fixed positioning causes overlap issues
	  - visualViewport API used for detection
	  
	  **Solution Approach**
	  1. Apply keyboard height to QuestionScreen layout
	  2. Hide examples when input is focused
	  3. Adjust button positions dynamically
	  4. Add smooth transitions for better UX
	  5. Handle both iOS and Android keyboard behaviors
	  
	  **Implementation Steps**
	  ```typescript
	  // In QuestionScreen.tsx
	  const [inputFocused, setInputFocused] = useState(false);
	  const keyboardHeight = useKeyboardHeight();
	  
	  // Adjust container padding
	  <div style={{
	paddingBottom: keyboardHeight > 0 ? `${keyboardHeight}px` : '20px',
	transition: 'padding-bottom 0.3s ease'
	  }}>
	  
	  // Hide examples when keyboard visible
	  {!inputFocused && keyboardHeight === 0 && (
	<ExampleGrid onExampleClick={handleExampleClick} />
	  )}
	  
	  // Input handlers
	  <input
	onFocus={() => setInputFocused(true)}
	onBlur={() => setInputFocused(false)}
	  />
	  ```
	  
	  **Mobile-Specific Considerations**
	  - iOS: Keyboard pushes viewport up
	  - Android: Keyboard overlays content
	  - PWA: Different behavior in standalone mode
	  - Safe areas for devices with notches
	  
	  **Testing Requirements**
	  - iPhone (various models with/without notch)
	  - Android phones (different keyboard apps)
	  - iPad/tablets in portrait and landscape
	  - PWA mode vs browser mode
	  - Different keyboard types (default, numeric, etc.)
	  
	  **CSS Adjustments**
	  ```css
	  /* Add to mobile styles */
	  .question-container {
	min-height: 100vh;
	min-height: 100dvh; /* Dynamic viewport height */
	display: flex;
	flex-direction: column;
	  }
	  
	  .input-area {
	margin-top: auto; /* Push to bottom */
	  }
	  
	  /* Smooth transitions */
	  .examples-grid {
	transition: opacity 0.2s, transform 0.2s;
	  }
	  ```
	  
	  **Deployment Process**
	  ```bash
	  # Standard frontend rebuild
	  cd /opt/proyecto-sting
	  docker build -t proyecto-sting_frontend \
	--build-arg VITE_API_BASE_URL=http://147.182.248.187:8001 \
	--no-cache ./frontend
	  docker-compose up -d frontend
	  
	  # Verify the fix
	  docker logs frontend --tail 50
	  ```
	  
	  **Success Criteria**
	  - No UI overlap when keyboard appears
	  - Smooth transitions when keyboard shows/hides
	  - Input field remains visible above keyboard
	  - Examples hide gracefully when typing
	  - Works on all major mobile browsers
	  
	  **Risks & Mitigation**
	  - Risk: visualViewport not supported in older browsers
	  - Mitigation: Fallback to window resize detection
	  - Risk: Different keyboard behaviors across devices
	  - Mitigation: Test extensively, add device-specific fixes
	  - Risk: Performance impact from constant height calculations
	  - Mitigation: Throttle/debounce height updates


## 🧪 Testing/Review



## ✅ Done

- [x] **Deploy to DigitalOcean** - Live at http://147.182.248.187
- [x] Set up Docker 1-Click Droplet ($12/month)
- [x] Configure all 6 services with Docker Compose
- [x] Set up environment variables
- [x] Configure firewall rules
- [x] Add favicon and Spanish title
- [x] Update header to "ORÁCULO DE LA BUROCRACIA"
- [x] Create microservices architecture with FastAPI
- [x] Build base agent template for all services
- [x] Set up Docker Compose orchestration
- [x] Create Makefile for easy development
- [x] Implement Router service for query routing (96.7% accuracy)
- [x] Create BCRA agent (Central Bank regulations)
- [x] Create Comex agent (Foreign trade)
- [x] Create Senasa agent (Agricultural safety)
- [x] Build Auditor service for response validation
- [x] **Multi-agent queries** (parallel processing)
- [x] **Complete Tavily Search Integration**
- [x] Create search_service.py module
- [x] Add search detection logic (two-tier system)
- [x] Integrate with all agents (BCRA, COMEX, SENASA)
- [x] Add caching layer
- [x] Implement two-tier search (quick + full)
- [x] Add search metadata tracking
- [x] Show search usage in responses
- [x] **Build React frontend with chat interface**
- [x] Create terminal-style UI with ASCII flow
- [x] Display which agents were consulted
- [x] Add response confidence indicators (percentages)
- [x] Show search usage in all responses
- [x] Display search costs when applicable
- [x] Show question on agent processing screen
- [x] Fix mobile example behavior
- [x] Write comprehensive README documentation
- [x] Create test_questions.json with 30 test cases
- [x] Build test_routing.py for routing accuracy testing
- [x] Create routing visualization HTML report
- [x] Test with 230 questions dataset
- [x] Run A/B Test with Real Questions
- [x] Implement cost tracking (shown in each response)
- [x] Two-tier search system for cost optimization
- [x] Search caching to reduce API calls




%% kanban:settings
```
{"kanban-plugin":"board","new-card-insertion-method":"prepend-compact","show-checkboxes":true,"archive-with-date":false,"list-collapse":[false,false,false,false,false,false,false]}
```
%%