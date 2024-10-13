class BPlusTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []

    def is_full(self):
        return len(self.keys) == 2 * self.t - 1

class BPlusTree:
    def __init__(self, t):
        self.t = t
        self.root = BPlusTreeNode(t, leaf=True)

    def insert(self, key):
        root = self.root
        if root.is_full():
            new_root = BPlusTreeNode(self.t)
            new_root.children.append(self.root)
            new_root.leaf = False
            self.split_child(new_root, 0)
            self.root = new_root
        self.insert_non_full(self.root, key)

    def insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            while i >= 0 and node.keys[i] > key:
                i -= 1
            node.keys.insert(i + 1, key)
        else:
            while i >= 0 and node.keys[i] > key:
                i -= 1
            i += 1
            if node.children[i].is_full():
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], key)

    def split_child(self, parent, i):
        t = self.t
        y = parent.children[i]
        z = BPlusTreeNode(t, y.leaf)
        mid = t
        parent.keys.insert(i, y.keys[mid-1])
        z.keys = y.keys[mid:]
        y.keys = y.keys[:mid-1]

        if not y.leaf:
            z.children = y.children[mid:]
            y.children = y.children[:mid]

        parent.children.insert(i + 1, z)

    def delete(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if node.leaf:
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
                return True
            return False
        else:
            if i < len(node.keys) and node.keys[i] == key:
                i += 1
            found = self.delete(key, node.children[i])
            if not found:
                return False
            if len(node.children[i].keys) < self.t - 1:
                self.rebalance(node, i)
            return True

    def rebalance(self, parent, i):
        child = parent.children[i]
        if i > 0 and len(parent.children[i-1].keys) >= self.t:
            left_sibling = parent.children[i-1]
            child.keys.insert(0, parent.keys[i-1])
            parent.keys[i-1] = left_sibling.keys.pop()
            if not child.leaf:
                child.children.insert(0, left_sibling.children.pop())
        elif i < len(parent.children) - 1 and len(parent.children[i+1].keys) >= self.t:
            right_sibling = parent.children[i+1]
            child.keys.append(parent.keys[i])
            parent.keys[i] = right_sibling.keys.pop(0)
            if not child.leaf:
                child.children.append(right_sibling.children.pop(0))
        else:
            if i > 0:
                self.merge(parent, i-1)
            else:
                self.merge(parent, i)

    def merge(self, parent, i):
        left = parent.children[i]
        right = parent.children[i + 1]
        left.keys.append(parent.keys[i])
        left.keys.extend(right.keys)
        if not left.leaf:
            left.children.extend(right.children)
        parent.keys.pop(i)
        parent.children.pop(i + 1)
        if parent == self.root and len(parent.keys) == 0:
            self.root = left

    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        elif node.leaf:
            return False
        else:
            return self.search(key, node.children[i])

# Testing the B+ tree
def test_b_plus_tree():
    # Create a B+ tree instance with a minimum degree of 2
    bpt = BPlusTree(2)

    # Insert some values into the B+ tree
    values_to_insert = [10, 20, 5, 6, 12, 30, 7, 17]
    for value in values_to_insert:
        bpt.insert(value)

    # Perform deletion operations
    values_to_delete = [6, 20, 5]
    for value in values_to_delete:
        bpt.delete(value)

    # Check if the remaining inserted values are still in the tree
    search_results = {}
    remaining_values = [value for value in values_to_insert if value not in values_to_delete]
    for value in remaining_values:
        search_results[value] = bpt.search(value)

    # Check if the deleted or never-inserted values are mistakenly found in the tree
    for value in values_to_delete + [4, 22, 100]:
        search_results[value] = bpt.search(value)

    # Print search results
    for key, found in search_results.items():
        print(f"Value {key} {'found' if found else 'not found'} in the B+ tree.")

test_b_plus_tree()
