import time

try:
    from .m1_pesanan import ArrayPesanan
except ImportError:
    from m1_pesanan import ArrayPesanan


# Penghubung agar M2 bisa memakai struktur ArrayPesanan dari M1,
# meskipun nama metode M1 berbeda dari append/get/delete.
def array_tambah(array, nilai):
    if array.size == array.capacity:
        array._resize(array.capacity * 2)
    array.data[array.size] = nilai
    array.size += 1


def array_get(array, indeks):
    if indeks < 0 or indeks >= array.size:
        return None
    return array.data[indeks]


def array_hapus(array, indeks):
    if indeks < 0 or indeks >= array.size:
        return None

    nilai = array.data[indeks]
    for i in range(indeks, array.size - 1):
        array.data[i] = array.data[i + 1]

    array.data[array.size - 1] = None
    array.size -= 1
    return nilai


def array_sisip(array, indeks, nilai):
    if indeks < 0:
        indeks = 0
    if indeks > array.size:
        indeks = array.size

    if array.size == array.capacity:
        array._resize(array.capacity * 2)

    for i in range(array.size, indeks, -1):
        array.data[i] = array.data[i - 1]

    array.data[indeks] = nilai
    array.size += 1


class Stack:
    def __init__(self):
        self.items = ArrayPesanan()

    def push(self, item):
        array_tambah(self.items, item)

    def pop(self):
        if self.is_empty():
            return None
        return array_hapus(self.items, self.items.size - 1)

    def peek(self):
        if self.is_empty():
            return None
        return array_get(self.items, self.items.size - 1)

    def is_empty(self):
        return self.items.size == 0

    def size(self):
        return self.items.size

    def teks(self):
        if self.is_empty():
            return "kosong"

        teks_stack = ""
        for i in range(self.items.size):
            if i > 0:
                teks_stack += " "
            teks_stack += str(array_get(self.items, i))
        return teks_stack


class AntreanNaif:
    """Antrean array naif: dequeue menggeser elemen, sehingga O(n)."""
    def __init__(self):
        self.data = ArrayPesanan()
        self.total_geseran = 0

    def enqueue(self, item):
        array_tambah(self.data, item)

    def dequeue(self):
        if self.is_empty():
            return None
        self.total_geseran += self.data.size - 1
        return array_hapus(self.data, 0)

    def pop_belakang(self):
        if self.is_empty():
            return None
        return array_hapus(self.data, self.data.size - 1)

    def push_depan(self, item):
        array_sisip(self.data, 0, item)

    def get(self, i):
        return array_get(self.data, i)

    def is_empty(self):
        return self.data.size == 0

    def size(self):
        return self.data.size

    def __len__(self):
        return self.data.size


class AntreanMelingkar:
    def __init__(self, capacity=4):
        if capacity < 1:
            capacity = 1
        self.capacity = capacity
        self.data = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geseran = 0

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.count):
            new_data[i] = self.data[(self.front + i) % self.capacity]
        self.data = new_data
        self.front = 0
        self.rear = self.count
        self.capacity = new_capacity

    def enqueue(self, item):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            return None
        item = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item

    def pop_belakang(self):
        if self.is_empty():
            return None
        self.rear = (self.rear - 1) % self.capacity
        item = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return item

    def push_depan(self, item):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.front = (self.front - 1) % self.capacity
        self.data[self.front] = item
        self.count += 1

    def get(self, i):
        if i < 0 or i >= self.count:
            raise IndexError("Indeks di luar jangkauan")
        return self.data[(self.front + i) % self.capacity]

    def is_empty(self):
        return self.count == 0

    def size(self):
        return self.count

    def __len__(self):
        return self.count


def format_rupiah(n):
    negatif = n < 0
    if negatif:
        n = -n

    s = str(n)
    hasil = ""
    hitung = 0
    for i in range(len(s) - 1, -1, -1):
        if hitung == 3:
            hasil = "." + hasil
            hitung = 0
        hasil = s[i] + hasil
        hitung += 1

    if negatif:
        return "-Rp " + hasil
    return "Rp " + hasil


