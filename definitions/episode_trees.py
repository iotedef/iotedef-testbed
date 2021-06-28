from definitions.episode import Episode
import copy

class Node:
    def __init__(self, label):
        self.label = label
        self.count = 0

    def get_label(self):
        return self.label

    def get_count(self):
        return self.count

    def add_count(self):
        self.count += 1

    def print_node(self, space):
        indent = ""
        for i in range(space):
            indent += " "
        print ("{}Node({})".format(indent, self.get_label()))

class EpisodeTrees:
    def __init__(self, root):
        self.root = root
        self.sub_trees = []

    def get_root(self):
        return self.root

    def add_sub_tree(self, tree):
        self.sub_trees.append(tree)

    def add_episode(self, episode):
        tree_node = self.root
        maps = episode.get_maps()
        tree_node.add_count()

        mlen = episode.get_size()
        nodes = {}
        for i in reversed(range(1, mlen)):
            nodes[i] = episode.get_nodes()[i+1]
        ep = Episode(aname=None, serial=None, window=None, nodes=nodes, maps=maps)

        if ep.get_size() > 0:
            found = False
            first_label = ep.get_nodes()[1]
            for sub_tree in self.sub_trees:
                if sub_tree.get_root().get_label() == first_label:
                    found = True
                    sub_tree.add_episode(ep)
                    break

            if not found:
                newtree = EpisodeTrees(Node(first_label))
                self.add_sub_tree(newtree)
                newtree.add_episode(ep)

    def find_episode(self, ep):
        ret = []
        ret.append(self.root)
        episode = copy.deepcopy(ep)
        episode.pop(0)
        
        if len(self.sub_trees) == 0 or len(episode) == 0:
            return ret
        else:
            for sub_tree in self.sub_trees:
                if sub_tree.get_root().get_label() == episode[0]:
                    return ret + sub_tree.find_episode(episode)
            return ret

    def find_exact_episode(self, episode):
        ret = self.find_episode(episode)
        if len(ret) != len(episode):
            ret = []
        return ret

    def print_tree(self, space):
        node = self.root
        node.print_node(space)

        if len(self.sub_trees) > 0:
            for sub_tree in self.sub_trees:
                sub_tree.print_tree(space + 2)
