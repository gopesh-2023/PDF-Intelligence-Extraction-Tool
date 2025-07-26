import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import datetime
import queue

try:
    from ttkthemes import ThemedTk
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

# --- Adobe color palette ---
ADOBE_RED = '#B10A1C'  # Darker Adobe red
ADOBE_DARK = '#181818'
ADOBE_LIGHT = '#F5F5F5'
ADOBE_ACCENT = '#FF5252'
ADOBE_TEXT = '#222222'
ADOBE_HEADER_FONT = ('Segoe UI', 18, 'bold')
ADOBE_BODY_FONT = ('Segoe UI', 11)
ADOBE_BUTTON_FONT = ('Segoe UI', 10, 'bold')

DARK_MODE = {
    'bg': '#181818',
    'fg': '#F5F5F5',
    'header_bg': '#2A0A12',
    'header_fg': '#F5F5F5',
    'accent': '#FF5252',
    'tab_bg': '#232323',
    'tab_fg': '#F5F5F5',
    'entry_bg': '#232323',
    'entry_fg': '#F5F5F5',
    'button_bg': '#B10A1C',
    'button_fg': '#F5F5F5',
    'progress': '#B10A1C',
}
LIGHT_MODE = {
    'bg': '#F5F5F5',
    'fg': '#222222',
    'header_bg': '#B10A1C',
    'header_fg': '#FFFFFF',
    'accent': '#FF5252',
    'tab_bg': '#FFFFFF',
    'tab_fg': '#222222',
    'entry_bg': '#FFFFFF',
    'entry_fg': '#222222',
    'button_bg': '#B10A1C',
    'button_fg': '#FFFFFF',
    'progress': '#B10A1C',
}

