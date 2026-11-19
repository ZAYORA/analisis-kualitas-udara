# Proyek Analisis Data: Air Quality Dataset (PRSA Beijing)

Analisis kualitas udara (PM2.5) dari 12 stasiun pemantau di Beijing periode Maret 2013 - Februari 2017, beserta dashboard interaktif menggunakan Streamlit.

## Struktur Direktori

```
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   └───PRSA_Data_*.csv (12 stasiun)
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment

Pastikan Python 3.11 atau lebih baru sudah terpasang (versi pada `requirements.txt` diuji dengan Python 3.12). Disarankan memakai virtual environment.

```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Menjalankan Dashboard

Jalankan perintah berikut dari folder utama proyek:

```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka otomatis di browser (biasanya http://localhost:8501).

## Menjalankan Notebook

Buka `notebook.ipynb` di Jupyter atau Google Colab, pastikan folder `data/` berisi 12 berkas CSV stasiun, lalu jalankan semua sel dari atas. Sel terakhir menghasilkan `dashboard/main_data.csv`.

## Sumber Data dan Koordinat

- Data kualitas udara: [Air Quality Dataset](https://github.com/marceloreis/HTI/tree/master) (PRSA Beijing Multi-Site Air Quality Data).
- Koordinat stasiun: Tabel S1 pada *Supplement* Foreback dkk. (2022), *Atmospheric Chemistry and Physics*, 22, 11089-11104, https://doi.org/10.5194/acp-22-11089-2022-supplement.

## Tautan Dashboard

Lihat `url.txt`.
