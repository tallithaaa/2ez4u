"""
2EZ4U Food Delivery - Frontend Tkinter (tema Fresh Pastel)
Letakkan file ini di folder  frontend/ui.py
Struktur proyek:
    ROOT/
      backend/m1_pesanan.py, m2_antrean.py, m3_laporan.py
      data/pesanan.csv
      frontend/ui.py
"""
import csv
import os
import re
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")

sys.path.insert(0, ROOT)
sys.path.insert(0, BACKEND)

from m1_pesanan import ArrayPesanan, LinkedListPesanan
from m2_antrean import ManajerUndoRedo, format_rupiah, proses_kasir
from m3_laporan import LaporanPesanan

# ---------------------------------------------------------------- PALET WARNA
# 5 warna dari gambar referensi
PINK = "#E6AAAE"          # pink (tombol utama, heading tabel)
OLIVE = "#CACB8A"         # olive (aksen, baris terpilih)
PEACH = "#E9BDAD"         # peach (hover, status bar)
MINT = "#ADDAC6"          # mint (header, aksen)
MINT_LIGHT = "#C5E7D9"    # mint muda (sidebar, baris belang)
# turunan untuk keterbacaan
MINT_PALE = "#F3FBF7"     # background aplikasi
CREAM = "#FFF9F6"         # kartu / panel
SELECTED = "#ADDAC6"      # menu terpilih
TEXT = "#4A3B3D"          # teks utama
DARK = "#5B4044"          # teks gelap di atas pastel
ROSE = "#A9626C"          # label / judul bagian
MUTED = "#8A6F72"         # teks redup

COLUMNS = ("#", "oid", "harga", "selesai",
           "resto", "menu", "pelanggan", "status")
POSTFIX_COLS = ("langkah", "token", "tindakan", "stack", "output")

