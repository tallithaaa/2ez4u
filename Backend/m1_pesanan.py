import csv

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
class ArrayPesanan:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.size = 0
        self.data = [None] * self.capacity

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def lihat(self, index):
        if index < 0 or index >= self.size:
            return None
        return self.data[index]

    def tambah_reguler(self, pesanan):
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = pesanan
        self.size += 1

    def tambah_prioritas(self, pesanan):
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        
        mid = self.size // 2

        for i in range(self.size, mid, -1):
            self.data[i] = self.data[i - 1]
            
        self.data[mid] = pesanan
        self.size += 1

    def tambah_vip(self, pesanan):
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
            
        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i - 1]
            
        self.data[0] = pesanan
        self.size += 1

    def hapus(self, index):
        if index < 0 or index >= self.size:
            return None
        
        removed = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
            
        self.data[self.size - 1] = None
        self.size -= 1
        return removed


class LinkedListPesanan:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def lihat(self, index):
        if index < 0 or index >= self.size:
            return None
        
        curr = self.head
        for _ in range(index):
            curr = curr.next
        return curr.data

    def tambah_reguler(self, pesanan):
        new_node = Node(pesanan)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def tambah_prioritas(self, pesanan):
        if self.size == 0 or self.size == 1:
            self.tambah_vip(pesanan)
            return

        new_node = Node(pesanan)
        mid = self.size // 2
        
        curr = self.head
        for _ in range(mid - 1):
            curr = curr.next
            
        new_node.next = curr.next
        curr.next = new_node
        self.size += 1

    def tambah_vip(self, pesanan):
        new_node = Node(pesanan)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def hapus(self, index):
        if index < 0 or index >= self.size or self.head is None:
            return None

        if index == 0:
            removed_data = self.head.data
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.size -= 1
            return removed_data

        curr = self.head
        for _ in range(index - 1):
            curr = curr.next

        removed_data = curr.next.data
        curr.next = curr.next.next

        if index == self.size - 1:
            self.tail = curr

        self.size -= 1
        return removed_data

def cek_data(nama_file, array, linked):
    with open(nama_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        next(reader)

        for baris in reader:
            array.tambah_reguler(baris)
            linked.tambah_reguler(baris)

if __name__ == "__main__":

    array = ArrayPesanan()
    linked= LinkedListPesanan()

    cek_data(
        "data/pesanan.csv",
        array, linked
    )

    print("\n===DATA PERTAMA===")

    i = 0
    while i<5 and i < array.size:
        print(array.lihat(i))
        i += 1