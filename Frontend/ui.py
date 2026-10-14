import csv
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")

sys.path.insert(0, ROOT)
sys.path.insert(0, BACKEND)

# Import backend disesuaikan dengan m1, m2, dan m3 milikmu
from m1_pesanan import ArrayPesanan, LinkedListPesanan
from m2_antrean import (
    AntreanMelingkar, AntreanNaif, ManajerUndoRedo, Stack,
    format_rupiah, proses_kasir
)
from m3_laporan import LaporanPesanan

NAVY = "#30415F"
DARK = "#24334B"
BG = "#EEF1F4"
WHITE = "#FFFFFF"
MUTED = "#5C6675"
SELECTED = "#DCE6F2"

COLUMNS = (
    "#", "oid", "harga", "selesai",
    "resto", "menu", "pelanggan", "status"
)

MENU = [
    ("DATA", [
        ("Load", "load")
    ]),
    ("M1 - DATA PESANAN", [
        ("ARRAY - LIHAT PESANAN", "array_lihat"),
        ("ARRAY - TAMBAH PESANAN REGULER", "array_reguler"),
        ("ARRAY - TAMBAH PESANAN PRIORITAS", "array_prioritas"),
        ("ARRAY - TAMBAH PESANAN VIP", "array_vip"),
        ("ARRAY - HAPUS PESANAN", "array_hapus"),
        ("LINKEDLIST - LIHAT PESANAN", "linked_lihat"),
        ("LINKEDLIST - TAMBAH PESANAN REGULER", "linked_reguler"),
        ("LINKEDLIST - TAMBAH PESANAN PRIORITAS", "linked_prioritas"),
        ("LINKEDLIST - TAMBAH PESANAN VIP", "linked_vip"),
        ("LINKEDLIST - HAPUS PESANAN", "linked_hapus"),
    ]),
    ("M2 - STACK DAN QUEUE", [
        ("STACK - POSTFIX (MESIN KASIR)", "postfix"),
        ("STACK - UNDO", "undo"),
        ("STACK - REDO", "redo"),
        ("QUEUE - ENQUEUE", "enqueue"),
        ("QUEUE - DEQUEUE NAIF", "dequeue_naif"),
        ("QUEUE - DEQUEUE CIRCULAR", "dequeue_circular"),
    ]),
    ("M3 - SORT DAN SEARCH", [
        ("SORT - INSERTION SORT", "insertion"),
        ("SORT - MERGE SORT", "merge"),
        ("SEARCH - LINEAR SEARCH", "linear"),
        ("SEARCH - BINARY SEARCH", "binary"),
    ]),
]

DESKRIPSI = {
    "load": ("Data: Load", "Muat data pesanan dari file CSV."),
    "array_lihat": ("Array: Lihat pesanan", "Ambil pesanan berdasarkan indeks."),
    "array_reguler": ("Array: Tambah reguler", "Tambah pesanan ke bagian belakang array."),
    "array_prioritas": ("Array: Tambah prioritas", "Sisipkan pesanan di bagian tengah array."),
    "array_vip": ("Array: Tambah VIP", "Sisipkan pesanan di bagian depan array."),
    "array_hapus": ("Array: Hapus pesanan", "Hapus pesanan berdasarkan indeks."),
    "linked_lihat": ("Linked List: Lihat pesanan", "Ambil pesanan berdasarkan indeks."),
    "linked_reguler": ("Linked List: Tambah reguler", "Tambah pesanan di bagian belakang linked list."),
    "linked_prioritas": ("Linked List: Tambah prioritas", "Sisipkan pesanan di bagian tengah linked list."),
    "linked_vip": ("Linked List: Tambah VIP", "Tambah pesanan di bagian depan linked list."),
    "linked_hapus": ("Linked List: Hapus pesanan", "Hapus pesanan berdasarkan indeks."),
    "postfix": ("Stack: Postfix (mesin kasir)", "Masukkan ekspresi untuk diproses oleh M2."),
    "undo": ("Stack: Undo", "Batalkan aksi terakhir pada antrean M2."),
    "redo": ("Stack: Redo", "Ulangi aksi antrean M2 yang dibatalkan."),
    "enqueue": ("Queue: Enqueue", "Tambahkan pesanan baru ke antrean M2."),
    "dequeue_naif": ("Queue: Dequeue naif", "Keluarkan pesanan dari depan antrean naif."),
    "dequeue_circular": ("Queue: Dequeue circular", "Keluarkan pesanan dari depan antrean melingkar."),
    "insertion": ("Sort: insertion sort, O(n²)", "Mengurutkan data dengan insertion sort."),
    "merge": ("Sort: merge sort, O(n log n)", "Membelah data lalu menggabungkan bagian yang terurut."),
    "linear": ("Search: linear search, O(n)", "Memeriksa data satu per satu."),
    "binary": ("Search: binary search, O(log n)", "Mencari data menggunakan binary search."),
}


