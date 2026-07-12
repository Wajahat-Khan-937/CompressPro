"""
backend/huffman.py
------------------------------------------------------------
Core Huffman Coding algorithm — byte & string compatible.
------------------------------------------------------------
"""

import heapq
from collections import Counter


class HuffmanNode:
    """A node in the Huffman tree."""
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        if self.freq != other.freq:
            return self.freq < other.freq
        def sort_key(node):
            if node.char is None:
                return (0, 0)
            elif isinstance(node.char, int):
                return (1, node.char)
            else:
                return (2, str(node.char))
        return sort_key(self) < sort_key(other)
    
    def is_leaf(self):
        return self.left is None and self.right is None


def build_frequency_table(data):
    """Build frequency table from any iterable (str, bytes, list)."""
    return dict(Counter(data))


def build_huffman_tree(freq_table):
    """Build Huffman tree from frequency table."""
    if not freq_table:
        return None
    
    heap = []
    for char, freq in freq_table.items():
        heapq.heappush(heap, HuffmanNode(char=char, freq=freq))
    
    if len(heap) == 1:
        node = heapq.heappop(heap)
        return HuffmanNode(freq=node.freq, left=node)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heapq.heappop(heap)


def _generate_codes_helper(node, current_code, code_dict):
    if node is None:
        return
    if node.is_leaf():
        code = current_code if current_code else "0"
        code_dict[node.char] = code
        return
    _generate_codes_helper(node.left, current_code + "0", code_dict)
    _generate_codes_helper(node.right, current_code + "1", code_dict)


def generate_codes(tree):
    """Generate Huffman codes from tree."""
    if tree is None:
        return {}
    code_dict = {}
    _generate_codes_helper(tree, "", code_dict)
    return code_dict


def encode(data, codes):
    """Encode data (str or bytes) using Huffman codes."""
    return "".join(codes[char] for char in data)


def decode(bit_string, tree):
    """Decode bit string back to original type using Huffman tree."""
    if tree is None:
        return b"" if tree is None else ""
    
    if tree.is_leaf() and tree.left is None:
        result = [tree.char] * len(bit_string)
        return _join_result(result)
    
    result = []
    current = tree
    
    for bit in bit_string:
        current = current.left if bit == "0" else current.right
        if current.is_leaf():
            result.append(current.char)
            current = tree
    
    return _join_result(result)


def _join_result(result):
    """Join result list into str or bytes depending on element type."""
    if not result:
        return ""
    if isinstance(result[0], int):
        return bytes(result)
    return "".join(result)