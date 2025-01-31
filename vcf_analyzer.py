import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import re
from openpyxl import load_workbook

class VCFAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VCF Analiz Programı")
        self.root.geometry("700x550")
        
        self.vcf_files = []
        self.assessment_types = set()
        self.classification_types = set()
        
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dosya seçim butonu
        self.select_button = ttk.Button(self.main_frame, text="VCF Dosyalarını Seç", command=self.select_files)
        self.select_button.pack(pady=10)
        
        # Seçili dosya sayısını gösteren label
        self.files_label = ttk.Label(self.main_frame, text="Seçili dosya sayısı: 0")
        self.files_label.pack(pady=5)
        
        # CLI_ASSESSMENT Tipleri
        self.assessment_frame = ttk.LabelFrame(self.main_frame, text="CLI_ASSESSMENT Tipleri", padding="5")
        self.assessment_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.assessment_listbox = tk.Listbox(self.assessment_frame, selectmode=tk.MULTIPLE)
        self.assessment_listbox.pack(fill=tk.BOTH, expand=True)
        
        # ING_CLASSIFICATION Tipleri
        self.classification_frame = ttk.LabelFrame(self.main_frame, text="ING_CLASSIFICATION Tipleri", padding="5")
        self.classification_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.classification_listbox = tk.Listbox(self.classification_frame, selectmode=tk.MULTIPLE)
        self.classification_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Analiz Butonu
        self.analyze_button = ttk.Button(self.main_frame, text="Analiz Et", command=self.analyze_files)
        self.analyze_button.pack(pady=15)

        self.root.mainloop()
    
    def select_files(self):
        self.vcf_files = filedialog.askopenfilenames(
            title="VCF dosyalarını seçin",
            filetypes=(("VCF files", "*.vcf"), ("All files", "*.*"))
        )
        self.files_label.config(text=f"Seçili dosya sayısı: {len(self.vcf_files)}")
        
        # Assessment ve Classification tiplerini bul
        self.assessment_types.clear()
        self.classification_types.clear()
        
        for vcf_file in self.vcf_files:
            with open(vcf_file) as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    if "CLI_ASSESSMENT=" in line:
                        assessment = re.search(r'CLI_ASSESSMENT=([^;]+)', line)
                        if assessment:
                            self.assessment_types.add(assessment.group(1))
                    if "ING_CLASSIFICATION=" in line:
                        classification = re.search(r'ING_CLASSIFICATION=([^;]+)', line)
                        if classification:
                            self.classification_types.add(classification.group(1))
        
        # Listbox'ları güncelle
        self.assessment_listbox.delete(0, tk.END)
        for assessment in sorted(self.assessment_types):
            self.assessment_listbox.insert(tk.END, assessment)

        self.classification_listbox.delete(0, tk.END)
        for classification in sorted(self.classification_types):
            self.classification_listbox.insert(tk.END, classification)
    
    def analyze_files(self):
        selected_assessments = [self.assessment_listbox.get(i) for i in self.assessment_listbox.curselection()]
        selected_classifications = [self.classification_listbox.get(i) for i in self.classification_listbox.curselection()]
        
        # **Yeni kural: Hiç seçim yapılmasa da tüm varyantları değerlendirebiliriz**
        results = {}

        for vcf_file in self.vcf_files:
            with open(vcf_file) as f:
                lines = f.readlines()
            
            # Lab Test ID'yi bul
            lab_id = ""
            for line in lines:
                if "##LabTestID=" in line:
                    lab_id = line.split("=")[1].strip()
                    break
            
            # Varyantları işle
            for line in lines:
                if line.startswith("#"):
                    continue
                
                fields = line.split("\t")
                info = dict(item.split("=") for item in fields[7].split(";") if "=" in item)
                
                assessment = info.get("CLI_ASSESSMENT", "N/A")
                classification = info.get("ING_CLASSIFICATION", "N/A")
                
                # **Seçim yapılmışsa filtre uygula, yoksa tüm varyantları al**
                if selected_assessments and assessment not in selected_assessments:
                    continue
                if selected_classifications and classification not in selected_classifications:
                    continue
                
                gene = info.get("GENE_SYMBOL", "N/A")
                mutation = info.get("HGVS_TRANSCRIPT", "N/A")
                
                # Format alanından AF ve DP değerlerini al
                format_fields = fields[8].split(":")
                sample_fields = fields[9].split(":")
                format_dict = dict(zip(format_fields, sample_fields))
                
                af = float(format_dict.get("ING_AF", 0))
                dp = int(format_dict.get("DP", 0))
                value = f"{af:.1f}% ({dp})"
                
                key = (gene, mutation, assessment, classification)
                if key not in results:
                    results[key] = {}
                results[key][lab_id] = value
        
        # DataFrame oluştur
        df_data = []
        for (gene, mutation, assessment, classification), values in results.items():
            row = {
                "Gene": gene, 
                "Mutation": mutation,
                "CLI_ASSESSMENT": assessment,
                "ING_CLASSIFICATION": classification
            }
            row.update(values)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Excel sütun genişliklerini ayarla
        if df_data:
            output_file = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if output_file:
                df.to_excel(output_file, index=False)
                
                wb = load_workbook(output_file)
                ws = wb.active
                for col in ws.columns:
                    max_length = 0
                    col_letter = col[0].column_letter
                    for cell in col:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    ws.column_dimensions[col_letter].width = max_length + 2  

                wb.save(output_file)

                tk.messagebox.showinfo("Başarılı", "Veriler Excel dosyasına kaydedildi!")
        else:
            tk.messagebox.showwarning("Uyarı", "Seçili kriterlere uygun varyant bulunamadı!")

if __name__ == "__main__":
    app = VCFAnalyzer()
