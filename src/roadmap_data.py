"""DSA roadmap taken from the supplied 'Data Structures & Algorithms' PDF.

Each entry: (section_id, group_name, [topic titles]). An empty group name means
the topics sit directly under the section.
"""

SECTIONS = [
    (1, "Programming Fundamentals", "Pick a language and learn the basics"),
    (2, "Basic Data Structures", "The building blocks of every program"),
    (3, "Algorithmic Complexity", "Measure how code scales"),
    (4, "Sorting Algorithms", "Ordering data efficiently"),
    (5, "Search Algorithms", "Finding data quickly"),
    (6, "Graph Data Structures", "Nodes, edges and paths"),
    (7, "Tree Data Structures", "Hierarchical data"),
    (8, "Advanced Data Structures", "Specialised structures for hard problems"),
    (9, "Complex Data Structures", "Database-style and balanced structures"),
    (10, "Problem-Solving Techniques", "Patterns for solving problems"),
    (11, "Platforms to Practice", "Where to practise coding problems"),
]

_BFS_DFS = ["Breadth First Search (BFS)", "Depth First Search (DFS)"]

TOPIC_GROUPS = [
    (1, "Pick a Language",
     ["C#", "C++", "Python", "Rust", "JavaScript", "Java", "Go", "Ruby"]),
    (1, "", ["Language Syntax", "Control Structures", "Pseudo Code", "Functions", "OOP Basics"]),

    (2, "", ["What are Data Structures?", "Why are Data Structures Important?",
             "Arrays", "Linked Lists", "Queues", "Stacks", "Hash Tables"]),

    (3, "", ["Time vs Space Complexity", "How to Calculate Complexity?"]),
    (3, "Asymptotic Notation",
     ["Big-O Notation", "Big-Theta (Big-θ) Notation", "Big-Omega (Big-Ω) Notation"]),
    (3, "Common Runtimes",
     ["Constant", "Logarithmic", "Linear", "Polynomial", "Exponential", "Factorial"]),

    (4, "", ["Bubble Sort", "Selection Sort", "Insertion Sort",
             "Merge Sort", "Quick Sort", "Heap Sort"]),

    (5, "", ["Binary Search", "Linear Search"]),

    (6, "", ["Directed Graph", "Undirected Graph"]),
    (6, "Search Algorithms", _BFS_DFS),
    (6, "Shortest Path Algorithms",
     ["Dijkstra's Algorithm", "Bellman-Ford Algorithm", "A* Algorithm"]),
    (6, "Minimum Spanning Tree", ["Prim's Algorithm", "Kruskal's Algorithm"]),

    (7, "", ["Binary Trees", "Binary Search Trees", "AVL Trees", "B-Trees", "Heap"]),
    (7, "Tree Traversal", ["In-Order Traversal", "Pre-Order Traversal", "Post-Order Traversal"]),
    (7, "Search Algorithms", _BFS_DFS),

    (8, "", ["Trie", "Segment Trees", "Fenwick Trees",
             "Disjoint Set (Union-Find)", "Suffix Trees and Arrays"]),

    (9, "", ["2-3 Trees", "B/B+ Trees", "Skip List", "ISAM"]),
    (9, "Indexing", ["Linear Indexing", "Tree-Based Indexing"]),

    (10, "", ["Brute Force", "Backtracking", "Greedy Algorithms", "Randomised Algorithms",
              "Divide and Conquer", "Recursion", "Dynamic Programming",
              "Two Pointer Technique", "Sliding Window Technique",
              "Fast and Slow Pointers", "Cyclic Sort", "Merge Intervals",
              "Two Heaps", "Kth Element", "Island Traversal", "Multi-threaded"]),

    (11, "", ["Leetcode", "Edabit"]),
]


def all_topics():
    """Flat list of (section_id, group_name, title, order_index)."""
    counters = {}
    out = []
    for section_id, group, titles in TOPIC_GROUPS:
        for title in titles:
            order = counters.get(section_id, 0)
            counters[section_id] = order + 1
            out.append((section_id, group, title, order))
    return out