def prioritas_operator(op):
    if op == "+" or op == "-":
        return 1
    if op == "*" or op == "/":
        return 2
    return 0


def pisah_token(ekspresi):
    tokens = []
    i = 0
    n = len(ekspresi)

    while i < n:
        c = ekspresi[i]
        if c == " ":
            i += 1
            continue

        if c in "0123456789":
            num = ""
            while i < n and ekspresi[i] in "0123456789":
                num += ekspresi[i]
                i += 1
            tokens.append(num)
        else:
            tokens.append(c)
            i += 1

    return tokens


def gabung_token(tokens):
    hasil = ""
    for i in range(len(tokens)):
        if i > 0:
            hasil += " "
        hasil += str(tokens[i])
    return hasil


def ke_postfix(ekspresi, langkah=None):
    tokens = pisah_token(ekspresi)
    output = []
    op_stack = Stack()
    nomor = 0

    for token in tokens:
        nomor += 1

        if token.isdigit():
            output.append(token)
            tindakan = "angka, langsung keluar"
        elif token == "(":
            op_stack.push(token)
            tindakan = "push ("
        elif token == ")":
            ketemu = False
            while not op_stack.is_empty():
                atas = op_stack.pop()
                if atas == "(":
                    ketemu = True
                    break
                output.append(atas)
            if not ketemu:
                raise ValueError("Kurung tutup tanpa pasangan")
            tindakan = "pop sampai ( , buang ("
        elif token in ("+", "-", "*", "/"):
            ada_pop = False
            while (not op_stack.is_empty()
                   and op_stack.peek() != "("
                   and prioritas_operator(op_stack.peek()) >= prioritas_operator(token)):
                output.append(op_stack.pop())
                ada_pop = True
            op_stack.push(token)
            if ada_pop:
                tindakan = "pop yang lebih/sama kuat, push " + token
            else:
                tindakan = "push " + token
        else:
            raise ValueError("Karakter tidak dikenali: " + token)

        if langkah is not None:
            langkah.append(("1." + str(nomor), token, tindakan,
                            op_stack.teks(), gabung_token(output)))

    while not op_stack.is_empty():
        atas = op_stack.pop()
        if atas == "(":
            raise ValueError("Kurung buka tanpa pasangan")
        output.append(atas)

    if langkah is not None:
        langkah.append(("1.akhir", "-", "pop sisa stack",
                        "kosong", gabung_token(output)))

    return output


def hitung_postfix(postfix_tokens, langkah=None):
    """Operand kanan di-pop lebih dahulu saat mengevaluasi operator."""
    val_stack = Stack()
    nomor = 0

    for token in postfix_tokens:
        nomor += 1

        if token.isdigit():
            val_stack.push(int(token))
            tindakan = "operand, push " + token
        else:
            if val_stack.size() < 2:
                raise ValueError("Ekspresi tidak valid")

            b = val_stack.pop()
            a = val_stack.pop()

            if token == "+":
                res = a + b
            elif token == "-":
                res = a - b
            elif token == "*":
                res = a * b
            elif token == "/":
                if b == 0:
                    raise ValueError("Pembagian dengan nol")
                res = a // b
            else:
                raise ValueError("Operator tidak dikenali: " + token)

            val_stack.push(res)
            tindakan = "pop " + str(b) + " dan " + str(a) + " -> " + str(a) + token + str(b) + " = " + str(res)

        if langkah is not None:
            langkah.append(("2." + str(nomor), token, tindakan,
                            val_stack.teks(), ""))

    if val_stack.size() != 1:
        raise ValueError("Ekspresi tidak valid")

    return val_stack.pop()


def proses_kasir(ekspresi):
    langkah = []
    postfix = ke_postfix(ekspresi, langkah)
    total = hitung_postfix(postfix, langkah)
    return postfix, total, langkah


