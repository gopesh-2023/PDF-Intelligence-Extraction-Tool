window.addEventListener('DOMContentLoaded', () => {
  const openBtn = document.getElementById('open-pdf-btn');
  const pdfViewer = document.getElementById('pdf-viewer');
  const pdfViewerContainer = document.getElementById('pdf-viewer-container');
  const pdfFilename = document.getElementById('pdf-filename');
  const closePdfBtn = document.getElementById('close-pdf-btn');
  const cliInput = document.getElementById('cli-input');
  const cliOutput = document.getElementById('cli-output');
  const themeToggle = document.getElementById('toggle-theme');

  const extractOutlinesBtn = document.getElementById("extract-outlines-btn");
  const analyzeTextBtn = document.getElementById("analyze-text-btn");
  const extractEntitiesBtn = document.getElementById("extract-entities-btn");
  const outlineResults = document.getElementById("outline-results");
  const modeButtons = document.querySelectorAll('.mode-button');
  const healthCheckBtn = document.getElementById("health-check-btn");

  let currentPdfPath = null;
  let currentPdfFile = null;
  let currentMode = 'outline'; // 'outline', 'persona', 'semantic', 'multilingual'

  // API base URL
  const API_BASE_URL = 'http://127.0.0.1:5000';

  themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
  });

  // Mode button handling
  modeButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
      // Remove active class from all buttons
      modeButtons.forEach(btn => btn.classList.remove('active'));
      // Add active class to clicked button
      button.classList.add('active');
      
      // Set current mode
      const modes = ['outline', 'persona', 'semantic', 'multilingual'];
      currentMode = modes[index];
      
      // Update button text and show/hide spaCy buttons
      if (currentMode === 'multilingual') {
        extractOutlinesBtn.style.display = 'none';
        analyzeTextBtn.style.display = 'inline-block';
        extractEntitiesBtn.style.display = 'inline-block';
      } else {
        extractOutlinesBtn.style.display = 'inline-block';
        analyzeTextBtn.style.display = 'none';
        extractEntitiesBtn.style.display = 'none';
        extractOutlinesBtn.textContent = `Extract ${currentMode.charAt(0).toUpperCase() + currentMode.slice(1)}`;
      }
      
      console.log(`Switched to ${currentMode} mode`);
    });
  });

  // Set default mode
  modeButtons[0].classList.add('active');

  // Health check functionality
  healthCheckBtn.addEventListener('click', async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      if (response.ok) {
        const health = await response.json();
        alert(`API Status: ${health.status}\nOutline: ${health.outline_extractor}\nPersona: ${health.persona_extractor}\nSemantic: ${health.semantic_extractor}`);
      } else {
        alert('API server is not responding');
      }
    } catch (error) {
      alert('Cannot connect to API server. Make sure it\'s running on localhost:5000');
    }
  });

  // Close PDF functionality
  closePdfBtn.addEventListener('click', () => {
    // Reset state
    currentPdfPath = null;
    currentPdfFile = null;
    
    // Show open button, hide PDF viewer
    openBtn.style.display = 'block';
    pdfViewerContainer.style.display = 'none';
    
    // Clear results
    outlineResults.textContent = '';
    
    console.log("PDF closed");
  });

  openBtn.addEventListener('click', () => {
    window.electronAPI.selectPDF();
  });

  window.electronAPI.loadPDF((filePath) => {
    // filename from path
    const filename = filePath.split('/').pop().split('\\').pop();
    pdfFilename.textContent = filename;
    
    // Show PDF viewer, hide open button
    openBtn.style.display = 'none';
    pdfViewerContainer.style.display = 'block';
    pdfViewer.src = filePath;
    currentPdfPath = filePath.replace('file://', '');
    
    // Convert file path to File object for API calls
    fetch(filePath)
      .then(response => response.blob())
      .then(blob => {
        currentPdfFile = new File([blob], filename, { type: 'application/pdf' });
        console.log("PDF loaded:", currentPdfPath);
      })
      .catch(error => {
        console.error("Error loading PDF file:", error);
      });
  });

  cliInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const cmd = cliInput.value.trim();
      if (cmd !== '') {
        cliOutput.value += `\n>>> ${cmd}`;
        window.electronAPI.sendCommand(cmd);
        cliInput.value = '';
      }
    }
  });

  window.electronAPI.onCommandResult((result) => {
    if (result.trim() === "__CLEAR_TERMINAL__") {
      cliOutput.value = '';
    } else {
      cliOutput.value += `\n${result}`;
    }
    cliOutput.scrollTop = cliOutput.scrollHeight;
  });

  // Show welcome message and available commands
  cliOutput.value = `>>> CLI Ready - Enhanced PDF Processing Terminal

📋 Available Commands:
  status          - Check API server status
  help            - Show all available commands
  list-pdfs       - List available PDF files
  outline <file>  - Extract basic outline from PDF
  persona <file>  - Extract persona-based insights
  semantic <file> - Extract semantic outline from PDF

💡 Try: help
`;

  // API call functions
  async function callOutlineAPI() {
    if (!currentPdfFile) {
      throw new Error("No PDF file loaded");
    }

    const formData = new FormData();
    formData.append('pdf', currentPdfFile);

    const response = await fetch(`${API_BASE_URL}/api/outline`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async function callPersonaAPI() {
    if (!currentPdfFile) {
      throw new Error("No PDF file loaded");
    }

    const formData = new FormData();
    formData.append('pdf', currentPdfFile);
    formData.append('persona', JSON.stringify({
      persona: "PDF Analyst",
      job_to_be_done: "Extract key insights and structure from this document"
    }));

    const response = await fetch(`${API_BASE_URL}/api/persona`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async function callSemanticAPI() {
    if (!currentPdfFile) {
      throw new Error("No PDF file loaded");
    }

    const formData = new FormData();
    formData.append('pdf', currentPdfFile);

    const response = await fetch(`${API_BASE_URL}/api/semantic-outline`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  extractOutlinesBtn.addEventListener('click', async () => {
    console.log(`Extract ${currentMode} button clicked ✅`);

    if (!currentPdfFile) {
      alert("Please open a PDF file first.");
      return;
    }

    // Show loading state
    const originalText = extractOutlinesBtn.textContent;
    extractOutlinesBtn.textContent = "🔄 Processing...";
    extractOutlinesBtn.disabled = true;
    
    outlineResults.textContent = "Processing your PDF... Please wait.\n";
    
    try {
      let result;
      
      switch (currentMode) {
        case 'outline':
          result = await callOutlineAPI();
          break;
        case 'persona':
          result = await callPersonaAPI();
          break;
        case 'semantic':
          result = await callSemanticAPI();
          break;
        default:
          throw new Error(`Unknown mode: ${currentMode}`);
      }

      // Display results
      if (result.error) {
        outlineResults.innerHTML = `<span class="error">❌ Error: ${result.error}</span>\n`;
      } else {
        outlineResults.innerHTML = `<span class="success">✅ ${currentMode.charAt(0).toUpperCase() + currentMode.slice(1)} extraction completed successfully!</span>\n\n<pre>${JSON.stringify(result, null, 2)}</pre>`;
      }
      
    } catch (error) {
      console.error('API call failed:', error);
      outlineResults.innerHTML = `<span class="error">❌ Error: ${error.message}</span>\n\nPlease check that the API server is running on localhost:5000`;
    } finally {
      // Restore button state
      extractOutlinesBtn.textContent = originalText;
      extractOutlinesBtn.disabled = false;
    }
  });

  // Keep the old outline log handler for compatibility
  window.electronAPI.onOutlineLog((msg) => {
    outlineResults.textContent += msg + "\n";
  });

  // spaCy Multilingual Analysis Functions
  async function callSpacyAnalyzeAPI(text) {
    const response = await fetch(`${API_BASE_URL}/api/spacy/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async function callSpacyEntitiesAPI(text) {
    const response = await fetch(`${API_BASE_URL}/api/spacy/entities`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // Extract text from PDF for spaCy analysis
  async function extractTextFromPDF() {
    if (!currentPdfFile) {
      throw new Error("No PDF file loaded");
    }

    // For now, we'll use a simple approach - extract text from the first few pages
    // In a full implementation, you'd want to extract all text from the PDF
    const formData = new FormData();
    formData.append('pdf', currentPdfFile);

    // Use the outline extractor to get text content
    const response = await fetch(`${API_BASE_URL}/api/outline`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // Combine all text from the outline
    let fullText = "";
    if (result.outline && Array.isArray(result.outline)) {
      for (const section of result.outline) {
        if (section.text) {
          fullText += section.text + " ";
        }
      }
    }
    
    return fullText || "No text content found in PDF";
  }

  // spaCy button event listeners
  analyzeTextBtn.addEventListener('click', async () => {
    console.log("Analyze Text button clicked ✅");

    if (!currentPdfFile) {
      alert("Please open a PDF file first.");
      return;
    }

    // Show loading state
    const originalText = analyzeTextBtn.textContent;
    analyzeTextBtn.textContent = "🔄 Analyzing...";
    analyzeTextBtn.disabled = true;
    
    outlineResults.textContent = "Analyzing PDF text with spaCy... Please wait.\n";
    
    try {
      // Extract text from PDF
      const pdfText = await extractTextFromPDF();
      
      // Analyze with spaCy
      const result = await callSpacyAnalyzeAPI(pdfText);

      // Display results
      if (result.error) {
        outlineResults.innerHTML = `<span class="error">❌ Error: ${result.error}</span>\n`;
      } else {
        const analysis = result.analysis;
        const keyPhrases = result.key_phrases;
        
        outlineResults.innerHTML = `
          <span class="success">✅ Multilingual Analysis completed!</span>
          
          <h4>📊 Text Analysis:</h4>
          <ul>
            <li><strong>Language Detected:</strong> ${analysis.language}</li>
            <li><strong>Sentences:</strong> ${analysis.sentences}</li>
            <li><strong>Tokens:</strong> ${analysis.tokens}</li>
            <li><strong>Named Entities:</strong> ${analysis.entities}</li>
            <li><strong>Noun Phrases:</strong> ${analysis.noun_phrases}</li>
          </ul>
          
          <h4>🔑 Key Phrases:</h4>
          <ul>
            ${keyPhrases.map(phrase => `<li>${phrase}</li>`).join('')}
          </ul>
          
          <h4>🏷️ Entity Types:</h4>
          <ul>
            ${Object.entries(analysis.entity_types).map(([type, count]) => 
              `<li><strong>${type}:</strong> ${count}</li>`
            ).join('')}
          </ul>
          
          <h4>📝 Key Entities:</h4>
          <ul>
            ${analysis.key_entities.map(entity => `<li>${entity}</li>`).join('')}
          </ul>
        `;
      }
      
    } catch (error) {
      console.error('spaCy analysis failed:', error);
      outlineResults.innerHTML = `<span class="error">❌ Error: ${error.message}</span>\n\nPlease check that the API server is running and spaCy is available`;
    } finally {
      // Restore button state
      analyzeTextBtn.textContent = originalText;
      analyzeTextBtn.disabled = false;
    }
  });

  extractEntitiesBtn.addEventListener('click', async () => {
    console.log("Extract Entities button clicked ✅");

    if (!currentPdfFile) {
      alert("Please open a PDF file first.");
      return;
    }

    // Show loading state
    const originalText = extractEntitiesBtn.textContent;
    extractEntitiesBtn.textContent = "🔄 Extracting...";
    extractEntitiesBtn.disabled = true;
    
    outlineResults.textContent = "Extracting named entities from PDF... Please wait.\n";
    
    try {
      // Extract text from PDF
      const pdfText = await extractTextFromPDF();
      
      // Extract entities with spaCy
      const result = await callSpacyEntitiesAPI(pdfText);

      // Display results
      if (result.error) {
        outlineResults.innerHTML = `<span class="error">❌ Error: ${result.error}</span>\n`;
      } else {
        const entities = result.entities;
        
        // Group entities by type
        const entityGroups = {};
        entities.forEach(entity => {
          if (!entityGroups[entity.label]) {
            entityGroups[entity.label] = [];
          }
          entityGroups[entity.label].push(entity.text);
        });
        
        outlineResults.innerHTML = `
          <span class="success">✅ Named Entity Extraction completed!</span>
          
          <h4>🏷️ Named Entities Found (${entities.length} total):</h4>
          ${Object.entries(entityGroups).map(([type, texts]) => `
            <div style="margin-bottom: 15px;">
              <h5>${type.toUpperCase()} (${texts.length}):</h5>
              <ul>
                ${texts.map(text => `<li>${text}</li>`).join('')}
              </ul>
            </div>
          `).join('')}
        `;
      }
      
    } catch (error) {
      console.error('Entity extraction failed:', error);
      outlineResults.innerHTML = `<span class="error">❌ Error: ${error.message}</span>\n\nPlease check that the API server is running and spaCy is available`;
    } finally {
      // Restore button state
      extractEntitiesBtn.textContent = originalText;
      extractEntitiesBtn.disabled = false;
    }
  });
});
