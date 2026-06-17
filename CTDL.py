# Hash Node

class HashNode:

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


# Hash Map

class HashMap:

    # ---------- Public ----------

    def __init__(self):
        self.__TABLE_SIZE = 128
        self.__buckets = [None] * self.__TABLE_SIZE

    def insert(self, key, value):

        index = self.__hash_function(key)

        current = self.__buckets[index]

        while current is not None:

            if current.key == key:
                current.value = value
                return

            current = current.next

        new_node = HashNode(key, value)

        new_node.next = self.__buckets[index]
        self.__buckets[index] = new_node

    def get(self, key):

        index = self.__hash_function(key)

        current = self.__buckets[index]

        while current is not None:

            if current.key == key:
                return current.value

            current = current.next

        return None

    def contains_key(self, key):
        return self.get(key) is not None

    def remove_key(self, key):

        index = self.__hash_function(key)

        current = self.__buckets[index]
        previous = None

        while current is not None:

            if current.key == key:

                if previous is None:
                    self.__buckets[index] = current.next
                else:
                    previous.next = current.next

                return

            previous = current
            current = current.next

    def clear(self):

        for i in range(self.__TABLE_SIZE):
            self.__buckets[i] = None

    def keys(self):

        result = []

        for bucket in self.__buckets:
            node = bucket
            while node is not None:
                result.append(node.key)
                node = node.next

        return result

    def values(self):

        result = []

        for bucket in self.__buckets:
            node = bucket
            while node is not None:
                result.append(node.value)
                node = node.next

        return result

    def items(self):

        result = []

        for bucket in self.__buckets:
            node = bucket
            while node is not None:
                result.append((node.key, node.value))
                node = node.next

        return result

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key):
        return self.contains_key(key)

    def __delitem__(self, key):
        self.remove_key(key)

    # ---------- Private ----------

    def __hash_function(self, key):

        hash_value = 0

        for ch in key:
            hash_value = (
                hash_value * 31 + ord(ch)
            ) % self.__TABLE_SIZE

        return hash_value