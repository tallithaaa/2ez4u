import csv
import time

try:
    from .m1_pesanan import ArrayPesanan, LinkedListPesanan
except ImportError:
    try:
        from m1_pesanan import ArrayPesanan, LinkedListPesanan
    except ImportError:
        ArrayPesanan = None
        LinkedListPesanan = None

INDEKS_KOLOM = (
    ("oid", 0),
    ("pelanggan", 1),
    ("resto", 2),
    ("menu", 3),
    ("harga", 4),
    ("prioritas", 5),
    ("t_masuk", 6),
    ("t_selesai", 7),
    ("status", 8),
)


def nilai_kunci(pesanan, kunci):
    """Mengambil nilai kunci dari baris CSV berbentuk list/tuple atau objek berisi data."""
    if kunci not in ("oid", "harga", "selesai", "t_selesai", "t_masuk",
                     "pelanggan", "resto", "menu", "prioritas", "status"):
        raise ValueError("Kunci tidak dikenal: " + str(kunci))

    nama_kolom = kunci
    if kunci == "selesai":
        nama_kolom = "t_selesai"

    data = pesanan
    if hasattr(pesanan, "data") and not isinstance(pesanan, (list, tuple)):
        data = pesanan.data

    indeks = -1
    for nama, nomor in INDEKS_KOLOM:
        if nama == nama_kolom:
            indeks = nomor
            break

    if indeks < 0 or indeks >= len(data):
        raise ValueError("Kolom " + nama_kolom + " tidak tersedia pada baris pesanan.")
    nilai = data[indeks]

    if nilai is None:
        return ""

    teks = str(nilai).strip()
    if nama_kolom in ("harga", "prioritas", "t_masuk", "t_selesai"):
        if teks == "":
            if nama_kolom == "t_selesai":
                return 2 ** 63
            return -1
        try:
            return int(float(teks))
        except ValueError:
            return -1
    return teks


def salin_data(data):
    """Salin data dari list biasa, ArrayPesanan, atau LinkedListPesanan ke list kerja."""
    hasil = []

    if data is None:
        return hasil

    if isinstance(data, list):
        for item in data:
            hasil.append(item)
        return hasil

    if hasattr(data, "capacity") and hasattr(data, "size") and hasattr(data, "data"):
        for i in range(data.size):
            hasil.append(data.lihat(i) if hasattr(data, "lihat") else data.data[i])
        return hasil

    if hasattr(data, "head") and hasattr(data, "size"):
        curr = data.head
        while curr is not None:
            hasil.append(curr.data)
            curr = curr.next
        return hasil

    if hasattr(data, "size") and callable(data.size) and hasattr(data, "get"):
        for i in range(data.size()):
            hasil.append(data.get(i))
        return hasil

    raise TypeError("Data harus berupa list, ArrayPesanan, LinkedListPesanan, atau antrean M2.")


def insertion_sort(larik, kunci="selesai", batas=20000):
    """
    Insertion sort stabil dan in-place.
    Mengembalikan (larik, jumlah_perbandingan, jumlah_pergeseran, waktu_ms).
    """
    if len(larik) > batas:
        raise ValueError(
            "Insertion sort ditolak untuk " + str(len(larik)) +
            " baris. Batasnya " + str(batas) + "; gunakan merge sort."
        )

    perbandingan = 0
    pergeseran = 0
    mulai = time.perf_counter()

    for i in range(1, len(larik)):
        item = larik[i]
        nilai_item = nilai_kunci(item, kunci)
        j = i - 1

        while j >= 0:
            perbandingan += 1
            if nilai_kunci(larik[j], kunci) > nilai_item:
                larik[j + 1] = larik[j]
                pergeseran += 1
                j -= 1
            else:
                break

        larik[j + 1] = item
        pergeseran += 1

    waktu_ms = (time.perf_counter() - mulai) * 1000
    return larik, perbandingan, pergeseran, waktu_ms


