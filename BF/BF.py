from bitarray import bitarray
import hashlib
from bisect import bisect_left, bisect_right

class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, item):
        print(f"Adding {item} to BloomFilter")
        for i in range(self.hash_count):
            index = self._hash(item, i) % self.size
            self.bit_array[index] = True
            print(f"  Hash {i}: index {index}")

    def query(self, item):
        print(f"Querying {item} in BloomFilter")
        for i in range(self.hash_count):
            index = self._hash(item, i) % self.size
            if not self.bit_array[index]:
                print(f"  Hash {i}: index {index} is 0")
                return False
        return True

    def _hash(self, item, seed):
        """ Generate a hash for the given item. """
        hash_value = hash((item, seed))
        return hash_value


class BTreeNode:
    def __init__(self, t):
        self.t = t  # Minimum degree (defines the range for number of keys)
        self.keys = []
        self.children = []
        self.leaf = True  # True if leaf node, false otherwise
        self.bloom_filter = BloomFilter(1000, 3)  # Adjust size and hash counts as needed

    def insert_non_full(self, key):
        i = len(self.keys) - 1
        if self.leaf:
            while i >= 0 and self.keys[i] > key:
                i -= 1
            self.keys.insert(i + 1, key)
            self.bloom_filter.add(key)
        else:
            while i >= 0 and self.keys[i] > key:
                i -= 1
            i += 1
            if len(self.children[i].keys) == 2 * self.t - 1:
                self.split_child(i)
                if key > self.keys[i]:
                    i += 1
            self.children[i].insert_non_full(key)

    def split_child(self, i):
        y = self.children[i]
        z = BTreeNode(y.t)
        z.leaf = y.leaf
        mid_index = self.t - 1  # 正确计算中间索引，因为数组索引是从0开始的

        # 确保分裂时考虑到叶子和非叶子节点的差异
        if y.leaf:
            z.keys = y.keys[mid_index + 1:]  # 新节点获取右半部分的键
            y.keys = y.keys[:mid_index + 1]  # 旧节点保留左半部分的键和中间键
        else:
            z.keys = y.keys[mid_index + 1:]  # 新节点获取右半部分的键
            z.children = y.children[mid_index + 1:]  # 新节点获取对应的子节点
            y.keys = y.keys[:mid_index]  # 旧节点保留左半部分的键
            y.children = y.children[:mid_index + 1]  # 旧节点保留对应的子节点

        # 将中间键提升到父节点
        self.keys.insert(i, y.keys.pop(mid_index))
        self.children.insert(i + 1, z)


class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t)
        self.t = t

    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            s = BTreeNode(self.t)
            s.children.append(self.root)
            s.leaf = False
            s.split_child(0)
            self.root = s
        self.root.insert_non_full(key)

    def search(self, key, node=None):
        if node is None:
            node = self.root
        if node.bloom_filter.query(key):
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            if i < len(node.keys) and key == node.keys[i]:
                return True
            elif node.leaf:
                return False
            else:
                return self.search(key, node.children[i])
        else:
            return False

if __name__ == "__main__":
    btree = BTree(3)  # Minimum degree t=3
    keys_to_insert = [10, 20, 5, 6, 12, 30, 7, 17]

    for key in keys_to_insert:
        print(f"Inserting {key}...")
        btree.insert(key)

    # 搜索存在的键
    print("Search 6:", btree.search(6))  # 预期输出：True

    # 搜索不存在的键
    print("Search 15:", btree.search(15))  # 预期输出：False
