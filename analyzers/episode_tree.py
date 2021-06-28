import sys
import copy
import logging
import time
import random
from analyzers.analyzer import Analyzer
from definitions.episode import Episode
from definitions.episode_trees import Node, EpisodeTrees

INTERVAL = 250

class EpisodeTree(Analyzer):
    def __init__(self, name):
        super().__init__(name)
        self.rules = None

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.info('Learning: {}'.format(self.get_name()))

        classes = config["classes"]
        max_len = config["max_len"]
        min_fr = config["min_fr"]
        min_conf = config["min_conf"]
        rv = config["rv"]
        width = config["width"]
        f, rules = extract_episodes(sequence, classes, max_len, width, min_fr, min_conf, rv)
        self.rules = rules

        for l in f.keys():
            logging.debug("F[{}]:".format(l))
            for e in f[l]:
                logging.debug("  - {}".format(f[l][e].get_nodes().values()))

        try:
            self.model = generate_episode_tree(f, rules)
            for episode_tree in self.model.values():
                logging.info("===== Episode Tree =====")
                episode_tree.print_tree(0)
                logging.info("\n")
            logging.info("Episode Tree is generated")
        except:
            self.mode = None
            logging.info("Episode Tree is not generated")

    def analysis(self, sequence, config):
        logging.info('Analysis: {}'.format(self.get_name()))
        ret = []
        episodes = []
        classes = config["classes"]
        max_len = config["max_len"]
        min_fr = config["min_fr"]
        min_conf = config["min_conf"]
        width = config["width"]
        nresults = config["nresults"]
        ncandidates = config["ncandidates"]
        nfinal = config["nfinal"]
        rv = config["rv"]
        length = max_len

        results = []
        starttime = int(time.time())
        while True:
            curr = int(time.time())
            if curr > starttime + INTERVAL:
                break
            episodes = extract_candidates(sequence, length, ncandidates)

            for episode in episodes:
                prob, hepisode = inference(self, episode)
                logging.info("final: {}, probability: {}\%".format(hepisode, round(prob * 100, 2)))

                for state in hepisode:
                    logging.info("hidden label: {}".format(state.get_hidden_label()))
                    if prob > 0 and state.get_hidden_label() == "I":
                        #time.sleep(1)
                        #results.append(state)
                        results.append((prob, state))
                        #break

                logging.info("Number of Episodes: {}, Number Of Results (config): {}, Number in Results: {}".format(len(episodes), nresults, len(results)))
                time.sleep(0.5)
            if len(results) >= nresults:
                break

        results = sorted(results, reverse=True, key=lambda x:x[0])

        ret = results[0:nfinal]
        self.print_infection_information(ret, config)

        logging.info("Analysis based on {} is finished".format(self.get_name()))

        return ret

cache = {}

def exist_episode(et, nodes):
    ret = True
    episode_tree = et.model
    episode = episode_tree[nodes[0]].find_exact_episode(nodes)
    if episode == []:
        ret = False
    return ret

def get_code(episode):
    ret = ""

    for state in episode:
        ret += state.get_hidden_label()

    return ret

def inference(et, episode):
    classes = ["B", "I", "R", "A"]
    rules = et.rules
    prob = 1.0

    curr = ""
    for i in range(len(episode)):
        state = episode[i]
        tmp = []
        for c in classes:
            try:
                coin = random.random()
                if coin > 0.5:
                    tprob = 1
                else:
                    tprob = rules[curr][curr + c]
            except:
                tprob = 0
            logging.debug("{} -> {}: {}, Prob[{}]: {}".format(curr, curr + c, tprob, c, state.get_probability_char(c)))
            tmp.append((c, tprob * state.get_probability_char(c)))
        tmp = sorted(tmp, key=lambda x: x[1], reverse=True)
        hs = tmp[0][0]
        sprob = tmp[0][1]
        curr = curr + hs
        state.set_hidden_label(hs)
        prob *= sprob
        logging.debug(">> {} -> {}: {}".format(curr[:-1], curr, prob))

    logging.info("Finally Decoded One: {}".format(curr))
    return prob, episode

used_candidates = []

def extract_candidates(sequence, length, ncandidates):
    ret = []
    states = sequence.get_sequence()

    lst = []
    for state in states:
        lst.append(state)
        if state.get_best_label_string() == "infection":
            for _ in range(20):
                lst.append(state)

    nstates = len(lst)

    while ncandidates > 0:
        used_idx = []
        episode = []
        code = ""

        for _ in range(length):
            idx = random.randrange(0, nstates)
            used_idx.append(idx)
            episode.append(lst[idx])

        episode = sorted(episode, key=lambda state:state.get_start_time())
        used_idx = sorted(used_idx)

        if used_idx not in used_candidates:
            ret.append(episode)
            used_candidates.append(used_idx)
            ncandidates -= 1

    logging.debug("extract_candidates: {}".format(ret))
    return ret

