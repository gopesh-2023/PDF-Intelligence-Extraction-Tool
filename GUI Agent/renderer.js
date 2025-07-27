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
  const outlineResults = document.getElementById("outline-results");
  const modeButtons = document.querySelectorAll('.mode-button');
  const healthCheckBtn = document.getElementById("health-check-btn");

  let currentPdfPath = null;
  let currentPdfFile = null;
  let currentMode = 'outline'; // 'outline', 'persona', 'semantic'

  // API base URL
  const API_BASE_URL = 'http://localhost:5000';

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
      const modes = ['outline', 'persona', 'semantic'];
      currentMode = modes[index];
      
      // Update button text
      const buttonTexts = ['🧩', '🧠', '🌐'];
      extractOutlinesBtn.textContent = `Extract ${currentMode.charAt(0).toUpperCase() + currentMode.slice(1)}`;
      
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
    // Extract filename from path
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
    cliOutput.value += `\n${result}`;
    cliOutput.scrollTop = cliOutput.scrollHeight;
  });

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
});