def cari_csv():
    return os.path.join(ROOT, "data", "pesanan.csv")


def harga_tampil(value):
    try:
        return f"{int(float(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value or "—")


class Aplikasi:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1480x920")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG)

        self.array = ArrayPesanan()
        self.linked = LinkedListPesanan()
        self.manajer_m2 = ManajerUndoRedo()  # Inisialisasi Manajer M2
        self.data = []
        self.laporan = None
        self.aktif = "merge"
        self.input = {}

        self.buat_tampilan()
        self.pilih_menu("merge")

    def buat_tampilan(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=27,
            font=("Consolas", 10),
            background="white",
            fieldbackground="white"
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#E9EDF1"
        )

        header = tk.Frame(self.root, bg=NAVY, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="2EZ4U Food Delivery",
            bg=NAVY,
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=18)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=8, pady=5)

        # MENU KIRI
        kiri = tk.Frame(body, bg="#E9EDF1", width=430)
        kiri.pack(side="left", fill="y", padx=(0, 8))
        kiri.pack_propagate(False)

        canvas = tk.Canvas(kiri, bg="#E9EDF1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            kiri, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        menu_frame = tk.Frame(canvas, bg="#E9EDF1")
        window = canvas.create_window(
            (0, 0), window=menu_frame, anchor="nw"
        )

        menu_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                window, width=event.width
            )
        )

        self.tombol_menu = {}

        for judul, items in MENU:
            tk.Label(
                menu_frame,
                text=judul,
                bg="#E9EDF1",
                fg=MUTED,
                anchor="w",
                font=("Segoe UI", 10, "bold")
            ).pack(fill="x", padx=10, pady=(10, 3))

            for label, key in items:
                button = tk.Button(
                    menu_frame,
                    text=label,
                    anchor="w",
                    font=("Segoe UI", 10),
                    bg="#FAFAFA",
                    relief="groove",
                    bd=1,
                    padx=10,
                    pady=4,
                    command=lambda k=key: self.pilih_menu(k)
                )
                button.pack(fill="x", padx=8, pady=1)
                self.tombol_menu[key] = button

        # PANEL KANAN
        kanan = tk.Frame(body, bg=WHITE)
        kanan.pack(side="left", fill="both", expand=True)

        self.judul = tk.Label(
            kanan, text="", bg=WHITE, fg="#20252D",
            anchor="w", font=("Segoe UI", 16, "bold")
        )
        self.judul.pack(fill="x", padx=18, pady=(15, 3))

        self.deskripsi = tk.Label(
            kanan, text="", bg=WHITE, fg=MUTED,
            anchor="w", justify="left",
            font=("Segoe UI", 10)
        )
        self.deskripsi.pack(fill="x", padx=18, pady=(0, 12))

        self.form = tk.Frame(kanan, bg=WHITE)
        self.form.pack(fill="x", padx=15, pady=5)

        ttk.Separator(kanan).pack(fill="x", pady=8)

        self.ringkasan = tk.Label(
            kanan,
            text="Tekan Load untuk membaca data CSV.",
            bg=WHITE,
            fg="#20252D",
            anchor="w",
            justify="left",
            font=("Segoe UI", 11)
        )
        self.ringkasan.pack(fill="x", padx=17, pady=8)

        table_frame = tk.Frame(kanan, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=14, pady=8)

        self.tabel = ttk.Treeview(
            table_frame, columns=COLUMNS, show="headings"
        )

        scroll_y = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tabel.yview
        )
        scroll_x = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.tabel.xview
        )

        self.tabel.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        for col in COLUMNS:
            self.tabel.heading(col, text=col)
            self.tabel.column(col, width=130, minwidth=75, anchor="w")

        self.tabel.column("#", width=45, anchor="center")
        self.tabel.column("oid", width=150)
        self.tabel.column("harga", width=100, anchor="e")

        self.tabel.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # COMMAND LOG
        tk.Label(
            self.root, text="COMMAND", bg=BG,
            fg=MUTED, anchor="w",
            font=("Segoe UI", 10, "bold")
        ).pack(fill="x", padx=14)

        self.command = tk.Text(
            self.root, height=4, font=("Consolas", 10),
            wrap="none", bg="white", fg="#303744"
        )
        self.command.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(
            self.root,
            text="Pilih menu di sebelah kiri untuk menjalankan operasi.",
            bg="#F8F5E7", fg="#4C4634",
            anchor="w", padx=12, pady=7
        ).pack(fill="x", padx=14, pady=(0, 6))

        self.status = tk.Label(
            self.root, text="[Siap] 2EZ4U Food Delivery",
            bg=DARK, fg="white", anchor="w",
            font=("Consolas", 10, "bold"), padx=14, pady=7
        )
        self.status.pack(fill="x", side="bottom", padx=8, pady=(0, 8))

    def pilih_menu(self, key):
        self.aktif = key

        for nama, button in self.tombol_menu.items():
            button.configure(
                bg=SELECTED if nama == key else "#FAFAFA",
                font=("Segoe UI", 10, "bold" if nama == key else "normal")
            )

        judul, deskripsi = DESKRIPSI[key]
        self.judul.configure(text=judul)
        self.deskripsi.configure(text=deskripsi)

        for widget in self.form.winfo_children():
            widget.destroy()

        self.input = {}

        def buat_entry(label, nama, nilai="", width=16):
            frame = tk.Frame(self.form, bg=WHITE)
            frame.pack(side="left", anchor="nw", padx=(0, 15))

            tk.Label(
                frame, text=label, bg=WHITE,
                fg="#374151", font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            ent = tk.Entry(frame, width=width, font=("Consolas", 11))
            ent.insert(0, nilai)
            ent.pack(anchor="w", pady=4)
            self.input[nama] = ent

        def buat_combo(label, nama, pilihan, awal):
            frame = tk.Frame(self.form, bg=WHITE)
            frame.pack(side="left", anchor="nw", padx=(0, 15))

            tk.Label(
                frame, text=label, bg=WHITE,
                fg="#374151", font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            combo = ttk.Combobox(
                frame, values=pilihan,
                state="readonly", width=15
            )
            combo.set(awal)
            combo.pack(anchor="w", pady=4)
            self.input[nama] = combo

        if key in ("array_lihat", "array_hapus",
                   "linked_lihat", "linked_hapus"):
            buat_entry("Indeks pesanan", "index", "0")

        elif key in ("array_reguler", "array_prioritas", "array_vip",
                     "linked_reguler", "linked_prioritas", "linked_vip",
                     "enqueue"):
            buat_entry("OID", "oid", "O-200001", 13)
            buat_entry("Pelanggan", "pelanggan", "Pelanggan Baru", 16)
            buat_entry("Restoran", "resto", "kafe-teknik", 15)
            buat_entry("Menu", "menu", "nasi-goreng", 15)
            buat_entry("Harga", "harga", "15000", 9)
            buat_entry("Prioritas", "prioritas", "0", 8)

        elif key == "postfix":
            buat_entry(
                "Ekspresi infix", "expression",
                "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", 38
            )

        elif key in ("insertion", "merge"):
            buat_entry("Jumlah baris", "jumlah",
                       "10" if key == "insertion" else "4000")
            buat_combo("Urutkan menurut", "kunci",
                       ["oid", "harga", "selesai"], "harga" if key == "insertion" else "oid")

        elif key in ("linear", "binary"):
            buat_entry("Target", "target", "O-000001", 18)
            buat_combo("Cari menurut", "kunci",
                       ["oid", "harga", "selesai"], "oid")

        elif key in ("dequeue_naif", "dequeue_circular"):
            buat_entry("Jumlah dequeue", "jumlah", "1")

        button_text = (
            "URUTKAN" if key in ("insertion", "merge")
            else "CARI" if key in ("linear", "binary")
            else "JALANKAN"
        )

        tk.Button(
            self.form, text=button_text,
            bg=NAVY, fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=22, pady=6,
            command=self.jalankan
        ).pack(side="right", padx=8, pady=(15, 0))

        self.tabel.delete(*self.tabel.get_children())
        self.ringkasan.configure(text="Siap menjalankan operasi.")
        self.status.configure(text=f"[Siap] {judul}")

    def muat_data(self):
        path = cari_csv()

        if not os.path.exists(path):
            raise FileNotFoundError(
                "CSV tidak ditemukan:\n" + path
            )

        with open(path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)
            data = [row for row in reader if row]

        self.array = ArrayPesanan()
        self.linked = LinkedListPesanan()
        self.manajer_m2 = ManajerUndoRedo()

        for row in data:
            self.array.tambah_reguler(row)
            self.linked.tambah_reguler(row)
            if len(row) > 8 and str(row[8]).strip().upper() == "ANTRE":
                self.manajer_m2.enqueue(row)

        self.data = data
        self.laporan = LaporanPesanan(data)
        return data

    def pastikan_data(self):
        if not self.data:
            self.muat_data()

    def tampilkan(self, rows):
        self.tabel.delete(*self.tabel.get_children())

        for i, row in enumerate(rows, 1):
            if isinstance(row, (list, tuple)):
                values = (
                    i,
                    row[0] if len(row) > 0 else "",
                    harga_tampil(row[4]) if len(row) > 4 else "",
                    (row[7] or "—") if len(row) > 7 else "—",
                    row[2] if len(row) > 2 else "",
                    row[3] if len(row) > 3 else "",
                    row[1] if len(row) > 1 else "",
                    row[8] if len(row) > 8 else "",
                )
            else:
                values = (i, str(row), "", "", "", "", "", "")
            self.tabel.insert("", "end", values=values)

    def get_input(self, name, default=""):
        widget = self.input.get(name)
        return widget.get().strip() if widget else default

    def buat_pesanan(self):
        return [
            self.get_input("oid"),
            self.get_input("pelanggan"),
            self.get_input("resto"),
            self.get_input("menu"),
            self.get_input("harga"),
            self.get_input("prioritas"),
            time.strftime("%H:%M:%S"),
            "",
            "ANTRE"
        ]

    def catat(self, nama, detail, ms):
        self.command.insert(
            "end", f"{nama:<22} -> {detail:<25} {ms:.2f} ms\n"
        )
        self.command.see("end")

    def jalankan(self):
        key = self.aktif
        mulai = time.perf_counter()

        try:
            if key == "load":
                data = self.muat_data()
                self.tampilkan(data[:2000])
                self.ringkasan.configure(
                    text=f"{len(data):,} pesanan berhasil dimuat.\n"
                         f"Ditampilkan maksimal 2.000 baris.".replace(",", ".")
                )
                self.catat("load_csv", f"{len(data)} pesanan",
                           (time.perf_counter() - mulai) * 1000)

            elif key.startswith("array_") or key.startswith("linked_"):
                self.pastikan_data()
                obj = self.array if key.startswith("array_") else self.linked
                operasi = key.split("_", 1)[1]

                if operasi == "lihat":
                    index = int(self.get_input("index"))
                    row = obj.lihat(index)
                    if row is None:
                        raise IndexError("Indeks pesanan tidak ditemukan.")
                    self.tampilkan([row])
                    self.ringkasan.configure(
                        text=f"Pesanan indeks {index}: {row[0]}"
                    )

                elif operasi == "hapus":
                    index = int(self.get_input("index"))
                    row = obj.hapus(index)
                    if row is None:
                        raise IndexError("Indeks pesanan tidak ditemukan.")
                    self.data = self.ambil_semua(obj)
                    self.tampilkan(self.data[:2000])
                    self.ringkasan.configure(
                        text=f"Pesanan {row[0]} dihapus. Sisa data: {obj.size}."
                    )

                else:
                    row = self.buat_pesanan()
                    nama_method = "tambah_" + operasi
                    getattr(obj, nama_method)(row)
                    self.data = self.ambil_semua(obj)
                    self.tampilkan(self.data[:2000])
                    self.ringkasan.configure(
                        text=f"Pesanan {row[0]} ditambahkan.\n"
                             f"Jumlah elemen: {obj.size}."
                    )

                self.catat(key, "berhasil",
                           (time.perf_counter() - mulai) * 1000)

            elif key in ("insertion", "merge", "linear", "binary"):
                self.pastikan_data()
                if self.laporan is None:
                    self.laporan = LaporanPesanan(self.data)

                kunci = self.get_input("kunci", "oid")

                if key in ("insertion", "merge"):
                    jumlah = int(self.get_input("jumlah", str(len(self.data))))
                    if jumlah < 0:
                        raise ValueError("Jumlah baris tidak boleh negatif.")
                    if jumlah > len(self.data):
                        jumlah = len(self.data)

                    if key == "insertion":
                        hasil, banding, pindah, ms = self.laporan.insertion(
                            kunci=kunci, jumlah=jumlah
                        )
                        nama = "insertion_sort"
                    else:
                        hasil, banding, pindah, ms = self.laporan.merge(
                            kunci=kunci, jumlah=jumlah
                        )
                        nama = "merge_sort"

                    self.tampilkan(hasil[:2000])
                    self.ringkasan.configure(
                        text=f"{len(hasil):,} pesanan diurutkan menurut {kunci}.\n"
                             f"{banding:,} perbandingan, {pindah:,} pemindahan.\n"
                             f"Waktu: {ms:.3f} ms.".replace(",", ".")
                    )
                    self.catat(nama, "M3 - " + nama, ms)

                elif key == "linear":
                    target = self.get_input("target")
                    row, index, banding, ms = self.laporan.linear(target, kunci)
                    self.tampilkan([row] if row else [])
                    self.ringkasan.configure(
                        text=(f"Target {target} ditemukan pada indeks {index}."
                              if row else f"Target {target} tidak ditemukan.")
                             + f"\nPerbandingan: {banding}. Waktu: {ms:.3f} ms."
                    )
                    self.catat("linear_search", "selesai", ms)

                else:
                    target = self.get_input("target")
                    row, index, sort_banding, banding, sort_ms, ms = (
                        self.laporan.binary(target, kunci)
                    )
                    self.tampilkan([row] if row else [])
                    self.ringkasan.configure(
                        text=(f"Target {target} ditemukan pada indeks terurut {index}."
                              if row else f"Target {target} tidak ditemukan.")
                             + f"\nPerbandingan binary search: {banding}."
                             + f"\nWaktu search: {ms:.3f} ms; persiapan urutan: {sort_ms:.3f} ms."
                    )
                    self.catat("binary_search", f"{banding} perbandingan", ms)

            # --- PENANGANAN M2 (KASIR, STACK, QUEUE, UNDO/REDO) ---
            elif key == "postfix":
                ekspresi = self.get_input("expression")
                postfix, total, langkah = proses_kasir(ekspresi)
                ms = (time.perf_counter() - mulai) * 1000
                self.tabel.delete(*self.tabel.get_children())
                
                # Tampilkan langkah proses pada tabel
                for no, tok, tind, st, out in langkah:
                    self.tabel.insert("", "end", values=(no, tok, tind, st, out, "", "", ""))
                
                self.ringkasan.configure(
                    text=f"Infix: {ekspresi}\nPostfix: {' '.join(postfix)}\nTotal: {format_rupiah(total)}"
                )
                self.catat("postfix_kasir", f"Total: {format_rupiah(total)}", ms)

            elif key == "enqueue":
                self.pastikan_data()
                row = self.buat_pesanan()
                self.manajer_m2.enqueue(row)
                ms = (time.perf_counter() - mulai) * 1000
                self.tampilkan([row])
                self.ringkasan.configure(
                    text=f"Pesanan {row[0]} berhasil masuk antrean.\n"
                         f"Ukuran antrean circular: {self.manajer_m2.circular.size()}."
                )
                self.catat("queue_enqueue", row[0], ms)

            elif key in ("dequeue_naif", "dequeue_circular"):
                self.pastikan_data()
                jumlah = int(self.get_input("jumlah", "1"))
                items, ms_naif, ms_circ = self.manajer_m2.dequeue(jumlah)
                ms = (time.perf_counter() - mulai) * 1000
                
                self.tampilkan(items)
                durasi = ms_naif if key == "dequeue_naif" else ms_circ
                self.ringkasan.configure(
                    text=f"{len(items)} pesanan di-dequeue ({key}).\n"
                         f"Waktu eksekusi: {durasi:.3f} ms.\n"
                         f"Sisa antrean: {self.manajer_m2.circular.size()}."
                )
                self.catat(key, f"{len(items)} item", ms)

            elif key == "undo":
                self.pastikan_data()
                pesan = self.manajer_m2.undo_last()
                ms = (time.perf_counter() - mulai) * 1000
                self.ringkasan.configure(text=f"{pesan}\nSisa antrean: {self.manajer_m2.circular.size()}")
                self.catat("undo_stack", "Undo berhasil", ms)

            elif key == "redo":
                self.pastikan_data()
                pesan = self.manajer_m2.redo_last()
                ms = (time.perf_counter() - mulai) * 1000
                self.ringkasan.configure(text=f"{pesan}\nSisa antrean: {self.manajer_m2.circular.size()}")
                self.catat("redo_stack", "Redo berhasil", ms)

            total_ms = (time.perf_counter() - mulai) * 1000
            self.status.configure(text=f"[{key}] {total_ms:.2f} ms")

        except Exception as error:
            self.ringkasan.configure(text=f"Operasi gagal: {error}")
            self.status.configure(text=f"[ERROR] {key}")
            messagebox.showerror("Operasi gagal", str(error))

    def ambil_semua(self, obj):
        hasil = []

        if isinstance(obj, ArrayPesanan):
            for i in range(obj.size):
                hasil.append(obj.lihat(i))
        else:
            node = obj.head
            while node is not None:
                hasil.append(node.data)
                node = node.next

        return hasil


def main():
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()


if __name__ == "__main__":
    main()