# --- Tooltip helper ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, font=('Segoe UI', 9))
        label.pack(ipadx=1)
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class PDFExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.dark_mode = False
        self.colors = LIGHT_MODE.copy()
        self.root.title("Adobe PDF Extractor - Offline Edition")
        self.root.geometry("1100x750")
        self.apply_theme()
        self.pdf_files = []
        self.persona_file = None
        self.sbert_model_dir = None
        self.summarizer_model_dir = None
        self.sbert_model = None
        self.summarizer = None
        self.outline_progress = None
        self.persona_progress = None
        self.semantic_progress = None
        self.outline_queue = queue.Queue()
        self.persona_queue = queue.Queue()
        self.semantic_queue = queue.Queue()
        self.setup_ui()

    def apply_theme(self):
        c = self.colors
        self.root.configure(bg=c['bg'])
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=ADOBE_BODY_FONT, padding=[10, 5], background=c['tab_bg'], foreground=c['tab_fg'])
        style.configure('Accent.TButton', foreground=c['button_fg'], background=c['button_bg'], font=ADOBE_BUTTON_FONT)
        style.map('Accent.TButton', background=[('active', c['accent'])])
        style.configure('TLabel', font=ADOBE_BODY_FONT, background=c['bg'], foreground=c['fg'])
        style.configure('TFrame', background=c['bg'])
        style.configure('TLabelFrame', background=c['bg'], foreground=c['fg'])
        style.configure('TButton', font=ADOBE_BUTTON_FONT, background=c['button_bg'], foreground=c['button_fg'])
        style.configure('TProgressbar', thickness=12, background=c['progress'])

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.colors = DARK_MODE.copy() if self.dark_mode else LIGHT_MODE.copy()
        self.apply_theme()
        self.update_all_colors()

    def update_all_colors(self):
        c = self.colors
        # Header
        self.header.configure(bg=c['header_bg'])
        self.logo.configure(bg=c['header_bg'], fg=c['header_fg'])
        self.title_label.configure(bg=c['header_bg'], fg=c['header_fg'])
        self.subtitle_label.configure(bg=c['header_bg'], fg=c['header_fg'])
        # Results areas
        self.outline_results.configure(bg=c['entry_bg'], fg=c['entry_fg'])
        self.persona_results.configure(bg=c['entry_bg'], fg=c['entry_fg'])
        self.semantic_results.configure(bg=c['entry_bg'], fg=c['entry_fg'])
        # Update all labels/buttons/frames recursively
        def update_widget_colors(widget):
            for child in widget.winfo_children():
                # Only set bg/fg for classic Tk widgets
                if isinstance(child, tk.Label):
                    child.configure(bg=c['bg'], fg=c['fg'])
                elif isinstance(child, tk.Frame):
                    child.configure(bg=c['bg'])
                elif isinstance(child, tk.Button):
                    child.configure(bg=c['button_bg'], fg=c['button_fg'])
                # Do NOT set bg/fg for ttk widgets (ttk.Frame, ttk.Label, etc.)
                update_widget_colors(child)
        update_widget_colors(self.root)

    def setup_ui(self):
        c = self.colors
        # Adobe-style header
        self.header = tk.Frame(self.root, bg=c['header_bg'], height=60)
        self.header.pack(fill='x', side='top')
        self.logo = tk.Label(self.header, text='A', font=('Segoe UI', 32, 'bold'), fg=c['header_fg'], bg=c['header_bg'])
        self.logo.pack(side='left', padx=(20, 10), pady=5)
        self.title_label = tk.Label(self.header, text='Adobe PDF Extractor', font=ADOBE_HEADER_FONT, fg=c['header_fg'], bg=c['header_bg'])
        self.title_label.pack(side='left', padx=10, pady=5)
        self.subtitle_label = tk.Label(self.header, text='Offline Edition', font=('Segoe UI', 12, 'italic'), fg=c['header_fg'], bg=c['header_bg'])
        self.subtitle_label.pack(side='left', padx=10, pady=5)
        # Dark mode toggle button
        self.dark_toggle = ttk.Button(self.header, text='🌙 Mode' if not self.dark_mode else '☀️ Light Mode', command=self.toggle_dark_mode, style='Accent.TButton')
        self.dark_toggle.pack(side='right', padx=20)
        ToolTip(self.dark_toggle, "Toggle dark/light mode.")
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        # Create tabs
        self.create_outline_tab()
        self.create_persona_tab()
        self.create_semantic_tab()
        self.create_settings_tab()
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w', font=ADOBE_BODY_FONT)
        self.status_bar.pack(side='bottom', fill='x')
        self.update_all_colors()

    def create_outline_tab(self):
        self.outline_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.outline_tab, text="Outline Extractor")
        title_label = ttk.Label(self.outline_tab, text="PDF Structured Outline Extractor", font=ADOBE_HEADER_FONT, foreground=ADOBE_RED)
        title_label.pack(pady=10)
        desc_label = ttk.Label(self.outline_tab, text="Extract structured outlines from PDFs using font-based analysis and clustering", font=ADOBE_BODY_FONT, wraplength=700)
        desc_label.pack(pady=5)
        file_frame = ttk.LabelFrame(self.outline_tab, text="Input Files", padding=10)
        file_frame.pack(fill='x', padx=10, pady=10)
        btn = ttk.Button(file_frame, text="Select PDF Files", command=self.browse_pdfs_outline, style='Accent.TButton')
        btn.pack(side='left', padx=5)
        ToolTip(btn, "Choose one or more PDF files to extract outlines from.")
        self.outline_pdf_label = ttk.Label(file_frame, text="No files selected", foreground='gray')
        self.outline_pdf_label.pack(side='left', padx=10)
        out_btn = ttk.Button(file_frame, text="Select Output Directory", command=self.browse_output_dir)
        out_btn.pack(side='left', padx=5)
        ToolTip(out_btn, "Choose where to save the extracted outlines.")
        self.outline_output_label = ttk.Label(file_frame, text="Default: outline_extractor/output", foreground='gray')
        self.outline_output_label.pack(side='left', padx=10)
        run_btn = ttk.Button(self.outline_tab, text="Extract Outlines", command=self.run_outline_extraction, style='Accent.TButton')
        run_btn.pack(pady=20)
        ToolTip(run_btn, "Start extracting outlines from the selected PDFs.")
        results_frame = ttk.LabelFrame(self.outline_tab, text="Results", padding=5)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.outline_results = scrolledtext.ScrolledText(results_frame, height=15, font=ADOBE_BODY_FONT, bg='#fff')
        self.outline_results.pack(fill='both', expand=True)
        self.outline_progress = ttk.Progressbar(results_frame, orient='horizontal', mode='determinate', length=400)
        self.outline_progress.pack(pady=5)
        self.outline_progress['value'] = 0
        self.outline_progress.pack_forget()

    def create_persona_tab(self):
        self.persona_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.persona_tab, text="Persona Insights")
        title_label = ttk.Label(self.persona_tab, text="Persona-Driven Insight Extractor", font=ADOBE_HEADER_FONT, foreground=ADOBE_RED)
        title_label.pack(pady=10)
        desc_label = ttk.Label(self.persona_tab, text="Extract insights from PDFs based on specific personas and job requirements", font=ADOBE_BODY_FONT, wraplength=700)
        desc_label.pack(pady=5)
        input_frame = ttk.LabelFrame(self.persona_tab, text="Input Files", padding=10)
        input_frame.pack(fill='x', padx=10, pady=10)
        pdf_row = ttk.Frame(input_frame)
        pdf_row.pack(fill='x', pady=5)
        pdf_btn = ttk.Button(pdf_row, text="Browse", command=self.browse_pdfs_persona, style='Accent.TButton')
        pdf_btn.pack(side='left', padx=5)
        ToolTip(pdf_btn, "Select PDF files for persona-based extraction.")
        self.persona_pdf_label = ttk.Label(pdf_row, text="No files selected", foreground='gray')
        self.persona_pdf_label.pack(side='left', padx=10)
        persona_row = ttk.Frame(input_frame)
        persona_row.pack(fill='x', pady=5)
        persona_btn = ttk.Button(persona_row, text="Browse", command=self.browse_persona, style='Accent.TButton')
        persona_btn.pack(side='left', padx=5)
        ToolTip(persona_btn, "Select a persona.json file.")
        self.persona_file_label = ttk.Label(persona_row, text="No file selected", foreground='gray')
        self.persona_file_label.pack(side='left', padx=10)
        models_frame = ttk.LabelFrame(self.persona_tab, text="AI Models", padding=10)
        models_frame.pack(fill='x', padx=10, pady=10)
        sbert_row = ttk.Frame(models_frame)
        sbert_row.pack(fill='x', pady=5)
        sbert_btn = ttk.Button(sbert_row, text="Browse", command=self.browse_sbert_model, style='Accent.TButton')
        sbert_btn.pack(side='left', padx=5)
        ToolTip(sbert_btn, "Select the SBERT model directory.")
        self.sbert_label = ttk.Label(sbert_row, text="No model selected", foreground='gray')
        self.sbert_label.pack(side='left', padx=10)
        sum_row = ttk.Frame(models_frame)
        sum_row.pack(fill='x', pady=5)
        sum_btn = ttk.Button(sum_row, text="Browse (Optional)", command=self.browse_summarizer_model, style='Accent.TButton')
        sum_btn.pack(side='left', padx=5)
        ToolTip(sum_btn, "Select the summarizer model directory (optional).")
        self.summarizer_label = ttk.Label(sum_row, text="No model selected (optional)", foreground='gray')
        self.summarizer_label.pack(side='left', padx=10)
        run_btn = ttk.Button(self.persona_tab, text="Extract Insights", command=self.run_persona_extraction, style='Accent.TButton')
        run_btn.pack(pady=20)
        ToolTip(run_btn, "Start extracting persona-based insights from the selected PDFs.")
        results_frame = ttk.LabelFrame(self.persona_tab, text="Results", padding=5)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.persona_results = scrolledtext.ScrolledText(results_frame, height=18, font=ADOBE_BODY_FONT, bg='#fff', wrap='word')
        self.persona_results.pack(fill='both', expand=True)
        self.persona_progress = ttk.Progressbar(results_frame, orient='horizontal', mode='determinate', length=400)
        self.persona_progress.pack(pady=5)
        self.persona_progress['value'] = 0
        self.persona_progress.pack_forget()

    def create_semantic_tab(self):
        self.semantic_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.semantic_tab, text="Semantic Outline")
        title_label = ttk.Label(self.semantic_tab, text="Semantic PDF Outline Extractor", font=ADOBE_HEADER_FONT, foreground=ADOBE_RED)
        title_label.pack(pady=10)
        desc_label = ttk.Label(self.semantic_tab, text="Extract semantic outlines from PDFs using SBERT embeddings and clustering", font=ADOBE_BODY_FONT, wraplength=700)
        desc_label.pack(pady=5)
        file_frame = ttk.LabelFrame(self.semantic_tab, text="Input Files", padding=10)
        file_frame.pack(fill='x', padx=10, pady=10)
        btn = ttk.Button(file_frame, text="Select PDF Files", command=self.browse_pdfs_semantic, style='Accent.TButton')
        btn.pack(side='left', padx=5)
        ToolTip(btn, "Choose one or more PDF files for semantic outline extraction.")
        self.semantic_pdf_label = ttk.Label(file_frame, text="No files selected", foreground='gray')
        self.semantic_pdf_label.pack(side='left', padx=10)
        model_frame = ttk.LabelFrame(self.semantic_tab, text="AI Model", padding=10)
        model_frame.pack(fill='x', padx=10, pady=10)
        btn2 = ttk.Button(model_frame, text="Select SBERT Model", command=self.browse_sbert_model_semantic, style='Accent.TButton')
        btn2.pack(side='left', padx=5)
        ToolTip(btn2, "Select the SBERT model directory for semantic outline extraction.")
        self.semantic_sbert_label = ttk.Label(model_frame, text="No model selected", foreground='gray')
        self.semantic_sbert_label.pack(side='left', padx=10)
        run_btn = ttk.Button(self.semantic_tab, text="Extract Semantic Outlines", command=self.run_semantic_extraction, style='Accent.TButton')
        run_btn.pack(pady=20)
        ToolTip(run_btn, "Start extracting semantic outlines from the selected PDFs.")
        results_frame = ttk.LabelFrame(self.semantic_tab, text="Results", padding=5)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.semantic_results = scrolledtext.ScrolledText(results_frame, height=15, font=ADOBE_BODY_FONT, bg='#fff')
        self.semantic_results.pack(fill='both', expand=True)
        self.semantic_progress = ttk.Progressbar(results_frame, orient='horizontal', mode='determinate', length=400)
        self.semantic_progress.pack(pady=5)
        self.semantic_progress['value'] = 0
        self.semantic_progress.pack_forget()

    def create_settings_tab(self):
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        title_label = ttk.Label(self.settings_tab, text="Application Settings", font=ADOBE_HEADER_FONT, foreground=ADOBE_RED)
        title_label.pack(pady=10)
        model_frame = ttk.LabelFrame(self.settings_tab, text="Model Management", padding=10)
        model_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(model_frame, text="Download Models (requires internet):", font=ADOBE_BODY_FONT).pack(anchor='w')
        sbert_frame = ttk.Frame(model_frame)
        sbert_frame.pack(fill='x', pady=5)
        sbert_btn = ttk.Button(sbert_frame, text="Download SBERT Model (all-MiniLM-L12-v2)", command=self.download_sbert_model, style='Accent.TButton')
        sbert_btn.pack(side='left', padx=5)
        ToolTip(sbert_btn, "Download the SBERT model for semantic and persona extraction.")
        sum_frame = ttk.Frame(model_frame)
        sum_frame.pack(fill='x', pady=5)
        sum_btn = ttk.Button(sum_frame, text="Download Summarizer Model (BART)", command=self.download_summarizer_model, style='Accent.TButton')
        sum_btn.pack(side='left', padx=5)
        ToolTip(sum_btn, "Download the summarizer model for persona extraction (optional).")
        info_frame = ttk.LabelFrame(self.settings_tab, text="Application Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        info_text = """
This application provides three different PDF extraction methods:\n\n1. Outline Extractor: Uses font-based analysis to extract document structure\n2. Persona Insights: Extracts relevant sections based on specific personas and job requirements\n3. Semantic Outline: Uses AI embeddings to create semantic document outlines\n\nAll processing is done offline once models are downloaded.
        """
        info_label = ttk.Label(info_frame, text=info_text, justify='left', wraplength=700)
        info_label.pack(anchor='w')
    # File browsing methods
    def browse_pdfs_outline(self):
        files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF files", "*.pdf")])
        if files:
            self.outline_pdfs = list(files)
            self.outline_pdf_label.config(text=f"{len(self.outline_pdfs)} file(s) selected", foreground='black')
            
    def browse_pdfs_persona(self):
        files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF files", "*.pdf")])
        if files:
            self.persona_pdfs = list(files)
            self.persona_pdf_label.config(text=f"{len(self.persona_pdfs)} file(s) selected", foreground='black')
            
    def browse_pdfs_semantic(self):
        files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF files", "*.pdf")])
        if files:
            self.semantic_pdfs = list(files)
            self.semantic_pdf_label.config(text=f"{len(self.semantic_pdfs)} file(s) selected", foreground='black')
            
    def browse_persona(self):
        file = filedialog.askopenfilename(title="Select persona.json", filetypes=[("JSON files", "*.json")])
        if file:
            self.persona_file = file
            self.persona_file_label.config(text=os.path.basename(file), foreground='black')
            
    def browse_sbert_model(self):
        directory = filedialog.askdirectory(title="Select SBERT model directory")
        if directory:
            self.sbert_model_dir = directory
            self.sbert_label.config(text=os.path.basename(directory), foreground='black')
            
    def browse_sbert_model_semantic(self):
        directory = filedialog.askdirectory(title="Select SBERT model directory")
        if directory:
            self.semantic_sbert_model_dir = directory
            self.semantic_sbert_label.config(text=os.path.basename(directory), foreground='black')
            
    def browse_summarizer_model(self):
        directory = filedialog.askdirectory(title="Select summarizer model directory")
        if directory:
            self.summarizer_model_dir = directory
            self.summarizer_label.config(text=os.path.basename(directory), foreground='black')
            
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.outline_output_dir = directory
            self.outline_output_label.config(text=directory, foreground='black')
            
    # Model download methods
    def download_sbert_model(self):
        def download():
            try:
                self.status_var.set("Downloading SBERT model...")
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L12-v2')
                
                # Save to a default location
                default_path = os.path.join(os.path.dirname(__file__), 'models', 'sbert_model')
                os.makedirs(os.path.dirname(default_path), exist_ok=True)
                model.save(default_path)
                
                self.status_var.set("SBERT model downloaded successfully!")
                messagebox.showinfo("Success", f"SBERT model downloaded to: {default_path}")
            except Exception as e:
                self.status_var.set("Download failed!")
                messagebox.showerror("Error", f"Failed to download SBERT model: {str(e)}")
                
        threading.Thread(target=download, daemon=True).start()
        
    def download_summarizer_model(self):
        def download():
            try:
                self.status_var.set("Downloading summarizer model...")
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                
                model_name = 'facebook/bart-large-cnn'
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                
                # Save to a default location
                default_path = os.path.join(os.path.dirname(__file__), 'models', 'summarizer_model')
                os.makedirs(os.path.dirname(default_path), exist_ok=True)
                model.save_pretrained(default_path)
                tokenizer.save_pretrained(default_path)
                
                self.status_var.set("Summarizer model downloaded successfully!")
                messagebox.showinfo("Success", f"Summarizer model downloaded to: {default_path}")
            except Exception as e:
                self.status_var.set("Download failed!")
                messagebox.showerror("Error", f"Failed to download summarizer model: {str(e)}")
                
        threading.Thread(target=download, daemon=True).start()
        
    # Extraction methods with improved progress and persona summary
    def run_outline_extraction(self):
        if not hasattr(self, 'outline_pdfs') or not self.outline_pdfs:
            messagebox.showerror("Error", "Please select PDF files first.")
            return
        self.outline_progress['value'] = 0
        self.outline_progress['maximum'] = len(self.outline_pdfs)
        self.outline_progress.pack()
        self.outline_results.delete(1.0, tk.END)
        self.status_var.set("Running outline extraction...")
        def extract(queue_):
            try:
                from outline_extractor.utils import extract_headings
                results = []
                for idx, pdf_path in enumerate(self.outline_pdfs):
                    try:
                        import fitz
                        doc = fitz.open(pdf_path)
                        title, outline = extract_headings(doc)
                        result = {
                            "file": os.path.basename(pdf_path),
                            "title": title,
                            "outline": outline
                        }
                        results.append(result)
                        output_dir = getattr(self, 'outline_output_dir', 'outline_extractor/output')
                        os.makedirs(output_dir, exist_ok=True)
                        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.json")
                        with open(output_file, 'w') as f:
                            json.dump(result, f, indent=2)
                    except Exception as e:
                        results.append({"file": os.path.basename(pdf_path), "error": str(e)})
                    queue_.put(('progress', idx + 1))
                queue_.put(('log', "Outline Extraction Results:\n\n"))
                for result in results:
                    queue_.put(('log', f"File: {result['file']}\n"))
                    if 'error' in result:
                        queue_.put(('log', f"Error: {result['error']}\n"))
                    else:
                        queue_.put(('log', f"Title: {result['title']}\n"))
                        queue_.put(('log', f"Headings: {len(result['outline'])}\n"))
                        for item in result['outline'][:5]:
                            queue_.put(('log', f"  - {item['text']} (Page {item['page']})\n"))
                    queue_.put(('log', "\n"))
                queue_.put(('done', None))
            except Exception as e:
                queue_.put(('error', str(e)))
        def process_queue():
            try:
                while True:
                    msg, data = self.outline_queue.get_nowait()
                    if msg == 'progress':
                        self.outline_progress['value'] = data
                        self.outline_progress.update()
                    elif msg == 'log':
                        self.outline_results.insert(tk.END, data)
                        self.outline_results.see(tk.END)
                    elif msg == 'done':
                        self.status_var.set("Outline extraction completed!")
                        self.outline_progress.pack_forget()
                        messagebox.showinfo("Success", "Outline extraction completed successfully!")
                        return
                    elif msg == 'error':
                        self.status_var.set("Extraction failed!")
                        self.outline_progress.pack_forget()
                        messagebox.showerror("Error", f"Outline extraction failed: {data}")
                        return
            except queue.Empty:
                self.root.after(100, process_queue)
        threading.Thread(target=extract, args=(self.outline_queue,), daemon=True).start()
        self.root.after(100, process_queue)
    def run_persona_extraction(self):
        if not hasattr(self, 'persona_pdfs') or not self.persona_pdfs:
            messagebox.showerror("Error", "Please select PDF files first.")
            return
        if not self.persona_file:
            messagebox.showerror("Error", "Please select persona.json file first.")
            return
        if not self.sbert_model_dir:
            messagebox.showerror("Error", "Please select SBERT model directory first.")
            return
        self.persona_progress['value'] = 0
        self.persona_progress['maximum'] = len(self.persona_pdfs)
        self.persona_progress.pack()
        self.persona_results.delete(1.0, tk.END)
        self.status_var.set("Running persona extraction...")
        def extract(queue_):
            try:
                from persona_insight_extractor.heading_utils import extract_headings_and_text
                from persona_insight_extractor.semantic_utils import rank_sections_by_similarity
                with open(self.persona_file, 'r') as f:
                    persona_data = json.load(f)
                persona = persona_data["persona"]
                job = persona_data["job_to_be_done"]
                combined_query = f"{persona}. Task: {job}"
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(self.sbert_model_dir)
                all_sections = []
                for idx, pdf_path in enumerate(self.persona_pdfs):
                    try:
                        sections = extract_headings_and_text(pdf_path, os.path.basename(pdf_path))
                        all_sections.extend(sections)
                    except Exception as e:
                        queue_.put(('log', f"Error processing {os.path.basename(pdf_path)}: {str(e)}\n"))
                    queue_.put(('progress', idx + 1))
                if not all_sections:
                    queue_.put(('log', "No sections extracted from PDFs.\n"))
                    queue_.put(('done', None))
                    return
                ranked = rank_sections_by_similarity(all_sections, combined_query)
                # Show full summary/text for each section
                queue_.put(('log', f"Persona: {persona}\n"))
                queue_.put(('log', f"Job: {job}\n\n"))
                queue_.put(('log', "Top relevant sections (full text):\n\n"))
                for i, item in enumerate(ranked[:10]):
                    queue_.put(('log', f"{i+1}. {item['title']}\n"))
                    queue_.put(('log', f"   Document: {item['document']} (Page {item['page']})\n"))
                    queue_.put(('log', f"   Text: {item['text']}\n\n"))
                output = {
                    "metadata": {
                        "persona": persona,
                        "job_to_be_done": job,
                        "timestamp": datetime.datetime.now().isoformat()
                    },
                    "sections": ranked[:10]
                }
                output_file = os.path.join('persona_insight_extractor/output', 'gui_output.json')
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w') as f:
                    json.dump(output, f, indent=2)
                queue_.put(('done', None))
            except Exception as e:
                queue_.put(('error', str(e)))
        def process_queue():
            try:
                while True:
                    msg, data = self.persona_queue.get_nowait()
                    if msg == 'progress':
                        self.persona_progress['value'] = data
                        self.persona_progress.update()
                    elif msg == 'log':
                        self.persona_results.insert(tk.END, data)
                        self.persona_results.see(tk.END)
                    elif msg == 'done':
                        self.status_var.set("Persona extraction completed!")
                        self.persona_progress.pack_forget()
                        messagebox.showinfo("Success", "Persona extraction completed successfully!")
                        return
                    elif msg == 'error':
                        self.status_var.set("Extraction failed!")
                        self.persona_progress.pack_forget()
                        messagebox.showerror("Error", f"Persona extraction failed: {data}")
                        return
            except queue.Empty:
                self.root.after(100, process_queue)
        threading.Thread(target=extract, args=(self.persona_queue,), daemon=True).start()
        self.root.after(100, process_queue)
    def run_semantic_extraction(self):
        if not hasattr(self, 'semantic_pdfs') or not self.semantic_pdfs:
            messagebox.showerror("Error", "Please select PDF files first.")
            return
        if not hasattr(self, 'semantic_sbert_model_dir') or not self.semantic_sbert_model_dir:
            messagebox.showerror("Error", "Please select SBERT model directory first.")
            return
        self.semantic_progress['value'] = 0
        self.semantic_progress['maximum'] = len(self.semantic_pdfs)
        self.semantic_progress.pack()
        self.semantic_results.delete(1.0, tk.END)
        self.status_var.set("Running semantic extraction...")
        def extract(queue_):
            try:
                from semantic_outline_extractor.utils import extract_outline
                results = []
                for idx, pdf_path in enumerate(self.semantic_pdfs):
                    try:
                        title, outline = extract_outline(pdf_path)
                        result = {
                            "file": os.path.basename(pdf_path),
                            "title": title,
                            "outline": outline
                        }
                        results.append(result)
                        output_dir = 'semantic_outline_extractor/output'
                        os.makedirs(output_dir, exist_ok=True)
                        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.json")
                        with open(output_file, 'w') as f:
                            json.dump({"title": title, "outline": outline}, f, indent=2)
                    except Exception as e:
                        results.append({"file": os.path.basename(pdf_path), "error": str(e)})
                    queue_.put(('progress', idx + 1))
                queue_.put(('log', "Semantic Outline Extraction Results:\n\n"))
                for result in results:
                    queue_.put(('log', f"File: {result['file']}\n"))
                    if 'error' in result:
                        queue_.put(('log', f"Error: {result['error']}\n"))
                    else:
                        queue_.put(('log', f"Title: {result['title']}\n"))
                        queue_.put(('log', f"Semantic Headings: {len(result['outline'])}\n"))
                        for item in result['outline'][:5]:
                            queue_.put(('log', f"  - {item['text']} (Page {item['page']})\n"))
                    queue_.put(('log', "\n"))
                queue_.put(('done', None))
            except Exception as e:
                queue_.put(('error', str(e)))
        def process_queue():
            try:
                while True:
                    msg, data = self.semantic_queue.get_nowait()
                    if msg == 'progress':
                        self.semantic_progress['value'] = data
                        self.semantic_progress.update()
                    elif msg == 'log':
                        self.semantic_results.insert(tk.END, data)
                        self.semantic_results.see(tk.END)
                    elif msg == 'done':
                        self.status_var.set("Semantic extraction completed!")
                        self.semantic_progress.pack_forget()
                        messagebox.showinfo("Success", "Semantic extraction completed successfully!")
                        return
                    elif msg == 'error':
                        self.status_var.set("Extraction failed!")
                        self.semantic_progress.pack_forget()
                        messagebox.showerror("Error", f"Semantic extraction failed: {data}")
                        return
            except queue.Empty:
                self.root.after(100, process_queue)
        threading.Thread(target=extract, args=(self.semantic_queue,), daemon=True).start()
        self.root.after(100, process_queue)

def main():
    root = tk.Tk()
    app = PDFExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 