class ManajerUndoRedo:
    def __init__(self, antrean_naif=None, antrean_circular=None):
        if antrean_naif is None:
            self.naif = AntreanNaif()
        else:
            self.naif = antrean_naif

        if antrean_circular is None:
            self.circular = AntreanMelingkar()
        else:
            self.circular = antrean_circular

        self.undo_stack = Stack()
        self.redo_stack = Stack()
        self._naif_basi = False

    def sinkron_naif(self):
        if not self._naif_basi:
            return

        baru = ArrayPesanan()
        for i in range(self.circular.size()):
            array_tambah(baru, self.circular.get(i))
        self.naif.data = baru
        self._naif_basi = False

    def _catat(self, tipe, data):
        self.undo_stack.push((tipe, data))
        self.redo_stack = Stack()

    def enqueue(self, item):
        if not self._naif_basi:
            self.naif.enqueue(item)
        self.circular.enqueue(item)
        self._catat("ENQUEUE", item)

    def dequeue(self, n=1):
        self.sinkron_naif()
        if n < 0:
            n = 0
        if n > self.circular.size():
            n = self.circular.size()

        t0 = time.perf_counter()
        for _ in range(n):
            self.naif.dequeue()
        ms_naif = (time.perf_counter() - t0) * 1000

        items = []
        t0 = time.perf_counter()
        for _ in range(n):
            items.append(self.circular.dequeue())
        ms_circular = (time.perf_counter() - t0) * 1000

        if len(items) > 0:
            self._catat("DEQUEUE", items)

        return items, ms_naif, ms_circular

    def undo_last(self):
        if self.undo_stack.is_empty():
            return "Tidak ada aksi yang bisa dibatalkan."

        aksi = self.undo_stack.pop()
        tipe, data = aksi

        if tipe == "ENQUEUE":
            if not self._naif_basi:
                self.naif.pop_belakang()
            self.circular.pop_belakang()
            pesan = "Pembatalan enqueue: " + str(data) + " dikeluarkan lagi dari belakang."
        else:
            for i in range(len(data) - 1, -1, -1):
                self.circular.push_depan(data[i])
            self._naif_basi = True
            pesan = "Pembatalan dequeue: " + str(len(data)) + " pesanan dikembalikan ke DEPAN antrean circular."

        self.redo_stack.push(aksi)
        return pesan

    def redo_last(self):
        if self.redo_stack.is_empty():
            return "Tumpukan redo kosong, tidak ada yang diulang."

        aksi = self.redo_stack.pop()
        tipe, data = aksi

        if tipe == "ENQUEUE":
            if not self._naif_basi:
                self.naif.enqueue(data)
            self.circular.enqueue(data)
            pesan = "Enqueue dikerjakan lagi: " + str(data) + " masuk kembali ke belakang."
        else:
            for _ in range(len(data)):
                self.circular.dequeue()
            self._naif_basi = True
            pesan = "Dequeue dikerjakan lagi: " + str(len(data)) + " pesanan keluar lagi dari antrean circular."

        self.undo_stack.push(aksi)
        return pesan

    def history(self):
        hasil = []
        for i in range(self.undo_stack.size()):
            hasil.append(array_get(self.undo_stack.items, i))
        return hasil

    def stats(self):
        self.sinkron_naif()
        return [
            ("queue_len_naif", self.naif.size()),
            ("queue_len_circular", self.circular.size()),
            ("queue_capacity", self.circular.capacity),
            ("total_geseran_naif", self.naif.total_geseran),
            ("total_geseran_circular", self.circular.total_geseran),
            ("undo_depth", self.undo_stack.size()),
            ("redo_depth", self.redo_stack.size()),
        ]