def extract_episodes(sequence, classes, max_len, width, min_fr, min_conf, rv):
    return algorithm1(sequence, classes, max_len, width, min_fr, min_conf, rv)

def generate_episode_tree(f, rule):
    max_len = max(f.keys())
    episode_trees = {}

    for mlen in reversed(range(1, max_len + 1)):
        logging.debug("f[{}]: {}".format(mlen, f[mlen]))
        for episode in f[mlen].values():
            nodes = episode.get_nodes()
            maps = episode.get_maps()
            root = nodes[1]

            if root not in episode_trees:
                episode_trees[root] = EpisodeTrees(Node(root))

            episode_trees[root].add_episode(episode)

    return episode_trees

def make_sub_episodes(lst):
    if len(lst) == 0:
        return [[]]
    else:
        base = make_sub_episodes(lst[:-1])
        operator = lst[-1:]
        return base + [(b + operator) for b in base]

def sub_episodes(ep):
    episode = list(ep.get_nodes().values())
    lst = make_sub_episodes(episode)
    ret = []

    for e in lst:
        if e == []:
            continue

        if e == episode:
            continue

        d = {}
        k = 1
        for item in e:
            d[k] = item
            k += 1
        ret.append(Episode(aname=None, serial=None, window=None, nodes=d, maps=ep.get_maps()))

    return ret

def previous_episode(ep):
    episode = list(ep.get_nodes().values())
    d = {}
    k = 1

    for n in episode[:-1]:
        d[k] = n
        k += 1

    return Episode(aname=None, serial=None, window=None, nodes=d, maps=ep.get_maps())
    
def sibling_episodes(classes, ep):
    ret = []
    episode = list(ep.get_nodes().values())
    d = {}
    k = 1
    maps = ep.get_maps()
    
    for n in episode[:-1]:
        d[k] = n
        k += 1
    
    for c in classes:
        tmp = copy.deepcopy(d)
        tmp[k] = maps[c]
        ret.append(Episode(aname=None, serial=None, window=None, nodes=tmp, maps=maps))

    return ret

# Algorithm 1: Find rules 
def algorithm1(sequence, classes, max_len, width, min_fr, min_conf, rv):
    logging.info("Start: Algorithm 1")
    rule = {}

    f = algorithm2(sequence, classes, max_len, width, min_fr, rv)
    
    logging.info("F: ")
    for l in f:
        logging.info("  > F[{}]:".format(l))
        for k in f[l]:
            logging.info("    - {}".format(list(f[l][k].get_nodes().values())))
        logging.info("")

    for l in f:
        for k in f[l]:
            a = f[l][k]
            b = previous_episode(a)
            lst = sibling_episodes(classes, a)

            total = 0
            for ep in lst:
                key = ep.get_code()
                if key not in cache:
                    freq = ep.get_frequency(sequence)
                    cache[key] = freq
                total += cache[key]

            if total > 0:
                confidence = cache[a.get_code()] / total
                logging.info("{} -> {}: {}".format(b.get_nodes().values(), a.get_nodes().values(), confidence))

                if confidence >= min_conf:
                    acode = a.get_code()
                    bcode = b.get_code()

                    #if acode == '':
                    #    acode = 0

                    #if bcode == '':
                    #    bcode = 0

                    if acode not in rule:
                        rule[acode] = {}

                    if bcode not in rule:
                        rule[bcode] = {}

                    rule[bcode][acode] = confidence
                    rule[acode][bcode] = confidence
           
    logging.info("Rule =====\n{}".format(rule))

    logging.info("Finish: Algorithm 1")
    return f, rule

# Algorithm 2: Find the frequent episodes
def algorithm2(sequence, classes, max_len, width, min_fr, rv):
    logging.info("Start: Algorithm 2")
    c = {}
    f = {}
    c[1] = {}
    k = 0
    for n in classes:
        k += 1
        tmp = {}
        tmp[1] = classes[n]
        c[1][k] = Episode(aname=None, serial=None, window=None, nodes=tmp, maps=classes)

    l = 1
    logging.info("C[{}]".format(l))
    for k in c[l]:
        logging.info("  - {}".format(list(c[l][k].get_nodes().values())))

    while l <= max_len or c[l] == []:
        f[l] = algorithm5(c[l], sequence, classes, max_len, width, min_fr, rv)
        
        logging.info("F[{}]:".format(l))
        for k in f[l].keys():
            logging.info("  - {} ({}) ".format(list(f[l][k].get_nodes().values()), f[l][k].get_block_start()))

        l += 1

        c[l] = algorithm3(f[l-1], l-1, classes, rv)
        logging.info("C[{}]".format(l))
        for k in c[l]:
            logging.info("  - {}".format(list(c[l][k].get_nodes().values())))

    logging.info("Finish: Algorithm 2")
    return f

