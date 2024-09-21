# an experiment for reading in a dfa, extracting a prefix-closed tree of raw_data, which maps strings in {0,1}^{<=d} to {-1,0,1}, 
# where d is the maximal length of a training string, and -1, 0, 1 represent "don't know", "not accept", and "accept", respectively.

def update_data(raw_data, state, accept):
    """insert a mapping from a state to {-1, 0, 1}"""
    if not (state in raw_data) or accept != -1: 
        raw_data[state] = accept

def insert_states(line, raw_data):
    """add a sequence of states into the raw_data list"""
    states = line.split()
    accept = int(states[0])
    state = ''
    for i in range(2, len(states)):
        # insert a prefix of the string (line) into raw_data
        update_data(raw_data, state, -1)
        state = state + states[i]
    update_data(raw_data, state, accept)

def produce_raw_data(filename):
    """create a raw_data list"""
    my_file = open(filename)
    data = my_file.read()
    my_file.close()
    lines = data.splitlines()
    # the first line is a desription sentence of the form "n1 n2" which can be safely skipped
    # where n1 is the number of entries and n2 is the size of alphabet (often 2)
    raw_data = {}
    for i in range(1, len(lines)):
        insert_states(lines[i], raw_data)
    
    return raw_data

def read_test_data(filename):
    """create a list of strings in {0,1}^*, each string represented as a list... """
    my_file = open(filename)
    data = my_file.read()
    my_file.close()
    lines = data.splitlines()
    # the first line is a desription sentence of the form "n1 n2" which can be safely skipped
    # where n1 is the number of entries and n2 is the size of alphabet (often 2)
    test_data = []
    for i in range(1, len(lines)):
        actions = lines[i].split()
        actions.pop(1)
        actions.pop(0)
        test_data.append(actions)
    return test_data

def check_comp(s1, s2, data, comp, incomp):
    if s2 in comp[s1]: return True
    elif s2 in incomp[s1]: return False
    # if not in the caches
    if data[s1] != -1 and data[s2] != -1 and data[s1] != data[s2]: # incompatiblity at current states
        incomp[s1].add(s2)
        incomp[s2].add(s1)
        return False
    elif not(s1+'0' in data) or not(s2+'0' in data): # left '0' compatible, checking right '1'
        if not(s1+'1' in data) or not(s2+'1' in data):
            comp[s1].add(s2)
            comp[s2].add(s1)
            return True
        elif check_comp(s1+'1', s2+'1', data, comp, incomp):
            comp[s1].add(s2)
            comp[s2].add(s1)
            return True
        else:
            incomp[s1].add(s2)
            incomp[s2].add(s1)
            return False
    elif check_comp(s1+'0', s2+'0', data, comp, incomp): # checking left '0' compatibility first, if true, check right '1'
        if not(s1+'1' in data) or not(s2+'1' in data):
            comp[s1].add(s2)
            comp[s2].add(s1)
            return True
        elif check_comp(s1+'1', s2+'1', data, comp, incomp):
            comp[s1].add(s2)
            comp[s2].add(s1)
            return True
        else:
            incomp[s1].add(s2)
            incomp[s2].add(s1)
            return False
    else: # left '0' incompatiblitly
        incomp[s1].add(s2)
        incomp[s2].add(s1)
        return False

def create_compatibility(states, data):
    comp = {}
    incomp = {}
    for i in range(len(states)):
        comp[states[i]]  = set()
        incomp[states[i]] = set()

    for i in reversed(range(len(states))):
        for j in reversed(range(i)):
            # now check if s1 and s2 are compatible with memoization
            check_comp(states[i], states[j], data, comp, incomp)
    return comp, incomp

def create_weight(states):
    weights = {}    # mapping each state to an int value
    for i in reversed(range(len(states))):
        state = states[i]
        left = states[i] + str('0')
        right = states[i] + str('1')
        if left in weights:
            if right in weights:
                weights[state] = weights[left] + weights[right] + 1
            else:
                weights[state] = weights[left] + 1
        elif right in weights:
            weights[state] = weights[right] + 1
        else:
            weights[state] = 1
    return weights

def incomp_class(state_one, state_two, merged_classes, incomp):
    """check if state_one and state_two are incompatible at the level of equivalence classes"""
    for s in merged_classes[state_one]:
        for t in merged_classes[state_two]:
            if s in incomp[t]:
                return True
    return False

def merge(state_one, state_two, eq_classes, merged_classes):
    """recursively merge state_one with state_two"""
    set_one = merged_classes[state_one]
    set_two = merged_classes[state_two]
    new_set = merged_classes[state_one].union(merged_classes[state_two])
    for s in set_one:
        merged_classes[s] = new_set
    for s in set_two:
        merged_classes[s] = new_set
    eq_classes.remove(state_two)
    if state_one+'0' in eq_classes and state_two+'0' in eq_classes:
        merge(state_one+'0', state_two+'0', eq_classes, merged_classes)
    if state_one+'1' in eq_classes and state_two+'1' in eq_classes:
        merge(state_one+'1', state_two+'1', eq_classes, merged_classes)

