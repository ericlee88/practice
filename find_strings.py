#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'findStrings' function below.
#
# The function is expected to return a STRING_ARRAY.
# The function accepts following parameters:
#  1. STRING_ARRAY w
#  2. INTEGER_ARRAY queries
#

class TrieNode:
    def __init__(self, prefix: str = None, level: int = 0):
        self.children = None
        self.withoutHead = None
        self.prefix = prefix
        self.level = level
        self.strCount = None

    def __getitem__(self, c: str):
        if self.children is None:
            return None
        return self.children[ord(c) - ord('a')]

    def __setitem__(self, c: str, node: 'TrieNode'):
        if self.children is None:
            self.makeInitInterior()
        self.children[ord(c) - ord('a')] = node

    def size(self):
        if self.strCount is not None:
            return self.strCount
        elif self.children is None:
            return len(self.prefix) - self.level + 1
        self.strCount = len(self.prefix) - self.level + 1 + sum(child.size() for child in self.children if child is not None)
        return self.strCount
    
    def makeInitInterior(self):
        self.children = [None] * 26

    def setChild(self, child: 'TrieNode'):
        if self.children is None:
            self.makeInitInterior()
        assert len(self.prefix) + 1 == child.level, f"{self.prefix} + 1 != {child.level}"
        self[child.prefix[child.level - 1]] = child
        if child.withoutHead is None and  self.withoutHead is not None:
            child.withoutHead = transverseIgnoringHead(self.withoutHead, child)
        elif child.withoutHead is None and self.level == 0:
            child.withoutHead = self

    def addChild(self, childPrefix: str) -> 'TrieNode':
        # Assert self.prefix is a prefix of childPrefix
        assert childPrefix.startswith(self.prefix), f"{self.prefix} is not a prefix of {childPrefix}"
        newChild = TrieNode(childPrefix, len(self.prefix) + 1)
        self.setChild(newChild)
        return newChild
    
    def setWithoutHead(self, node: 'TrieNode', nodeParent: 'TrieNode'):
        if node.level >= self.level and nodeParent is not None:
            node = nodeParent
        if self.withoutHead is None or self.withoutHead.level < node.level and node.level < self.level:
            self.withoutHead = node

    def __repr__(self):
        return f"TrieNode({self.prefix}, {self.level})"
    
    def print(self):
        indent = "  " * self.level
        print("{}{} [size = {}])".format(indent, self, self.size()))
        if self.withoutHead is not None:
            print("{}>>> withoutHead -> {}".format(indent, self.withoutHead))
        if self.children is None:
            return
        for i, child in enumerate(self.children, ord('a')):
            if child is None:
                continue
            print("{}>> '{}' -> child({} [size={}])".format(indent, chr(i), str(child), child.size()))
        for child in self.children:
            if child is None:
                continue
            child.print()

def findSplit(src: str, substr: str) -> int:
    if len(src) == 0:
        return 0
    for i, (a, b) in enumerate(zip(src, substr)):
        if a != b:
            return i
    return min(len(src), len(substr))
    
def transverseIgnoringHead(node: TrieNode, toFollow: TrieNode) -> TrieNode:
    if node.children is None or len(toFollow.prefix) <= 1:
        return node
    prefixToFollow = toFollow.prefix[1:]
    if node.level >= toFollow.level - 1:
        return node
    elif len(node.prefix) >= len(prefixToFollow):
        return node
    child = node[prefixToFollow[len(node.prefix)]]
    if child is None or child.level >= toFollow.level:
        return node
    assert prefixToFollow.startswith(child.prefix[:child.level]), f"{prefixToFollow} does not start with {child.prefix}"
    return transverseIgnoringHead(child, toFollow)

def addSubstrings(node: TrieNode, substr: str, toTrack: TrieNode) -> TrieNode:
    if node.prefix is None:
        node.prefix = ''
        node.makeInitInterior()
    assert node.prefix[:node.level] == substr[:node.level], f"{node.prefix[:node.level]} != {substr[:node.level]}"
    split = node.level + findSplit(node.prefix[node.level:], substr[node.level:])
    if split == len(substr):
        # `node` already captures entirety of `substr`
        if toTrack is not None:
            toTrack.setWithoutHead(node, None)
        return node
    elif split < len(node.prefix):
        leftOverNode = TrieNode(node.prefix, split + 1)
        leftOverNode.children = node.children
        # change to new interior split
        node.prefix = node.prefix[:split]
        node.makeInitInterior()
        newChild = node.addChild(substr)  # new node
        if toTrack is not None:
            toTrack.setWithoutHead(newChild, node)
        node.setChild(leftOverNode)
        return newChild
    else:  # split == len(node.prefix):
        # `substr` is an extension of node's prefix
        if node.children is None:
            node.prefix = substr
            if toTrack is not None:
                toTrack.setWithoutHead(node, None)
            return node
        oldChild = node[substr[split]]
        if oldChild is None:
            newChild = node.addChild(substr)
            if toTrack is not None:
                toTrack.setWithoutHead(newChild, node)
            return newChild
        else:
            return addSubstrings(oldChild, substr, toTrack)
        
def processString(root: TrieNode, string: str):
    prevNode = None
    for numIgnored in range(len(string)):
        toSearch = prevNode.withoutHead if prevNode is not None and prevNode.withoutHead is not None else root
        # toSearch = root
        newNode = addSubstrings(toSearch, string[numIgnored:], prevNode)
        prevNode = newNode
    
def queryTree(node: TrieNode, query: int) -> str:
    if query < len(node.prefix) - node.level + 1:
        return node.prefix[:(query + node.level)]
    elif node.children is None:
        return "INVALID"
    query -= len(node.prefix) - node.level + 1
    for child in node.children:
        if child is None:
            continue
        if child.size() > query:
            return queryTree(child, query)
        query -= child.size()
    return "INVALID"

def findStrings(w, queries):
    # Write your code here
    root = TrieNode()
    for word in w:
        processString(root, word)

    for query in queries:
        yield queryTree(root, query)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    w_count = int(input().strip())

    w = []

    for _ in range(w_count):
        w_item = input()
        w.append(w_item)

    queries_count = int(input().strip())

    queries = []

    for _ in range(queries_count):
        queries_item = int(input().strip())
        queries.append(queries_item)

    result = findStrings(w, queries)

    fptr.write('\n'.join(result))
    fptr.write('\n')

    fptr.close()
