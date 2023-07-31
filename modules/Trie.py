class Trie:
    def __init__(self):
        self.root = TrieNode()
        
    #insert a word into the trie
    def insert(self, word, callback = None):
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.callback = callback

    #search for a word in the trie
    def search(self, word):
        current = self.root
        callback = None
        for char in word:
            if char not in current.children:
                return callback
            current = current.children[char]
            if current.callback != None:
                callback = current.callback
        return callback

    def __str__(self):
        return self.root.__str__()
    
#TrieNode class
class TrieNode:
    def __init__(self):
        self.children = {}
        self.callback = None
    def __str__(self):
        current = self
        string = ''
        for char in current.children:
            string += char+ '->'+ current.children[char].__str__()
        return string