def merge_sort(larik, kunci="selesai"):
    """
    Merge sort stabil.
    Mengembalikan (larik_terurut, jumlah_perbandingan, jumlah_pemindahan, waktu_ms).
    Data input tidak diubah; hasil dikembalikan sebagai list baru.
    """
    kerja = salin_data(larik)
    perbandingan = [0]
    pemindahan = [0]
    mulai = time.perf_counter()

    def urutkan(lo, hi):
        if hi - lo <= 1:
            return kerja[lo:hi]

        mid = (lo + hi) // 2
        kiri = urutkan(lo, mid)
        kanan = urutkan(mid, hi)
        gabungan = []
        i = 0
        j = 0

        while i < len(kiri) and j < len(kanan):
            perbandingan[0] += 1
            # <= menjaga stabilitas: jika kunci sama, item dari bagian kiri dulu.
            if nilai_kunci(kiri[i], kunci) <= nilai_kunci(kanan[j], kunci):
                gabungan.append(kiri[i])
                i += 1
            else:
                gabungan.append(kanan[j])
                j += 1
            pemindahan[0] += 1

        while i < len(kiri):
            gabungan.append(kiri[i])
            i += 1
            pemindahan[0] += 1

        while j < len(kanan):
            gabungan.append(kanan[j])
            j += 1
            pemindahan[0] += 1

        return gabungan

    hasil = urutkan(0, len(kerja))
    waktu_ms = (time.perf_counter() - mulai) * 1000
    return hasil, perbandingan[0], pemindahan[0], waktu_ms


def linear_search(larik, target, kunci="oid"):
    """
    Mencari dari awal sampai ketemu.
    Mengembalikan (indeks, jumlah_perbandingan, waktu_ms); indeks -1 jika tidak ada.
    """
    mulai = time.perf_counter()
    perbandingan = 0
    target_teks = str(target).strip()

    for i in range(len(larik)):
        perbandingan += 1
        nilai = nilai_kunci(larik[i], kunci)
        if str(nilai) == target_teks:
            waktu_ms = (time.perf_counter() - mulai) * 1000
            return i, perbandingan, waktu_ms

    waktu_ms = (time.perf_counter() - mulai) * 1000
    return -1, perbandingan, waktu_ms


def binary_search(larik_terurut, target, kunci="oid"):
    """
    Binary search hanya benar jika larik sudah terurut menurut kunci yang sama.
    Mengembalikan (indeks, jumlah_perbandingan, waktu_ms); indeks -1 jika tidak ada.
    """
    mulai = time.perf_counter()
    lo = 0
    hi = len(larik_terurut) - 1
    perbandingan = 0
    target_teks = str(target).strip()

    while lo <= hi:
        mid = (lo + hi) // 2
        nilai = nilai_kunci(larik_terurut[mid], kunci)
        perbandingan += 1

        if str(nilai) == target_teks:
            waktu_ms = (time.perf_counter() - mulai) * 1000
            return mid, perbandingan, waktu_ms

        if isinstance(nilai, int):
            try:
                target_banding = int(float(target_teks))
            except ValueError:
                target_banding = target_teks
        else:
            target_banding = target_teks

        if nilai < target_banding:
            lo = mid + 1
        else:
            hi = mid - 1

    waktu_ms = (time.perf_counter() - mulai) * 1000
    return -1, perbandingan, waktu_ms


def muat_csv(nama_file):
    """Muat CSV menjadi list baris, tanpa header, sesuai format M1."""
    hasil = []
    with open(nama_file, "r", encoding="utf-8-sig", newline="") as file:
        pembaca = csv.reader(file)
        header = next(pembaca, None)
        if header is None:
            return hasil

        for baris in pembaca:
            if len(baris) > 0:
                hasil.append(baris)
    return hasil