MENU = [
    ("DATA", [
        ("Load", "load"),
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
    "postfix": ("Stack: Postfix (mesin kasir)", "Masukkan ekspresi infix untuk diproses menjadi postfix lalu dievaluasi."),
    "undo": ("Stack: Undo", "Batalkan aksi terakhir pada antrean M2."),
    "redo": ("Stack: Redo", "Ulangi aksi antrean M2 yang dibatalkan."),
    "enqueue": ("Queue: Enqueue", "Tambahkan pesanan baru ke antrean M2."),
    "dequeue_naif": ("Queue: Dequeue naif", "Keluarkan pesanan dari depan antrean naif (geser elemen)."),
    "dequeue_circular": ("Queue: Dequeue circular", "Keluarkan pesanan dari depan antrean melingkar."),
    "insertion": ("Sort: insertion sort, O(n²)", "Mengurutkan data dengan insertion sort."),
    "merge": ("Sort: merge sort, O(n log n)", "Membelah data lalu menggabungkan bagian yang terurut."),
    "linear": ("Search: linear search, O(n)", "Memeriksa data satu per satu."),
    "binary": ("Search: binary search, O(log n)", "Mencari data pada data terurut dengan binary search."),
}


# ---------------------------------------------------------------- HELPER
def cari_csv():
    return os.path.join(ROOT, "data", "pesanan.csv")


def harga_tampil(value):
    try:
        return f"{int(float(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value or "—")


def fmt_int(n):
    """Format angka dengan pemisah titik (gaya Indonesia)."""
    return f"{n:,}".replace(",", ".")


def ukuran(obj):
    """Ambil ukuran struktur data, baik size berupa atribut maupun method."""
    s = obj.size
    return s() if callable(s) else s


def mix(a, b, t):
    """Campur dua warna hex (t=0 -> a, t=1 -> b)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(p + (q - p) * t) for p, q in zip(ca, cb))


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class Aplikasi:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1480x920")
        self.root.minsize(1100, 700)
        self.root.configure(bg=MINT_PALE)

        # --- struktur data M1 / M2 / M3 (satu sumber data bersama)
        self.array = ArrayPesanan()
        self.linked = LinkedListPesanan()
        self.manajer_m2 = ManajerUndoRedo()
        self.data = []
        self.laporan = None
        self.oid_dipakai = set()

        self.aktif = "merge"
        self.input = {}

        self.buat_tampilan()
        self.pilih_menu("merge")

    # ------------------------------------------------------------ TAMPILAN
    def buat_tampilan(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=27, font=("Consolas", 10),
                        background=CREAM, fieldbackground=CREAM,
                        foreground=TEXT, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background=PINK, foreground=DARK, relief="flat")
        style.map("Treeview",
                  background=[("selected", OLIVE)],
                  foreground=[("selected", DARK)])
        style.map("Treeview.Heading", background=[("active", PEACH)])
        style.configure("TCombobox", fieldbackground=CREAM, background=MINT)
        for arah in ("Vertical", "Horizontal"):
            style.configure(f"{arah}.TScrollbar", background=MINT,
                            troughcolor=MINT_LIGHT, bordercolor=MINT_LIGHT,
                            arrowcolor=DARK)

        # ---------- HEADER (gradasi mint segar)
        self.header = tk.Canvas(self.root, height=92, bg=MINT_LIGHT,
                                highlightthickness=0)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self.gambar_header)

        # ---------- BODY
        body = tk.Frame(self.root, bg=MINT_PALE)
        body.pack(fill="both", expand=True, padx=8, pady=6)

        # ----- sidebar kiri
        kiri = tk.Frame(body, bg=MINT_LIGHT, width=410)
        kiri.pack(side="left", fill="y", padx=(0, 8))
        kiri.pack_propagate(False)

        tk.Frame(kiri, height=6, bg=PEACH).pack(fill="x")

        wadah = tk.Frame(kiri, bg=MINT_LIGHT)
        wadah.pack(fill="both", expand=True)

        canvas = tk.Canvas(wadah, bg=MINT_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(wadah, orient="vertical",
                                  command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        menu_frame = tk.Frame(canvas, bg=MINT_LIGHT)
        window = canvas.create_window((0, 0), window=menu_frame, anchor="nw")
        menu_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(
            window, width=e.width))

        # scroll dengan mouse wheel hanya saat kursor di sidebar
        def _wheel(event):
            delta = -1 * (event.delta // 120) if event.delta else (
                -1 if event.num == 4 else 1)
            canvas.yview_scroll(delta, "units")

        def _bind(_):
            canvas.bind_all("<MouseWheel>", _wheel)
            canvas.bind_all("<Button-4>", _wheel)
            canvas.bind_all("<Button-5>", _wheel)

        def _unbind(_):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _bind)
        canvas.bind("<Leave>", _unbind)

        self.tombol_menu = {}
        for judul, items in MENU:
            tk.Label(menu_frame, text="●  " + judul, bg=MINT_LIGHT,
                     fg=ROSE, anchor="w",
                     font=("Segoe UI", 10, "bold")
                     ).pack(fill="x", padx=10, pady=(12, 3))

            for label, key in items:
                b = tk.Button(menu_frame, text=label, anchor="w",
                              font=("Segoe UI", 10), bg=CREAM, fg=TEXT,
                              activebackground=PINK, activeforeground=DARK,
                              relief="flat", bd=0, padx=12, pady=5,
                              cursor="hand2",
                              command=lambda k=key: self.pilih_menu(k))
                b.pack(fill="x", padx=8, pady=1)
                b.bind("<Enter>", lambda e, k=key: self.hover(k, True))
                b.bind("<Leave>", lambda e, k=key: self.hover(k, False))
                self.tombol_menu[key] = b

        # ----- panel kanan
        kanan = tk.Frame(body, bg=CREAM, highlightthickness=2,
                         highlightbackground=MINT)
        kanan.pack(side="left", fill="both", expand=True)

        tk.Frame(kanan, height=6, bg=PINK).pack(fill="x")

        self.judul = tk.Label(kanan, text="", bg=CREAM, fg=DARK,
                              anchor="w", font=("Segoe UI", 16, "bold"))
        self.judul.pack(fill="x", padx=18, pady=(10, 3))

        self.deskripsi = tk.Label(kanan, text="", bg=CREAM, fg=MUTED,
                                  anchor="w", justify="left",
                                  font=("Segoe UI", 10))
        self.deskripsi.pack(fill="x", padx=18, pady=(0, 10))

        # form: area field (grid, bisa wrap) + tombol aksi di kanan
        self.form = tk.Frame(kanan, bg=CREAM)
        self.form.pack(fill="x", padx=15, pady=5)
        self.form_fields = tk.Frame(self.form, bg=CREAM)
        self.form_fields.pack(side="left", anchor="nw")
        self.form_action = tk.Frame(self.form, bg=CREAM)
        self.form_action.pack(side="right", anchor="ne")

        ttk.Separator(kanan).pack(fill="x", pady=8)

        self.ringkasan = tk.Label(
            kanan, text="Tekan Load untuk membaca data CSV.",
            bg=CREAM, fg=TEXT, anchor="w", justify="left",
            font=("Segoe UI", 11))
        self.ringkasan.pack(fill="x", padx=17, pady=8)

        table_frame = tk.Frame(kanan, bg=CREAM)
        table_frame.pack(fill="both", expand=True, padx=14, pady=8)

        self.tabel = ttk.Treeview(table_frame, columns=COLUMNS,
                                  show="headings")
        self.tabel.tag_configure("ganjil", background=CREAM)
        self.tabel.tag_configure("genap", background=MINT_LIGHT)

        sy = ttk.Scrollbar(table_frame, orient="vertical",
                           command=self.tabel.yview)
        sx = ttk.Scrollbar(table_frame, orient="horizontal",
                           command=self.tabel.xview)
        self.tabel.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        self.tabel.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.set_kolom("umum")

        # ---------- COMMAND LOG
        tk.Label(self.root, text="COMMAND", bg=MINT_PALE, fg=ROSE,
                 anchor="w", font=("Segoe UI", 10, "bold")
                 ).pack(fill="x", padx=14)

        self.command = tk.Text(self.root, height=4, font=("Consolas", 10),
                               wrap="none", bg=CREAM, fg=TEXT,
                               relief="flat", highlightthickness=1,
                               highlightbackground=MINT,
                               highlightcolor=PINK)
        self.command.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(self.root,
                 text="Pilih menu di sebelah kiri untuk menjalankan operasi.",
                 bg=MINT, fg=DARK, anchor="w", padx=12, pady=7
                 ).pack(fill="x", padx=14, pady=(0, 6))

        # ---------- STATUS BAR (peach)
        self.status_bar = tk.Canvas(self.root, height=34, bg=PEACH,
                                    highlightthickness=0)
        self.status_bar.pack(fill="x", side="bottom", padx=8, pady=(0, 8))
        self.status_bar.bind("<Configure>", self.gambar_status)
        self.status_teks = "[Siap] 2EZ4U Food Delivery"

    # ---- gambar header & status bar
    def gambar_header(self, event):
        c, w, h = self.header, event.width, event.height
        c.delete("all")

        # 1) gradasi mint segar dari kiri ke kanan
        for x in range(0, w, 4):
            c.create_rectangle(x, 0, x + 4, h, outline="",
                               fill=mix(MINT_LIGHT, MINT, x / max(w, 1)))

        # 2) kartu judul: logo bulat + nama + subjudul
        rounded_rect(c, 16, 12, 410, h - 12, 26,
                     fill=CREAM, outline=PINK, width=3)
        d = h - 48
        c.create_oval(32, 24, 32 + d, 24 + d, fill=PINK, outline="")
        c.create_text(32 + d / 2, h / 2, text="2Z", fill=CREAM,
                      font=("Segoe UI", 18, "bold"))
        c.create_text(100, h / 2 - 12, anchor="w", text="2EZ4U",
                      fill=DARK, font=("Segoe UI", 24, "bold"))
        c.create_text(102, h / 2 + 17, anchor="w", text="FOOD DELIVERY",
                      fill=MUTED, font=("Segoe UI", 10, "bold"))

        # 3) badge modul di kanan
        for i, (teks, warna_badge) in enumerate(
                (("M1", PINK), ("M2", OLIVE), ("M3", PEACH))):
            x = w - 250 + i * 78
            rounded_rect(c, x, 26, x + 66, h - 26, 16,
                         fill=warna_badge, outline=CREAM, width=2)
            c.create_text(x + 33, h / 2, text=teks, fill=DARK,
                          font=("Segoe UI", 13, "bold"))

    def gambar_status(self, event=None):
        c = self.status_bar
        w = c.winfo_width()
        h = c.winfo_height()
        c.delete("all")
        c.create_text(14, h / 2, anchor="w", text=self.status_teks,
                      fill=DARK, font=("Consolas", 10, "bold"))

    def set_status(self, teks):
        self.status_teks = teks
        self.gambar_status()

    def hover(self, key, masuk):
        if key == self.aktif:
            return
        self.tombol_menu[key].configure(bg=PEACH if masuk else CREAM)

    # ------------------------------------------------------------ KOLOM TABEL
    def set_kolom(self, mode):
        """Ganti kolom tabel: 'postfix' untuk tabel langkah kasir, selain itu data pesanan."""
        if mode == "postfix":
            lebar = {"langkah": 80, "token": 80, "tindakan": 280,
                     "stack": 140, "output": 260}
            self.tabel.configure(columns=POSTFIX_COLS)
            for col in POSTFIX_COLS:
                self.tabel.heading(col, text=col)
                self.tabel.column(
                    col, width=lebar[col], minwidth=60,
                    anchor="center" if col in ("langkah", "token") else "w")
        else:
            self.tabel.configure(columns=COLUMNS)
            for col in COLUMNS:
                self.tabel.heading(col, text=col)
                self.tabel.column(col, width=130, minwidth=75, anchor="w")
            self.tabel.column("#", width=45, anchor="center")
            self.tabel.column("oid", width=150)
            self.tabel.column("harga", width=100, anchor="e")

    # ------------------------------------------------------------ MENU
    def pilih_menu(self, key):
        self.aktif = key

        for nama, b in self.tombol_menu.items():
            b.configure(bg=SELECTED if nama == key else CREAM,
                        font=("Segoe UI", 10,
                              "bold" if nama == key else "normal"))

        judul, deskripsi = DESKRIPSI[key]
        self.judul.configure(text=judul)
        self.deskripsi.configure(text=deskripsi)

        for w in self.form_fields.winfo_children():
            w.destroy()
        for w in self.form_action.winfo_children():
            w.destroy()
        self.input = {}
        self._slot = 0

        def taruh(frame):
            # maksimal 3 field per baris supaya tidak melebar keluar layar
            frame.grid(row=self._slot // 3, column=self._slot % 3,
                       sticky="nw", padx=(0, 15), pady=(0, 4))
            self._slot += 1

        def buat_entry(label, nama, nilai="", width=16):
            f = tk.Frame(self.form_fields, bg=CREAM)
            taruh(f)
            tk.Label(f, text=label, bg=CREAM, fg=ROSE,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            e = tk.Entry(f, width=width, font=("Consolas", 11),
                         bg="white", fg=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=MINT,
                         highlightcolor=PINK)
            e.insert(0, nilai)
            e.pack(anchor="w", pady=4, ipady=2)
            self.input[nama] = e

        def buat_combo(label, nama, pilihan, awal):
            f = tk.Frame(self.form_fields, bg=CREAM)
            taruh(f)
            tk.Label(f, text=label, bg=CREAM, fg=ROSE,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            cb = ttk.Combobox(f, values=pilihan, state="readonly", width=15)
            cb.set(awal)
            cb.pack(anchor="w", pady=4)
            self.input[nama] = cb

        if key in ("array_lihat", "array_hapus", "linked_lihat", "linked_hapus"):
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
            buat_entry("Ekspresi infix", "expression",
                       "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", 44)

        elif key in ("insertion", "merge"):
            buat_entry("Jumlah baris", "jumlah",
                       "10" if key == "insertion" else "4000")
            buat_combo("Urutkan menurut", "kunci",
                       ["oid", "harga", "selesai"],
                       "harga" if key == "insertion" else "oid")

        elif key in ("linear", "binary"):
            buat_entry("Target", "target", "O-000001", 18)
            buat_combo("Cari menurut", "kunci",
                       ["oid", "harga", "selesai"], "oid")

        elif key in ("dequeue_naif", "dequeue_circular"):
            buat_entry("Jumlah dequeue", "jumlah", "1")

        # kolom tabel: postfix punya kolom sendiri, menu lain kembali ke kolom pesanan
        self.set_kolom("postfix" if key == "postfix" else "umum")

        teks_tombol = ("URUTKAN" if key in ("insertion", "merge")
                       else "CARI" if key in ("linear", "binary")
                       else "JALANKAN")
        tombol = tk.Button(self.form_action, text=teks_tombol, bg=PINK,
                           fg=DARK, activebackground=OLIVE,
                           activeforeground=DARK, relief="flat",
                           font=("Segoe UI", 11, "bold"), padx=24, pady=7,
                           cursor="hand2", command=self.jalankan)
        tombol.pack(padx=8, pady=(18, 0))
        tombol.bind("<Enter>", lambda e: tombol.configure(bg=OLIVE))
        tombol.bind("<Leave>", lambda e: tombol.configure(bg=PINK))

        self.tabel.delete(*self.tabel.get_children())
        self.ringkasan.configure(text="Siap menjalankan operasi.")
        self.set_status(f"[Siap] {judul}")

    # ------------------------------------------------------------ DATA / SINKRON
    def muat_data(self):
        path = cari_csv()
        if not os.path.exists(path):
            raise FileNotFoundError("CSV tidak ditemukan:\n" + path)

        with open(path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)
            data = [row for row in reader if row]

        # reset semua modul supaya M1, M2, M3 mulai dari data yang sama
        self.array = ArrayPesanan()
        self.linked = LinkedListPesanan()
        self.manajer_m2 = ManajerUndoRedo()

        for row in data:
            self.array.tambah_reguler(list(row))
            self.linked.tambah_reguler(list(row))
            if len(row) > 8 and str(row[8]).strip().upper() == "ANTRE":
                self.manajer_m2.enqueue(list(row))

        self.data = data
        self.laporan = LaporanPesanan(data)
        self.oid_dipakai = {str(r[0]) for r in data if r}
        return data

    def pastikan_data(self):
        if not self.data:
            self.muat_data()

    def sinkron(self, obj):
        """Setelah M1 berubah, M3 (sort/search) memakai data terbaru."""
        self.data = self.ambil_semua(obj)
        self.laporan = LaporanPesanan(self.data)
        self.oid_dipakai = {str(r[0]) for r in self.data if r}

    def ambil_semua(self, obj):
        hasil = []
        if isinstance(obj, ArrayPesanan):
            for i in range(ukuran(obj)):
                hasil.append(obj.lihat(i))
        else:
            node = obj.head
            while node is not None:
                hasil.append(node.data)
                node = node.next
        return hasil

    # ------------------------------------------------------------ TAMPIL
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
            self.tabel.insert("", "end", values=values,
                              tags=("genap" if i % 2 == 0 else "ganjil",))

    def get_input(self, name, default=""):
        widget = self.input.get(name)
        return widget.get().strip() if widget else default

    def buat_pesanan(self):
        oid = self.get_input("oid")
        if not oid:
            raise ValueError("OID tidak boleh kosong.")
        if oid in self.oid_dipakai:
            raise ValueError(f"OID {oid} sudah ada. Gunakan OID lain.")

        harga = self.get_input("harga")
        try:
            if float(harga) < 0:
                raise ValueError
        except ValueError:
            raise ValueError("Harga harus berupa angka tidak negatif.")

        prioritas = self.get_input("prioritas", "0")
        try:
            int(prioritas)
        except ValueError:
            raise ValueError("Prioritas harus berupa bilangan bulat.")

        return [
            oid,
            self.get_input("pelanggan"),
            self.get_input("resto"),
            self.get_input("menu"),
            harga,
            prioritas,
            time.strftime("%H:%M:%S"),
            "",
            "ANTRE",
        ]

    def naikkan_oid(self):
        """Setelah sukses menambah, OID di form dinaikkan satu agar tidak bentrok."""
        e = self.input.get("oid")
        if not e:
            return
        m = re.match(r"^(.*?)(\d+)$", e.get().strip())
        if m:
            baru = m.group(1) + str(int(m.group(2)) + 1).zfill(len(m.group(2)))
            e.delete(0, "end")
            e.insert(0, baru)

    def catat(self, nama, detail, ms):
        waktu = time.strftime("%H:%M:%S")
        self.command.insert(
            "end", f"[{waktu}] {nama:<18} -> {detail:<26} {ms:.2f} ms\n")
        self.command.see("end")

    # ------------------------------------------------------------ AKSI UTAMA
    def jalankan(self):
        key = self.aktif
        mulai = time.perf_counter()

        try:
            # ================= DATA
            if key == "load":
                data = self.muat_data()
                self.tampilkan(data[:2000])
                self.ringkasan.configure(
                    text=f"{fmt_int(len(data))} pesanan berhasil dimuat.\n"
                         "Ditampilkan maksimal 2.000 baris.")
                self.catat("load_csv", f"{len(data)} pesanan",
                           (time.perf_counter() - mulai) * 1000)

            # ================= M1
            elif key.startswith("array_") or key.startswith("linked_"):
                self.pastikan_data()
                utama = self.array if key.startswith("array_") else self.linked
                lain = self.linked if utama is self.array else self.array
                operasi = key.split("_", 1)[1]

                if operasi == "lihat":
                    index = int(self.get_input("index"))
                    row = utama.lihat(index) if 0 <= index < ukuran(utama) else None
                    if row is None:
                        raise IndexError("Indeks pesanan tidak ditemukan.")
                    self.tampilkan([row])
                    self.ringkasan.configure(
                        text=f"Pesanan indeks {index}: {row[0]}")

                elif operasi == "hapus":
                    index = int(self.get_input("index"))
                    if not 0 <= index < ukuran(utama):
                        raise IndexError("Indeks pesanan tidak ditemukan.")
                    row = utama.hapus(index)
                    if row is None:
                        raise IndexError("Indeks pesanan tidak ditemukan.")
                    lain.hapus(index)           # jaga array & linked list tetap kembar
                    self.sinkron(utama)         # M3 ikut memakai data terbaru
                    self.tampilkan(self.data[:2000])
                    self.ringkasan.configure(
                        text=f"Pesanan {row[0]} dihapus. "
                             f"Sisa data: {fmt_int(ukuran(utama))}.")

                else:
                    row = self.buat_pesanan()
                    nama_method = "tambah_" + operasi
                    getattr(utama, nama_method)(list(row))
                    getattr(lain, nama_method)(list(row))
                    self.sinkron(utama)
                    posisi = next((i for i, r in enumerate(self.data)
                                   if r and r[0] == row[0]), None)
                    self.tampilkan([row])
                    self.ringkasan.configure(
                        text=f"Pesanan {row[0]} ditambahkan"
                             + (f" pada indeks {posisi}." if posisi is not None else ".")
                             + f"\nJumlah elemen: {fmt_int(ukuran(utama))}.")
                    self.naikkan_oid()

                self.catat(key, "berhasil",
                           (time.perf_counter() - mulai) * 1000)

            # ================= M3
            elif key in ("insertion", "merge", "linear", "binary"):
                self.pastikan_data()
                if self.laporan is None:
                    self.laporan = LaporanPesanan(self.data)

                kunci = self.get_input("kunci", "oid")

                if key in ("insertion", "merge"):
                    jumlah = int(self.get_input("jumlah", str(len(self.data))))
                    if jumlah < 0:
                        raise ValueError("Jumlah baris tidak boleh negatif.")
                    jumlah = min(jumlah, len(self.data))

                    if key == "insertion":
                        hasil, banding, pindah, ms = self.laporan.insertion(
                            kunci=kunci, jumlah=jumlah)
                        nama = "insertion_sort"
                    else:
                        hasil, banding, pindah, ms = self.laporan.merge(
                            kunci=kunci, jumlah=jumlah)
                        nama = "merge_sort"

                    self.tampilkan(hasil[:2000])
                    self.ringkasan.configure(
                        text=f"{fmt_int(len(hasil))} pesanan diurutkan menurut {kunci}.\n"
                             f"{fmt_int(banding)} perbandingan, {fmt_int(pindah)} pemindahan.\n"
                             f"Waktu: {ms:.3f} ms.")
                    self.catat(nama, "M3 - " + nama, ms)

                elif key == "linear":
                    target = self.get_input("target")
                    row, index, banding, ms = self.laporan.linear(target, kunci)
                    self.tampilkan([row] if row else [])
                    self.ringkasan.configure(
                        text=(f"Target {target} ditemukan pada indeks {index}."
                              if row else f"Target {target} tidak ditemukan.")
                             + f"\nPerbandingan: {fmt_int(banding)}. Waktu: {ms:.3f} ms.")
                    self.catat("linear_search", f"{banding} perbandingan", ms)

                else:
                    target = self.get_input("target")
                    row, index, sort_banding, banding, sort_ms, ms = (
                        self.laporan.binary(target, kunci))
                    self.tampilkan([row] if row else [])
                    self.ringkasan.configure(
                        text=(f"Target {target} ditemukan pada indeks terurut {index}."
                              if row else f"Target {target} tidak ditemukan.")
                             + f"\nPerbandingan binary search: {fmt_int(banding)}."
                             + f"\nWaktu search: {ms:.3f} ms; "
                               f"persiapan urutan: {sort_ms:.3f} ms.")
                    self.catat("binary_search", f"{banding} perbandingan", ms)

            # ================= M2
            elif key == "postfix":
                ekspresi = self.get_input("expression")
                if not ekspresi:
                    raise ValueError("Ekspresi tidak boleh kosong.")
                postfix, total, langkah = proses_kasir(ekspresi)
                ms = (time.perf_counter() - mulai) * 1000

                self.set_kolom("postfix")
                self.tabel.delete(*self.tabel.get_children())
                for n, (no, tok, tind, st, out) in enumerate(langkah, 1):
                    self.tabel.insert("", "end",
                                      values=(no, tok, tind, st, out),
                                      tags=("genap" if n % 2 == 0 else "ganjil",))

                self.ringkasan.configure(
                    text=f"Struk: {ekspresi}\n"
                         f"Postfix: {' '.join(postfix)}\n"
                         f"Total: {format_rupiah(total)}")
                self.catat("stack_postfix", "-> M2 - stack", ms)

            elif key == "enqueue":
                self.pastikan_data()
                row = self.buat_pesanan()
                self.manajer_m2.enqueue(list(row))
                self.oid_dipakai.add(row[0])
                ms = (time.perf_counter() - mulai) * 1000
                self.tampilkan([row])
                self.ringkasan.configure(
                    text=f"Pesanan {row[0]} berhasil masuk antrean.\n"
                         f"Ukuran antrean circular: "
                         f"{fmt_int(self.manajer_m2.circular.size())}.")
                self.naikkan_oid()
                self.catat("queue_enqueue", row[0], ms)

            elif key in ("dequeue_naif", "dequeue_circular"):
                self.pastikan_data()
                jumlah = int(self.get_input("jumlah", "1"))
                if jumlah < 1:
                    raise ValueError("Jumlah dequeue minimal 1.")
                items, ms_naif, ms_circ = self.manajer_m2.dequeue(jumlah)
                ms = (time.perf_counter() - mulai) * 1000

                self.tampilkan(items)
                durasi = ms_naif if key == "dequeue_naif" else ms_circ
                self.ringkasan.configure(
                    text=f"{len(items)} pesanan di-dequeue ({key}).\n"
                         f"Waktu {key.split('_')[1]}: {durasi:.3f} ms "
                         f"(naif {ms_naif:.3f} ms | circular {ms_circ:.3f} ms).\n"
                         f"Sisa antrean: {fmt_int(self.manajer_m2.circular.size())}.")
                self.catat(key, f"{len(items)} item", ms)

            elif key in ("undo", "redo"):
                self.pastikan_data()
                if key == "undo":
                    pesan = self.manajer_m2.undo_last()
                else:
                    pesan = self.manajer_m2.redo_last()
                ms = (time.perf_counter() - mulai) * 1000
                self.ringkasan.configure(
                    text=f"{pesan}\nSisa antrean: "
                         f"{fmt_int(self.manajer_m2.circular.size())}")
                self.catat(f"{key}_stack", str(pesan)[:26], ms)

            total_ms = (time.perf_counter() - mulai) * 1000
            self.set_status(f"[{key}] {total_ms:.2f} ms")

        except Exception as error:
            self.ringkasan.configure(text=f"Operasi gagal: {error}")
            self.set_status(f"[ERROR] {key}")
            messagebox.showerror("Operasi gagal", str(error))


def main():
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()


if __name__ == "__main__":
    main()