def merge_states(eq_classes, incomp): 
    """this function implements strategy 1 which is deterministic"""
    merged_classes = {} # eventually this maps each state to a set of all states in the same class
    for state in eq_classes:
        merged_classes[state] = {state} # initialized merged_classes as the identity relation
    while eq_classes != []:
        if len(eq_classes) == 1: break # all class merging is done
        top_tag = 0
        state_one = eq_classes[0]
        idx = 1
        while incomp_class(state_one, eq_classes[idx], merged_classes, incomp): 
            if idx >= len(eq_classes) - 1: #eq_classes[idx] is now the last
                #eq_classes.pop(0)
                eq_classes.remove(state_one)
                top_tag = 1
                break
            else:
                idx += 1
        if top_tag == 1: continue
        # now state_one is compatible with eq_classes[idx]
        merge(state_one, eq_classes[idx], eq_classes, merged_classes)
    
    return merged_classes # finally we return the equivalence class relation

def get_sign(state, merged_classes, data):
    """to find the sign of a given equivalent class"""
    for s in merged_classes[state]:
        if data[s] != -1:
            return data[s]
    return -1   # not found

def get_next(bit, state, merged_classes): # to find out the next state given state and 0/1
    for s in merged_classes[state]:
        if (s + bit) in merged_classes.keys():
            return s + bit
    return 'None'

def not_visited(state, visited, transition, current_state, merged_classes): 
    """add (s, t) to a transition, and decide if t has been visited or not. If not, add t; 
    if yes, make sure to add (s, t') where t' is the state already in visited """
    assert state != 'None'
    for s in visited:
        for t in merged_classes[s]:
            if t == state:
                transition[current_state] = s # the representative state
                return False
    visited.add(state) # add state as a new representative state
    transition[current_state] = state
    return True

def generate_dfa(state_set, merged_classes, data):
    """compute a set of states with labelling and transition functions"""
    dfa, label, visited = [], {}, set()
    transition_left, transition_right = {}, {}
    assert len(state_set) != 0
    label[''] = get_sign('', merged_classes, data)
    dfa.append('')
    visited.add('')
    while dfa != []: # dfa stores what have not yet computed
        current_state = dfa[0]
        dfa.remove(current_state)
        left = get_next('0', current_state, merged_classes)
        if left != 'None':
            if not_visited(left, visited, transition_left, current_state, merged_classes):
                label[left] = get_sign(left, merged_classes, data)
                dfa.append(left)
        right = get_next('1', current_state, merged_classes)
        if right != 'None': 
            if not_visited(right, visited, transition_right, current_state, merged_classes):
                label[right] = get_sign(right, merged_classes, data)
                dfa.append(right)
    return visited, label, transition_left, transition_right

def main():
    """the starting point"""
    data = produce_raw_data("~/train.a")
    states = list(data.keys())
    sorted(states, key=lambda x: len(x))
    #print(states)    
    print("totally " + str(len(states)) + " states:")

    # Next, we use DP to sort out two relations:
    # The first compatibility relation is encoded by a dictionary/mapping from strings to lists of strings
    # starting from the largest states (longest strings)
    comp, incomp = create_compatibility(states, data) # still need to simplify this function call...

    # The first heuristic is deterministic.
    # We calculate a weight for all all states/nodes of the tree.
    # Plainly, the weight of a node is the number of nodes in the tree rooted at this node.
    # (A) We start from node X (or class X) with the largest weight, and find the node Y (or class Y) with largest weight that is compatible with X
    # (B) Merge X with Y recursively, which creates a number of equivalence classes on successive states due to the merge.
    #     The compatibility relations is now defined for classes (of states).
    # (C) If X is not compatible with all other classes (of singleton state), remove X. Then, repeat (A) with the class currently with the largest weight. 
    weights = create_weight(states)
    print("The weight of the root is " + str(weights['']))

    # We start from a list of classes, where each class contains a single state
    eq_classes = list(data.keys())
    sorted(eq_classes, key=lambda x: weights[x])
    
    # Strategy 1: (greedy) start with all singleton classes, merge the largest with the largest compatible so far until that largest class is incompatible with all others
    merged_classes = merge_states(eq_classes, incomp)
    #print("The states equivalent to the root state has", end =" ")
    #print(str(len(merged_classes[''])) + " states.")
    
    visited, label, transition_left, transition_right = generate_dfa(set(states), merged_classes, data)
    print("Generated "+ str(len(visited)) + " states.")
    #print("The initial state has label "+ str(label['']))
    print("There are "+ str(len(transition_left.keys())) + " left transitions and "+ str(len(transition_right.keys())) + " right transitions")
    determined = 0
    for s in label:
        if label[s] != -1:
            determined += 1
    print(f"There are {determined} determined states")

    test_data = read_test_data("~/test.a")
    # now we run through all test cases over the dfa represented by visited, label, transition_left, transition_right, where init = ''
    output = ''
    for actions in test_data:
        my_state = ''
        for a in actions:
            if a == '0':
                my_state = transition_left[my_state]
            else:
                my_state = transition_right[my_state]
        output += str(label[my_state])
    print(output) # a string in {0,1}^1800

main()
