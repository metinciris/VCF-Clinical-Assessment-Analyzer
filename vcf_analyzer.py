import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import re

class VCFAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VCF Analiz Programı")
        self.root.geometry("600x400")
        
        self.vcf_files = []
        self.assessment_types = set()
        self.selected_assessments = []
        
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dosya seçim butonu
        self.select_button = ttk.Button(self.main_frame, text="VCF Dosyalarını Seç", command=self.select_files)
        self.select_button.pack(pady=10)
        
        # Seçili dosyaları göster
        self.files_label = ttk.Label(self.main_frame, text="Seçili dosya sayısı: 0")
        self.files_label.pack(pady=5)
        
        # Assessment tipleri için liste kutusu
        self.listbox_frame = ttk.LabelFrame(self.main_frame, text="CLI_ASSESSMENT Tipleri", padding="5")
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.assessment_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.MULTIPLE)
        self.assessment_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Analiz butonu
        self.analyze_button = ttk.Button(self.main_frame, text="Analiz Et", command=self.analyze_files)
        self.analyze_button.pack(pady=10)
        
        self.root.mainloop()
    
    def select_files(self):
        self.vcf_files = filedialog.askopenfilenames(
            title="VCF dosyalarını seçin",
            filetypes=(("VCF files", "*.vcf"), ("All files", "*.*"))
        )
        self.files_label.config(text=f"Seçili dosya sayısı: {len(self.vcf_files)}")
        
        # Assessment tiplerini bul
        self.assessment_types = set()
        for vcf_file in self.vcf_files:
            with open(vcf_file) as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    if "CLI_ASSESSMENT=" in line:
                        assessment = re.search(r'CLI_ASSESSMENT=([^;]+)', line)
                        if assessment:
                            self.assessment_types.add(assessment.group(1))
        
        # Listbox'ı güncelle
        self.assessment_listbox.delete(0, tk.END)
        for assessment in sorted(self.assessment_types):
            self.assessment_listbox.insert(tk.END, assessment)
    
    def analyze_files(self):
        # Seçili assessment tiplerini al
        selected_indices = self.assessment_listbox.curselection()
        selected_assessments = [self.assessment_listbox.get(i) for i in selected_indices]
        
        if not selected_assessments:
            tk.messagebox.showwarning("Uyarı", "Lütfen en az bir CLI_ASSESSMENT tipi seçin!")
            return
        
        # Sonuçları tutacak dictionary
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
                
                if "CLI_ASSESSMENT" not in info:
                    continue
                
                assessment = info["CLI_ASSESSMENT"]
                if assessment not in selected_assessments:
                    continue
                
                if "GENE_SYMBOL" not in info or "HGVS_TRANSCRIPT" not in info:
                    continue
                
                gene = info["GENE_SYMBOL"]
                mutation = info["HGVS_TRANSCRIPT"]
                
                # Format alanından AF ve DP değerlerini al
                format_fields = fields[8].split(":")
                sample_fields = fields[9].split(":")
                format_dict = dict(zip(format_fields, sample_fields))
                
                if "ING_AF" in format_dict and "DP" in format_dict:
                    af = float(format_dict["ING_AF"])
                    dp = int(format_dict["DP"])
                    value = f"{af:.1f}% ({dp})"
                    key = (gene, mutation)
                    if key not in results:
                        results[key] = {}
                    results[key][lab_id] = value
        
        # DataFrame oluştur
        df_data = []
        for (gene, mutation), values in results.items():
            row = {"Gene": gene, "Mutation": mutation}
            row.update(values)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Excel'e kaydet
        if df_data:
            output_file = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if output_file:
                df.to_excel(output_file, index=False)
                tk.messagebox.showinfo("Başarılı", "Veriler Excel dosyasına kaydedildi!")
        else:
            tk.messagebox.showwarning("Uyarı", "Seçili kriterlere uygun varyant bulunamadı!")

if __name__ == "__main__":
    app = VCFAnalyzer()
