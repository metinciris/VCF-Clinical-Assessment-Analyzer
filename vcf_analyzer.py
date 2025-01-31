import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import pandas as pd
import re
from openpyxl import load_workbook

class VCFAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VCF Analiz Programı")
        self.root.geometry("700x600")
        
        self.vcf_files = []
        self.analysis_labels = {"CLI_ASSESSMENT", "ING_CLASSIFICATION"}  # Varsayılan etiketler
        
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dosya seçim butonu
        self.select_button = ttk.Button(self.main_frame, text="VCF Dosyalarını Seç", command=self.select_files)
        self.select_button.pack(pady=10)
        
        # Seçili dosya sayısını gösteren label
        self.files_label = ttk.Label(self.main_frame, text="Seçili dosya sayısı: 0")
        self.files_label.pack(pady=5)
        
        # Dinamik Etiketler Listesi
        self.label_frame = ttk.LabelFrame(self.main_frame, text="Analiz Edilecek Etiketler", padding="5")
        self.label_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.label_listbox = tk.Listbox(self.label_frame, selectmode=tk.MULTIPLE)
        self.label_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Etiket ekleme ve kaldırma butonları
        self.add_label_button = ttk.Button(self.main_frame, text="Yeni Etiket Ekle", command=self.add_label)
        self.add_label_button.pack(pady=5)
        self.remove_label_button = ttk.Button(self.main_frame, text="Seçili Etiketi Kaldır", command=self.remove_label)
        self.remove_label_button.pack(pady=5)
        
        # Analiz Butonu
        self.analyze_button = ttk.Button(self.main_frame, text="Analiz Et", command=self.analyze_files)
        self.analyze_button.pack(pady=15)

        self.update_label_list()
        self.root.mainloop()
    
    def select_files(self):
        self.vcf_files = filedialog.askopenfilenames(
            title="VCF dosyalarını seçin",
            filetypes=(("VCF files", "*.vcf"), ("All files", "*.*"))
        )
        self.files_label.config(text=f"Seçili dosya sayısı: {len(self.vcf_files)}")
    
    def update_label_list(self):
        """GUI'deki etiket listesini günceller."""
        self.label_listbox.delete(0, tk.END)
        for label in sorted(self.analysis_labels):
            self.label_listbox.insert(tk.END, label)
    
    def add_label(self):
        """Kullanıcının yeni bir etiket eklemesini sağlar."""
        new_label = simpledialog.askstring("Yeni Etiket", "Yeni etiket adını girin:")
        if new_label and new_label.strip():
            self.analysis_labels.add(new_label.strip())
            self.update_label_list()
    
    def remove_label(self):
        """Seçili etiketi kaldırır."""
        selected_indices = self.label_listbox.curselection()
        for i in selected_indices[::-1]:  # Baştan silersek index kayar
            label = self.label_listbox.get(i)
            self.analysis_labels.discard(label)
        self.update_label_list()

    def analyze_files(self):
        selected_labels = [self.label_listbox.get(i) for i in self.label_listbox.curselection()]
        
        # Eğer hiç etiket seçilmemişse tüm verileri al
        if not selected_labels:
            selected_labels = list(self.analysis_labels)

        results = []

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

                # Seçili etiketlerden herhangi biri varsa işle
                matched_labels = {label: info.get(label, "N/A") for label in selected_labels}
                etiket_sinifi = ", ".join(f"{k}: {v}" for k, v in matched_labels.items() if v != "N/A")

                gene = info.get("GENE_SYMBOL", "N/A")
                mutation = info.get("HGVS_TRANSCRIPT", "N/A")
                
                # Format alanından AF ve DP değerlerini al
                format_fields = fields[8].split(":")
                sample_fields = fields[9].split(":")
                format_dict = dict(zip(format_fields, sample_fields))
                
                af = float(format_dict.get("ING_AF", 0))
                dp = int(format_dict.get("DP", 0))
                value = f"{af:.1f}% ({dp})"
                
                results.append({
                    "Gene": gene,
                    "Mutation": mutation,
                    "Etiket Sınıfı": etiket_sinifi,  # Yeni sütun
                    lab_id: value
                })
        
        df = pd.DataFrame(results)
        
        # Excel sütun genişliklerini ayarla
        if not df.empty:
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