# Algorithm 3: Find the candidate frequent episodes
def algorithm3(f, l, classes, rv):
    logging.info("Start: Algorithm 3")
    ret = {}
    k = 0

    if l == 1:
        for h in range(1, len(f)+1):
            f[h].set_block_start(1)
    else:
        bstart = 1
        for i in f:
            f[i].set_block_start(bstart)
            if f[bstart].get_nodes()[l-1] != f[i].get_nodes()[l-1]:
                bstart = i
                f[i].set_block_start(bstart)

    for i in f:
        current_block_start = k+1
        j = f[i].get_block_start()

        while f[j].get_block_start() == f[i].get_block_start():
            alpha_nodes = {}
            beta_nodes = {}
            fi_nodes = f[i].get_nodes()
            fj_nodes = f[j].get_nodes()
            found = True

            for x in range(1, l+1):
                alpha_nodes[x] = fi_nodes[x]
            alpha_nodes[l+1] = fj_nodes[l]

            for y in range(1, l):
                for x in range(1, y):
                    beta_nodes[x] = alpha_nodes[x]

                for x in range(y, l+1):
                    beta_nodes[x] = alpha_nodes[x+1]

                contained = False
                for n in range(1, len(f) + 1):
                    if f[n].compare(beta_nodes) == True:
                        contained = True

                # Subepisode is not included in the episode collection of the size l
                if not contained:
                    found = False
                    break

            # All the subepisodes are included in the episode collection of the size l
            if found:
                duplicated = False
                for key in ret:
                    lst = ret[key].get_nodes()
                    if lst == alpha_nodes:
                        duplicated = True
                if not duplicated:
                    k = k + 1
                    ret[k] = Episode(aname=None, serial=None, window=None, nodes=alpha_nodes, maps=classes)
                    ret[k].set_block_start(current_block_start)

            j += 1
            if j not in f:
                break

    logging.info("Finish: Algorithm 3")
    return ret

def algorithm5(c, sequence, classes, max_len, width, min_fr, rv):
    logging.info("Start: Algorithm 5")
    ret = {}
    waits = {}
    beginsat = {}
    k = 0
    win = width * sequence.get_granularity()

    for cl in classes:
        waits[classes[cl]] = set([])

    for alpha in c.values():
        nodes = alpha.get_nodes()
        
        for i in range(1, alpha.get_size() + 1):
            alpha.set_initialized(i, 0)

        waits[nodes[1]].add((alpha, 1))
        alpha.set_freq_count(0)

    for t in sequence.drange(sequence.get_start_time() - win, sequence.get_start_time(), sequence.get_granularity()):
        beginsat[round(t, rv)] = set([])

    for start in sequence.drange(sequence.get_start_time() - win + sequence.get_granularity(), sequence.get_end_time() + sequence.get_granularity(), sequence.get_granularity()):
        start = round(start, rv)
        beginsat[round(start + win - sequence.get_granularity(), rv)] = set([])
        transitions = set([])

        lst = sequence.get_events_at(round(start + win - sequence.get_granularity(), rv))

        for state in lst:
            # TODO: Check how to set the label of the state is the best (using get_best_label() is the best way?)
            """
            num = 0
            
            if state.get_label("attack") == 1:
                num = 1
            elif state.get_label("reconnaissance") == 1:
                num = 3
            elif state.get_label("infection") == 1:
                num = 2
            else:
                num = 0
            """

            num = state.get_best_label()
            a = classes[num]
            t = state.get_start_time()
            rlst = []

            for alpha, j in waits[a]:
                if j == alpha.get_size() and alpha.get_initialized(j) == 0:
                    alpha.set_in_window(start)

                if j == 1:
                    transitions.add((alpha, 1, round(start + win - sequence.get_granularity(), rv)))
                else:
                    transitions.add((alpha, j, round(alpha.get_initialized(j-1), rv)))
                    beginsat[round(alpha.get_initialized(j-1), rv)].remove((alpha, j-1))
                    alpha.set_initialized(j-1, 0)
                    rlst.append((alpha, j))
            
            for (alpha, j) in rlst:
                waits[a].remove((alpha, j))

        for alpha, j, t in transitions:
            nodes = alpha.get_nodes()
            alpha.set_initialized(j, round(t, rv))

            beginsat[round(t, rv)].add((alpha, j))

            if j < alpha.get_size():
                waits[nodes[j+1]].add((alpha, j+1))

        for alpha, l in beginsat[round(start - sequence.get_granularity(), rv)]:
            nodes = alpha.get_nodes()

            if l == alpha.get_size():
                alpha.set_freq_count(alpha.get_freq_count() - alpha.get_in_window() + start)
            else:
                if (alpha, l+1) in waits[nodes[l+1]]:
                    waits[nodes[l+1]].remove((alpha, l+1))
            alpha.set_initialized(l, 0)

    k = 0
    for alpha in c.values():
        if alpha.get_freq_count() / (sequence.get_end_time() - sequence.get_start_time() + win - sequence.get_granularity()) > min_fr:
            k += 1
            ret[k] = alpha

    logging.info("Finish: Algorithm 5")
    return ret