class LaporanPesanan:
    """Pembungkus fitur M3 agar mudah dipanggil dari app.py/ui.py nantinya."""

    def __init__(self, sumber):
        self.data_asli = sumber
        self.data = salin_data(sumber)
        self.terakhir = []
        self.hasil_terakhir = None

    def insertion(self, kunci="selesai", jumlah=None, batas=20000):
        data_kerja = []
        n = len(self.data)
        if jumlah is None or jumlah > n:
            jumlah = n
        if jumlah < 0:
            jumlah = 0

        for i in range(jumlah):
            data_kerja.append(self.data[i])

        hasil, banding, geser, ms = insertion_sort(data_kerja, kunci, batas)
        self.terakhir = hasil
        self.hasil_terakhir = ("insertion_sort", kunci, banding, geser, ms)
        return hasil, banding, geser, ms

    def merge(self, kunci="selesai", jumlah=None):
        data_kerja = []
        n = len(self.data)
        if jumlah is None or jumlah > n:
            jumlah = n
        if jumlah < 0:
            jumlah = 0

        for i in range(jumlah):
            data_kerja.append(self.data[i])

        hasil, banding, pindah, ms = merge_sort(data_kerja, kunci)
        self.terakhir = hasil
        self.hasil_terakhir = ("merge_sort", kunci, banding, pindah, ms)
        return hasil, banding, pindah, ms

    def linear(self, target, kunci="oid"):
        indeks, banding, ms = linear_search(self.data, target, kunci)
        pesanan = None
        if indeks >= 0:
            pesanan = self.data[indeks]
        self.hasil_terakhir = ("linear_search", kunci, banding, ms)
        return pesanan, indeks, banding, ms

    def binary(self, target, kunci="oid"):
        data_urut, banding_sort, pindah, ms_sort = merge_sort(self.data, kunci)
        indeks, banding, ms = binary_search(data_urut, target, kunci)
        pesanan = None
        if indeks >= 0:
            pesanan = data_urut[indeks]
        self.terakhir = data_urut
        self.hasil_terakhir = (
            "binary_search", kunci, banding_sort, pindah, ms_sort, banding, ms
        )
        return pesanan, indeks, banding_sort, banding, ms_sort, ms

    def stats(self):
        if self.hasil_terakhir is None:
            return "Belum ada operasi M3 yang dijalankan."

        info = self.hasil_terakhir
        if info[0] in ("insertion_sort", "merge_sort"):
            return (
                "Operasi: " + info[0] +
                "\nKunci: " + str(info[1]) +
                "\nPerbandingan: " + str(info[2]) +
                "\nPemindahan: " + str(info[3]) +
                "\nWaktu: " + format_ms(info[4])
            )

        if info[0] == "linear_search":
            return (
                "Operasi: linear_search" +
                "\nKunci: " + str(info[1]) +
                "\nPerbandingan: " + str(info[2]) +
                "\nWaktu: " + format_ms(info[3])
            )

        return (
            "Operasi: binary_search" +
            "\nKunci: " + str(info[1]) +
            "\nPerbandingan saat menyiapkan urutan: " + str(info[2]) +
            "\nPemindahan saat merge sort: " + str(info[3]) +
            "\nWaktu menyiapkan urutan: " + format_ms(info[4]) +
            "\nPerbandingan binary search: " + str(info[5]) +
            "\nWaktu binary search: " + format_ms(info[6])
        )


def format_ms(ms):
    return str(round(ms, 3)) + " ms"


def tampilkan_ringkas(judul, hasil, kunci, batas=10):
    print("\n" + judul)
    print("Jumlah data:", len(hasil))
    print("Urutan berdasarkan:", kunci)
    print("Contoh hasil:")
    print("oid          | pelanggan                 | harga  | t_selesai | status")
    print("-" * 78)
    jumlah = len(hasil)
    if jumlah > batas:
        jumlah = batas
    for i in range(jumlah):
        baris = hasil[i]
        oid = baris[0] if len(baris) > 0 else ""
        pelanggan = baris[1] if len(baris) > 1 else ""
        harga = baris[4] if len(baris) > 4 else ""
        selesai = baris[7] if len(baris) > 7 else ""
        status = baris[8] if len(baris) > 8 else ""
        print(str(oid) + " | " + str(pelanggan)[:25].ljust(25) + " | " +
              str(harga).rjust(6) + " | " + str(selesai).rjust(9) + " | " + str(status))


