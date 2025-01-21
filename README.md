# VCF-Clinical-Assessment-Analyzer


Bu program, Clinical Insight panel sonuçlarından export edilen VCF dosyalarını analiz ederek seçilen klinik değerlendirme (CLI_ASSESSMENT) tiplerine göre varyantları filtreleyip Excel formatında raporlar.

## Özellikler

- Çoklu VCF dosyası seçimi ve analizi
- Otomatik CLI_ASSESSMENT tiplerinin tespiti ve listelenmesi
- Kullanıcı dostu grafiksel arayüz
- Çoklu CLI_ASSESSMENT tipi seçimi imkanı
- Excel formatında rapor çıktısı
- Her varyant için allel frekansı (AF) ve okuma derinliği (DP) bilgisi

## Gereksinimler

```python
pandas
tkinter
```

## Kurulum

```bash
pip install pandas
```

Not: tkinter genellikle Python'un standart kurulumu ile birlikte gelir.

## Kullanım

1. Programı çalıştırın:
```bash
python vcf_analyzer.py
```

2. Ana arayüzde "VCF Dosyalarını Seç" butonuna tıklayın
3. Analiz etmek istediğiniz VCF dosyalarını seçin
4. Listelenen CLI_ASSESSMENT tiplerinden analiz etmek istediklerinizi seçin
   - Çoklu seçim için Ctrl tuşunu kullanabilirsiniz
5. "Analiz Et" butonuna tıklayın
6. Sonuç Excel dosyasını kaydetmek için konum ve isim belirleyin

## VCF Dosyası Hazırlama

VCF dosyalarını Clinical Insight panel hasta dosyasından şu şekilde export edebilirsiniz:
1. Clinical Insight panelinde hasta dosyasına gidin
2. Export seçeneğine tıklayın
3. File type olarak "VCF" seçin
4. "Export a VCF file with standard annotations" seçeneğini işaretleyin
5. Export işlemini başlatın

## Çıktı Format

Excel dosyasında şu kolonlar bulunur:
- Gene: Gen sembolü
- Mutation: HGVS formatında mutasyon
- [Sample_ID]: Her örnek için AF% (DP) formatında değerler

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Bir Pull Request oluşturun
