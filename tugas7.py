import math
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


DATABASE_PATH = Path(__file__).with_name("prediksi_diabetes.db")


def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pasien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pasien TEXT NOT NULL,
                usia INTEGER NOT NULL,
                gula_darah REAL NOT NULL,
                bmi REAL NOT NULL,
                riwayat_ortu TEXT NOT NULL,
                hasil_prediksi TEXT NOT NULL
            )
            """
        )


def predict_risk(glucose, bmi, age, parental_history):
    """Return a simple educational risk estimate, not a medical diagnosis."""
    if glucose >= 200 or (
        glucose >= 126 and (bmi >= 30 or parental_history == "Ya")
    ):
        return "Risiko Tinggi"

    if (
        glucose >= 100
        or bmi >= 25
        or age >= 45
        or parental_history == "Ya"
    ):
        return "Risiko Sedang"

    return "Risiko Rendah"


class DiabetesPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Prediksi Risiko Diabetes")
        self.root.geometry("760x590")
        self.root.minsize(680, 540)
        self.root.configure(bg="#f3f6fa")

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.glucose_var = tk.StringVar()
        self.bmi_var = tk.StringVar()
        self.history_var = tk.StringVar()

        self._build_interface()

    def _build_interface(self):
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Prediksi Risiko Diabetes",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            container,
            text=(
                "Masukkan data pasien untuk mendapatkan estimasi risiko "
                "berdasarkan aturan sederhana."
            ),
            wraplength=680,
        ).pack(anchor="w", pady=(4, 18))

        form = ttk.LabelFrame(container, text="Data Pasien", padding=16)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        fields = (
            ("Nama pasien", self.name_var),
            ("Usia (tahun)", self.age_var),
            ("Gula darah (mg/dL)", self.glucose_var),
            ("BMI", self.bmi_var),
        )
        for row, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=row, column=0, sticky="w", padx=(0, 14), pady=6
            )
            ttk.Entry(form, textvariable=variable).grid(
                row=row, column=1, sticky="ew", pady=6
            )

        ttk.Label(form, text="Riwayat diabetes orang tua").grid(
            row=4, column=0, sticky="w", padx=(0, 14), pady=6
        )
        history_combo = ttk.Combobox(
            form,
            textvariable=self.history_var,
            values=("Ya", "Tidak"),
            state="readonly",
        )
        history_combo.grid(row=4, column=1, sticky="ew", pady=6)
        history_combo.set("Tidak")

        buttons = ttk.Frame(container)
        buttons.pack(fill="x", pady=14)
        ttk.Button(
            buttons, text="Prediksi dan Simpan", command=self.predict_and_save
        ).pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(
            side="left", padx=(10, 0)
        )
        ttk.Button(buttons, text="Lihat Data", command=self.show_records).pack(
            side="left", padx=(10, 0)
        )

        self.result_label = tk.Label(
            container,
            text="Hasil prediksi akan tampil di sini.",
            font=("Segoe UI", 12, "bold"),
            bg="#e8edf3",
            fg="#263238",
            padx=12,
            pady=12,
        )
        self.result_label.pack(fill="x")
        ttk.Label(
            container,
            text=(
                "Catatan: hasil ini hanya estimasi edukatif, bukan diagnosis "
                "atau pengganti pemeriksaan tenaga kesehatan. Gula darah "
                "diasumsikan dalam mg/dL; kondisi pengukuran dapat memengaruhi "
                "interpretasi."
            ),
            wraplength=680,
            justify="left",
        ).pack(anchor="w", pady=(12, 0))

    def clear_form(self):
        self.name_var.set("")
        self.age_var.set("")
        self.glucose_var.set("")
        self.bmi_var.set("")
        self.history_var.set("Tidak")
        self.result_label.configure(
            text="Hasil prediksi akan tampil di sini.",
            bg="#e8edf3",
            fg="#263238",
        )

    def _validated_input(self):
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("Nama pasien wajib diisi.")

        try:
            age = int(self.age_var.get().strip())
            glucose = float(self.glucose_var.get().strip().replace(",", "."))
            bmi = float(self.bmi_var.get().strip().replace(",", "."))
        except ValueError as error:
            raise ValueError(
                "Usia harus berupa bilangan bulat, sedangkan gula darah dan "
                "BMI harus berupa angka."
            ) from error

        if not 1 <= age <= 120:
            raise ValueError("Usia harus berada di antara 1 dan 120 tahun.")
        if not math.isfinite(glucose) or not 20 <= glucose <= 600:
            raise ValueError("Gula darah harus berada di antara 20 dan 600 mg/dL.")
        if not math.isfinite(bmi) or not 10 <= bmi <= 80:
            raise ValueError("BMI harus berada di antara 10 dan 80.")

        parental_history = self.history_var.get()
        if parental_history not in ("Ya", "Tidak"):
            raise ValueError("Pilih riwayat diabetes orang tua: Ya atau Tidak.")

        return name, age, glucose, bmi, parental_history

    def predict_and_save(self):
        try:
            name, age, glucose, bmi, parental_history = self._validated_input()
        except ValueError as error:
            messagebox.showerror("Input tidak valid", str(error), parent=self.root)
            return

        result = predict_risk(glucose, bmi, age, parental_history)
        colors = {
            "Risiko Rendah": ("#e8f5e9", "#1b5e20"),
            "Risiko Sedang": ("#fff8e1", "#8d5b00"),
            "Risiko Tinggi": ("#ffebee", "#b71c1c"),
        }

        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                connection.execute(
                    """
                    INSERT INTO pasien
                        (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (name, age, glucose, bmi, parental_history, result),
                )
        except sqlite3.Error as error:
            messagebox.showerror(
                "Kesalahan database",
                f"Data tidak dapat disimpan: {error}",
                parent=self.root,
            )
            return

        background, foreground = colors[result]
        self.result_label.configure(
            text=f"Hasil prediksi untuk {name}: {result}",
            bg=background,
            fg=foreground,
        )
        messagebox.showinfo(
            "Prediksi berhasil",
            f"{result} berhasil disimpan ke database.",
            parent=self.root,
        )

    def show_records(self):
        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                records = connection.execute(
                    """
                    SELECT id, nama_pasien, usia, gula_darah, bmi,
                           riwayat_ortu, hasil_prediksi
                    FROM pasien
                    ORDER BY id DESC
                    """
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror(
                "Kesalahan database",
                f"Riwayat pasien tidak dapat dibaca: {error}",
                parent=self.root,
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Riwayat Pasien")
        window.geometry("900x360")
        window.minsize(700, 260)

        columns = (
            "id",
            "nama_pasien",
            "usia",
            "gula_darah",
            "bmi",
            "riwayat_ortu",
            "hasil_prediksi",
        )
        headings = (
            "ID",
            "Nama pasien",
            "Usia",
            "Gula darah",
            "BMI",
            "Riwayat orang tua",
            "Hasil prediksi",
        )
        table_frame = ttk.Frame(window, padding=12)
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        table = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=12
        )
        for column, heading in zip(columns, headings):
            table.heading(column, text=heading)
            table.column(column, width=110, anchor="center")
        table.column("nama_pasien", width=160, anchor="w")
        table.column("hasil_prediksi", width=130)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=table.yview
        )
        table.configure(yscrollcommand=scrollbar.set)
        table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for record in records:
            table.insert("", "end", values=record)

        if not records:
            ttk.Label(table_frame, text="Belum ada data pasien tersimpan.").grid(
                row=1, column=0, sticky="w", pady=(10, 0)
            )


if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = DiabetesPredictionApp(root)
    root.mainloop()