def main():
    import os

    folder_backend = os.path.dirname(os.path.abspath(__file__))
    lokasi_csv = os.path.normpath(
        os.path.join(folder_backend, "..", "data", "pesanan.csv")
    )

    if not os.path.exists(lokasi_csv):
        lokasi_alternatif = os.path.join(folder_backend, "data", "pesanan.csv")
        if os.path.exists(lokasi_alternatif):
            lokasi_csv = lokasi_alternatif

    print("=== M3: SORTING DAN SEARCHING DARI CSV ===")
    print("File CSV:", lokasi_csv)

    try:
        data = muat_csv(lokasi_csv)
    except FileNotFoundError:
        print("File CSV tidak ditemukan:", lokasi_csv)
        raise SystemExit(1)

    if len(data) == 0:
        print("CSV tidak memiliki data pesanan.")
        return

    print("Jumlah pesanan terbaca:", len(data))
    laporan = LaporanPesanan(data)

    # 1. Insertion sort: gunakan 10 data pertama agar tidak berat untuk CSV besar.
    jumlah_uji = len(data)
    if jumlah_uji > 10:
        jumlah_uji = 10

    try:
        hasil, banding, geser, ms = laporan.insertion(
            kunci="harga", jumlah=jumlah_uji, batas=20000
        )
        tampilkan_ringkas("=== 1. INSERTION SORT (10 DATA PERTAMA, KUNCI HARGA) ===",
                          hasil, "harga")
        print("Perbandingan:", banding)
        print("Pemindahan:", geser)
        print("Waktu:", format_ms(ms))
    except ValueError as error:
        print("Insertion sort:", error)

    hasil_merge, banding_merge, pindah_merge, ms_merge = laporan.merge(
        kunci="selesai"
    )
    tampilkan_ringkas("=== 2. MERGE SORT (SELURUH DATA, KUNCI WAKTU SELESAI) ===",
                      hasil_merge, "selesai")
    print("Perbandingan:", banding_merge)
    print("Pemindahan:", pindah_merge)
    print("Waktu:", format_ms(ms_merge))

    target = data[0][0]
    pesanan, indeks, banding_linear, ms_linear = laporan.linear(target, "oid")
    print("\n=== 3. LINEAR SEARCH ===")
    print("Target:", target)
    print("Indeks ditemukan:", indeks)
    print("Perbandingan:", banding_linear)
    print("Waktu:", format_ms(ms_linear))
    print("Pesanan:", pesanan)

    pesanan, indeks, banding_sort, banding_binary, ms_sort, ms_binary = laporan.binary(
        target, "oid"
    )
    print("\n=== 4. BINARY SEARCH ===")
    print("Target:", target)
    print("Indeks pada data terurut:", indeks)
    print("Perbandingan saat merge sort:", banding_sort)
    print("Perbandingan binary search:", banding_binary)
    print("Waktu mengurutkan:", format_ms(ms_sort))
    print("Waktu binary search:", format_ms(ms_binary))
    print("Pesanan:", pesanan)

    print("\n=== RINGKASAN M3 ===")
    print("Insertion sort :", banding, "perbandingan untuk", jumlah_uji, "data")
    print("Merge sort     :", banding_merge, "perbandingan untuk", len(data), "data")
    print("Linear search  :", banding_linear, "perbandingan")
    print("Binary search  :", banding_binary, "perbandingan (setelah data diurutkan)")


if __name__ == "__main__":
    main()
