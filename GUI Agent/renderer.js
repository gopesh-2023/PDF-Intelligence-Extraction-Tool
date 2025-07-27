window.addEventListener('DOMContentLoaded', () => {
  const openBtn = document.getElementById('open-pdf-btn');
  const pdfViewer = document.getElementById('pdf-viewer');
  const cliInput = document.getElementById('cli-input');
  const cliOutput = document.getElementById('cli-output');
  const themeToggle = document.getElementById('toggle-theme');

  const extractOutlinesBtn = document.getElementById("extract-outlines-btn");
  const outlineResults = document.getElementById("outline-results");

  let currentPdfPath = null;

  themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
  });

  openBtn.addEventListener('click', () => {
    window.electronAPI.selectPDF();
  });

  window.electronAPI.loadPDF((filePath) => {
    openBtn.style.display = 'none';
    pdfViewer.style.display = 'block';
    pdfViewer.src = filePath;
    currentPdfPath = filePath.replace('file://', '');
    console.log("PDF loaded:", currentPdfPath);
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

  extractOutlinesBtn.addEventListener('click', () => {
    console.log("Extract Outlines button clicked ✅");

    if (currentPdfPath) {
      outlineResults.textContent = "";
      window.electronAPI.extractOutlines(currentPdfPath);
    } else {
      alert("Please open a PDF file first.");
    }
  });

  window.electronAPI.onOutlineLog((msg) => {
    outlineResults.textContent += msg + "\n";
  });
});
