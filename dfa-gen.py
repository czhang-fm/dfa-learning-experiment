import random

INIT_SIZE = 50
INIT_ALPHABET = 2
DFA_NUM = 2

class DFA:
    """A class that represents a deterministic finite automaton"""
    def __init__(self, size, alphabet):
        self.size = size # the initial size of the DFA
        self.alphabet = alphabet # set of actions
        self.transitions = {} # (state, action) -> state
        self.label = {} # 1 for accept, 0 for non-accept
        self.depth = 0

    def generate_trans_label(self):
        """randomly generate the initial transitions and labelling"""
        for s in range(self.size):
            self.label[s] = random.randint(0, self.alphabet - 1)
            for a in range(self.alphabet):
                target = random.randint(0, self.size - 1)
                self.transitions[(s, a)] = target
    
    #def __repr__(self) -> str:
    #    str(self.transitions)

    """removing states non-reachable from the initial state 0"""
    """at the same time we compute the depth of the dfa """
    def remove_nonreachables(self):
        """we first find all indices reachable from 0 """
        current = [] # the queue that is used for breadth-first exploration
        depth = {} # mapping from states to their depth
        max_depth = 0 # the value that is to be assigned to self.depth
        visited = set()
        current.append(0)
        visited.add(0)
        depth[0] = 0
        while len(current) != 0:
            s = current[0]
            current.pop(0)
            for a in range(self.alphabet):
                t = self.transitions[(s, a)]
                if not(t in visited):
                    depth[t] = depth[s] + 1
                    if max_depth < depth[t]:
                        max_depth = depth[t]
                    current.append(t)
                    visited.add(t)
        
        self.depth = max_depth
        if len(visited) == self.size: ## no need to do any adjustment
            return
        
        # now visited is the set of indices reachable and it's a proper subset
        states = list(visited)
        states.sort()
        tmp_label = {}
        tmp_transitions = {}
        for s in states:
            new_s = states.index(s)
            tmp_label[new_s] = self.label[s]
            for a in range(self.alphabet):
                t = self.transitions[(s, a)]
                new_t = states.index(t)
                tmp_transitions[(new_s, a)] = new_t
        
        self.label = tmp_label
        self.transitions = tmp_transitions
        self.size = len(states)


    def minimize(self):
        """minimize the current DFA"""
        """a partition represent a set of states, each pair of states in a partition are equivalent """
        seed = set() # this set stores a seed state for each partition, which is the range of part
        part = {} # a function that maps each state in 0..self.size-1 to its seed state
        seed.add(0)
        part[0] = 0
        other_label = -1 # the first state that has a different label than state 0
        """ initialize the partition map as two equivalence classes: accept states && non-accept states """
        for s in range(1, self.size):
            if self.label[s] != self.label[0]:
                if other_label == -1:
                    other_label = s
                    seed.add(s)
                    part[s] = s
                else:
                    part[s] = other_label
            else:
                part[s] = 0
        """We revise part and seed in the following code: """
        tag = True
        while tag:
            tag = False
            new_seed = set()
            old_part  = {} # just to remember the original partition of new seeds
            old_action = {} # remember for which action the new seed is generated
            for action in range(self.alphabet):
                for s in range(self.size):
                    seed_state = part[s]
                    if part[self.transitions[(s, action)]] != part[self.transitions[(seed_state, action)]]:
                        found = False
                        for ns in new_seed:
                            if old_part[ns] == part[s] and old_action[ns] == action and part[self.transitions[(s, action)]] == part[self.transitions[(ns, action)]]:
                                found = True
                                part[s] = ns
                                break
                        if not found:
                            new_seed.add(s)
                            old_part[s] = part[s]
                            part[s] = s
                            old_action[s] = action
                if len(new_seed) > 0:
                    tag = True
                    seed = seed.union(new_seed)
                    break
        
        """Now we need to codense the DFA and update self.size to the size of the seed set and also self.transitions """
        tmp_transitions = {}
        tmp_label = {}
        equ = {} # mapping each seed into a new index value in 0..len(seed)-1
        visited  = set()
        idx = 0
        for s in seed:
            if not (s in visited):
                equ[s] = idx
                tmp_label[idx] = self.label[s]
                idx += 1
                visited.add(s)
            for a in range(self.alphabet):
                t = self.transitions[(s, a)]
                seed_t = part[t]
                if not (seed_t in visited):
                    equ[seed_t] = idx
                    tmp_label[idx] = self.label[seed_t]
                    idx += 1
                    visited.add(seed_t)
                tmp_transitions[(equ[s], a)] = equ[seed_t]
        
        # update the DFA parameters
        self.size = idx
        self.transitions = tmp_transitions
        self.label = tmp_label
    
    def run(self, actions): # return 0 for non-accept, or 1 for accept
        """run the current dfa with an array of actions"""
        """we assume all actions are integers of values within [0, self.alphabet) """
        state = 0
        for a in actions:
            state = self.transitions[(state, a)]
        return self.label[state]

def DFA_gen():
    """generate a random DFA with a specified size"""
    dfa = DFA(INIT_SIZE, INIT_ALPHABET)
    dfa.generate_trans_label()

    return dfa

def random_depth(d):
    if random.randint(0,1) == 1:
        return d
    else:
        return random.randint(0, d-1)

def gen_test(dfa):
    # We generate test cases here.
    # At the moment we generate at most n^{h+2} training cases of length up to 1.5 * h, 
    # where h is the depth of the dfa and n is the size of alphabet
    # After that we generate at most n^{h+1} test cases of length up to 1.5 * h
    tests = []
    max_num_tests = 2**(dfa.depth - 1) # + 2)
    #print(max_num_tests)
    max_depth = dfa.depth * 3 // 2
    for i in range(max_num_tests):
        test_d = random_depth(max_depth)
        actions = []
        action_string = ''
        for j in range(test_d):
            a = random.randint(0, dfa.alphabet - 1)
            actions.append(a)
            if j == test_d - 1:
                action_string = action_string + str(a)
            else:
                action_string = action_string + str(a) + ' '
        result = dfa.run(actions)
        action_string = str(result) + ' ' + str(len(actions)) + ' ' + action_string
        if action_string not in tests:
            tests.append(action_string)
    return tests

def main():
    #dfa = DFA_gen()
    # up to here the DFA is not necessarily minimal
    #print(dfa.transitions)
    #print(dfa.label)
    #print(f"The DFA has {dfa.size} states.")
    #dfa.remove_nonreachables()
    #print("minimizing...")
    #dfa.minimize()
    #print(f"The DFA now has {dfa.size} states with depth {dfa.depth}.")
    #tests = gen_test(dfa)
    #print(f"generated {len(tests)} test cases")
    #for t in tests:
    #    print(t)
    num = 0
    while num < DFA_NUM:
        dfa = DFA_gen()
        dfa.remove_nonreachables()
        dfa.minimize()
        train = gen_test(dfa)
        train_filename = 'train' + str(num) + '.txt'
        f = open(train_filename, "x")
        f.write(f"The DFA has {dfa.size} states with depth {dfa.depth}. We have {len(train)} training entries.")
        for t in train:
            f.write('\n' + t)
        f.close()
        tests = gen_test(dfa)
        test_filename = 'test' + str(num) + '.txt'
        f = open(test_filename, "x")
        f.write(f"The DFA has {dfa.size} states with depth {dfa.depth}. We have {len(tests)} test entries.")
        for t in tests:
            f.write('\n' + t)
        f.close()
        num += 1
    
main()