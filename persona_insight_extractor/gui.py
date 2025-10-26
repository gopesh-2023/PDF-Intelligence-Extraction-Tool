import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import threading

# Try to import SentenceTransformer from a local directory
from sentence_transformers import SentenceTransformer, util
from heading_utils import extract_headings_and_text
from semantic_utils import rank_sections_by_similarity

class PersonaInsightGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Persona Insight Extractor (Offline)")
        self.pdf_files = []
        self.persona_file = None
        self.model_dir = None
        self.model = None
        self.sections = []
        self.result = None
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Select PDF files:").grid(row=0, column=0, sticky="w")
        tk.Button(frame, text="Browse", command=self.browse_pdfs).grid(row=0, column=1)
        self.pdf_label = tk.Label(frame, text="No files selected", fg="gray")
        self.pdf_label.grid(row=0, column=2, sticky="w")

        tk.Label(frame, text="Select persona.json:").grid(row=1, column=0, sticky="w")
        tk.Button(frame, text="Browse", command=self.browse_persona).grid(row=1, column=1)
        self.persona_label = tk.Label(frame, text="No file selected", fg="gray")
        self.persona_label.grid(row=1, column=2, sticky="w")

        tk.Label(frame, text="Local SBERT model directory:").grid(row=2, column=0, sticky="w")
        tk.Button(frame, text="Browse", command=self.browse_model).grid(row=2, column=1)
        self.model_label = tk.Label(frame, text="No directory selected", fg="gray")
        self.model_label.grid(row=2, column=2, sticky="w")

        tk.Button(frame, text="Run Extraction", command=self.run_extraction).grid(row=3, column=0, columnspan=2, pady=10)
        self.status_label = tk.Label(frame, text="Idle", fg="blue")
        self.status_label.grid(row=3, column=2, sticky="w")

        tk.Label(frame, text="Results:").grid(row=4, column=0, sticky="nw")
        self.result_text = scrolledtext.ScrolledText(frame, width=80, height=20)
        self.result_text.grid(row=4, column=1, columnspan=2, pady=5)
        tk.Button(frame, text="Save Results", command=self.save_results).grid(row=5, column=2, sticky="e")

    def browse_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.pdf_files = list(files)
            self.pdf_label.config(text=f"{len(self.pdf_files)} file(s) selected", fg="black")
        else:
            self.pdf_label.config(text="No files selected", fg="gray")

    def browse_persona(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file:
            self.persona_file = file
            self.persona_label.config(text=os.path.basename(file), fg="black")
        else:
            self.persona_label.config(text="No file selected", fg="gray")

    def browse_model(self):
        directory = filedialog.askdirectory()
        if directory:
            self.model_dir = directory
            self.model_label.config(text=directory, fg="black")
        else:
            self.model_label.config(text="No directory selected", fg="gray")

    def run_extraction(self):
        if not self.pdf_files or not self.persona_file or not self.model_dir:
            messagebox.showerror("Missing Input", "Please select PDF files, persona.json, and a local SBERT model directory.")
            return
        self.status_label.config(text="Running...", fg="orange")
        self.result_text.delete(1.0, tk.END)
        threading.Thread(target=self._run_extraction_thread, daemon=True).start()

    def _run_extraction_thread(self):
        try:
            import_path = os.path.join(os.path.dirname(__file__), '../outline_extractor/output')
            # Try to load the model from the specified directory
            if not os.path.exists(os.path.join(self.model_dir, "config.json")):
                self.status_label.config(text="Model not found!", fg="red")
                messagebox.showerror("Model Error", "No SBERT model found in the selected directory. Please download and place a model there.")
                return
            self.model = SentenceTransformer(self.model_dir)
            with open(self.persona_file, "r") as f:
                persona_data = json.load(f)
            persona = persona_data["persona"]
            job = persona_data["job_to_be_done"]
            combined_query = f"{persona}. Task: {job}"
            all_sections = []
            doc_headings = {}
            for pdf in self.pdf_files:
                doc_sections = extract_headings_and_text(pdf, os.path.basename(pdf))
                all_sections.extend(doc_sections)
                # Try to load outline_extractor headings
                outline_path = os.path.join(import_path, os.path.basename(pdf).replace('.pdf', '.json'))
                if os.path.exists(outline_path):
                    with open(outline_path, 'r') as f:
                        outline_data = json.load(f)
                    doc_headings[os.path.basename(pdf)] = outline_data.get('outline', [])
                else:
                    doc_headings[os.path.basename(pdf)] = []
            if not all_sections:
                self.status_label.config(text="No sections found", fg="red")
                self.result_text.insert(tk.END, "No sections extracted from the PDFs.")
                return
            ranked = rank_sections_by_similarity(all_sections, combined_query)
            output = {
                "metadata": {
                    "documents": [os.path.basename(f) for f in self.pdf_files],
                    "persona": persona,
                    "job_to_be_done": job
                },
                "sections": [],
                "subsection_analysis": [],
                "headings": doc_headings
            }
            for i, item in enumerate(ranked[:10]):
                output["sections"].append({
                    "document": item["document"],
                    "page": item["page"],
                    "section_title": item["title"],
                    "importance_rank": i+1
                })
                output["subsection_analysis"].append({
                    "document": item["document"],
                    "page": item["page"],
                    "refined_text": item["text"],
                    "importance_rank": i+1
                })
            self.result = output
            self.result_text.insert(tk.END, json.dumps(output, indent=2))
            self.status_label.config(text="Done", fg="green")
        except Exception as e:
            self.status_label.config(text="Error", fg="red")
            self.result_text.insert(tk.END, f"Error: {e}")

    def save_results(self):
        if not self.result:
            messagebox.showerror("No Results", "No results to save.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file:
            with open(file, "w") as f:
                json.dump(self.result, f, indent=2)
            messagebox.showinfo("Saved", f"Results saved to {file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonaInsightGUI(root)
    root.mainloop() 