def cetak_tabel_kasir(ekspresi):
    postfix, total, langkah = proses_kasir(ekspresi)

    print("TAHAP 1 - KONVERSI INFIX KE POSTFIX")
    print("Ekspresi:", ekspresi, " -> postfix")
    print("{:<10} {:<38} {:<18} {}".format("token", "tindakan", "stack", "keluaran"))
    print("-" * 105)

    for nomor, token, tindakan, stack, keluaran in langkah:
        if nomor.startswith("1."):
            print("{:<10} {:<38} {:<18} {}".format(
                token, tindakan, stack, keluaran
            ))

    print("\nTAHAP 2 - EVALUASI POSTFIX")
    print("Postfix:", gabung_token(postfix))
    print("{:<20} {:<48} {}".format("token", "tindakan", "stack nilai"))
    print("-" * 105)

    for nomor, token, tindakan, stack, keluaran in langkah:
        if nomor.startswith("2."):
            print("{:<20} {:<48} {}".format(token, tindakan, stack))

    print("\nTOTAL:", format_rupiah(total))
    return postfix, total


def muat_pesanan_csv(nama_file):
    import csv
    pesanan = ArrayPesanan()
    with open(nama_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader, None)
        for baris in reader:
            if baris:
                array_tambah(pesanan, baris)
    return pesanan


def tampilkan_postfix_pesanan(pesanan):
    # Data CSV berbentuk list kolom:
    # oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status
    harga = int(pesanan[4])
    oid = pesanan[0]
    pelanggan = pesanan[1]
    resto = pesanan[2]
    menu = pesanan[3]

    # CSV hanya menyimpan total harga per menu, bukan jumlah item.
    # Jadi 1 * harga menunjukkan perhitungan harga pesanan pertama.
    ekspresi = "( 1 * " + str(harga) + " )"

    print("\n=== KASIR STACK DARI DATA CSV ===")
    print("Pesanan :", oid)
    print("Pelanggan:", pelanggan)
    print("Restoran:", resto)
    print("Menu    :", menu)
    print("Harga   :", format_rupiah(harga))
    print("Ekspresi perhitungan:", ekspresi)
    cetak_tabel_kasir(ekspresi)


if __name__ == "__main__":
    import os

    # Lokasi CSV dihitung dari folder file ini:
    # Strukdat/Backend/m2_antrean.py -> Strukdat/data/pesanan.csv
    folder_backend = os.path.dirname(os.path.abspath(__file__))
    lokasi_csv = os.path.normpath(
        os.path.join(folder_backend, "..", "data", "pesanan.csv")
    )

    print("=== 1. KASIR STACK DARI CSV ===")

    try:
        data_csv = muat_pesanan_csv(lokasi_csv)
    except FileNotFoundError:
        print("File CSV tidak ditemukan:", lokasi_csv)
        raise SystemExit(1)

    print("CSV:", lokasi_csv)
    print("Jumlah pesanan terbaca:", data_csv.size)

    # Pilih pesanan pertama yang masih ANTRE dan harga valid.
    pesanan_aktif = None
    for i in range(data_csv.size):
        baris = array_get(data_csv, i)
        if baris is None or len(baris) <= 8:
            continue
        if baris[8].strip().upper() != "ANTRE":
            continue
        try:
            int(baris[4])
            pesanan_aktif = baris
            break
        except (ValueError, IndexError):
            continue

    if pesanan_aktif is None:
        print("Tidak ditemukan pesanan berstatus ANTRE dengan harga valid.")
    else:
        tampilkan_postfix_pesanan(pesanan_aktif)

    print("\n=== 2. QUEUE + UNDO/REDO ===")
    m = ManajerUndoRedo()
    for i in range(data_csv.size):
        baris = array_get(data_csv, i)
        if baris is not None and len(baris) > 0:
            m.enqueue(baris[0])

    print("Data antrean dimuat dari CSV:", data_csv.size, "pesanan")
    keluar, waktu_naif, waktu_circular = m.dequeue(2)
    print("Pesanan yang di-dequeue:", keluar)
    print("Waktu antrean naif:", round(waktu_naif, 4), "ms")
    print("Waktu antrean melingkar:", round(waktu_circular, 4), "ms")
    print(m.undo_last())
    print(m.redo_last())
    print("Statistik:", m.stats())
