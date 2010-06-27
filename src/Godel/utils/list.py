from collections import deque

class list_functions:
    def flatten(self, List):
        ### take a list of varied depth
        ### and flatten it! with no recursion
        return reduce(list.__add__, map(lambda x: list(x), [y for y in List]))


    def uniqify(self, sequence): 
        # order preserving
         def id_(x):
             if isinstance(x, tuple):
                 x = ''.join(x)
             if isinstance(x, list):
                 x = ''.join(x)
             if isinstance(x, dict):
                 x = cPickle.dumps(x)
             
             return x
             
         seen   = {}
         result = []
         for item in sequence:
             marker = id_(item)
             if marker in seen:
                 continue
             
             seen[marker] = True
             result.append(item)
             
         return result
     
    def print_list(self, List):
        stack = [(List, -1)]
        while stack:
            item, level = stack.pop()
            if isinstance(item, list):
                for i in reversed(item):
                    stack.append((i, level+1))
            else:
                print "\t" * level, item

    def max_depth(self, List):
        accessorList = self.subtree_indices(List)
        a_list = self.flatten(accessorList)
        c_max_depth = reduce(lambda x, y: max(x, y), a_list)
        if c_max_depth:
            return max(c_max_depth)


    def isBranch(self, node):
        return isinstance(node, list)
        
    def treeTraversal(self, node):
        debug(node)
        debug(self.depth_stack)

        self.frame_stack.append([])
        for x in self.depth_stack:
            self.frame_stack[-1].append(x)
        
        if self.isBranch(node):
            self.depth_stack.append((self.depth_stack[-1][0] + 1, len(node)))
            for child in node:
                if isinstance(child, list):
                    self.treeTraversal(child)
                else:
                    self.list_depth_stack.append((self.element, len(self.depth_stack)))
                    self.element += 1
                    
                    if len(self.depth_stack) > 1:
                        while self.depth_stack:
                            depth, length = self.depth_stack.pop()
                            if length-1 > 0:
                                self.depth_stack.append((depth, length-1))
                                break
        



    def combinations(iterable, r):
        # combinations('ABCD', 2) --> AB AC AD BC BD CD
        # combinations(range(4), 3) --> 012 013 023 123
        pool = tuple(iterable)
        n = len(pool)
        if r > n:
            return

        indices = range(r)
        
        yield tuple(pool[i] for i in indices)
        
        while True:
            for i in reversed(range(r)):
                if indices[i] != i + n - r:
                    break
                else:
                    return
                
            indices[i] += 1
            for j in range(i+1, r):
                indices[j] = indices[j-1] + 1

            yield tuple(pool[i] for i in indices)


    def subtree_indices(self, tree_rep):
        tree = [([], tree_rep)]
        list_of_indexLists = []
        tree_indices = deque()
        while tree != []:
            (indices, sub_tree) = tree.pop(0)
            #print indices, sub_tree
            list_of_indexLists.append(indices)
            for (ordinal, subTree) in enumerate(sub_tree[1:]):
                debug(ordinal)
                debug(subTree)
                if isinstance(subTree, list):
                    idxs = indices[:]

                    debug(idxs)
                    debug(ordinal)

                    if len(idxs) == 0:
                        tree_indices.append([0])
                    else:
                        tree_indices.append(idxs)

                    idxs.append(ordinal+1)
                    tree.append((idxs, subTree))

        return list_of_indexLists
