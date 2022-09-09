import json
import os

###
# TODO: text processing
###

def add_node_count(transition_counts, node, next_word):
    """
    adds a node into transition counts dict - if node or next node do not exist -> create new entry
    
    params:
        transition_counts: dict with structure {node1: {next_word1: count1, next_word2: count2, ...}, node2:...}
        word: current node
        next_word: next node
    """

    if node in transition_counts:
        if next_word in transition_counts[node]:
            transition_counts[node][next_word] += 1
        else:
            transition_counts[node][next_word] = 1
    else:
        transition_counts[node] = {next_word: 1}

def update_counts(transition_counts, sentence, node_length):
    """
    updates tranistion counts dict (modifies transition_counts)

    params:
        transition_counts: dict with structure {node1: {next_word1: count1, next_word2: count2, ...}, node2:...}
        sentence: list of strings (words) to use for updating
        node_length: number of words per node in markov chain (number of words in key in transition_counts dict)
    """
    # check if sentence is smaller than required node_length
    if len(sentence) < node_length:
        return

    # start with the terminator
    add_node_count(transition_counts, ".", " ".join(sentence[0:node_length]))

    # increment next word counts for each node
    for i, _ in enumerate(sentence[:-node_length]):
        node = " ".join(sentence[i:i+node_length])
        next_node = sentence[i+node_length]
        add_node_count(transition_counts, node, next_node)
    
    # add terminator (".") count for last node
    add_node_count(transition_counts, " ".join(sentence[-node_length:]), ".")

def counts_to_probs(transition_counts):
    """
    translates transition_counts dict into transition_probs dict and returns it

    params:
        transition_counts: dict with structure {node1: {next_word1: count1, next_word2: count2, ...}, node2:...}
    
    returns:
        transition_probs: dict with structure {node1: {next_word1: prob1, next_word2: prob2, ...}, node2:...}
    """

    # translate counts into probs
    transition_probs = {key: val.copy() for key, val in transition_counts.items()} # so you copy inner dicts as well
    for word, next_words in transition_probs.items():
        total_counts = 0
        for next_word, counts in next_words.items():
            total_counts += counts
        
        for next_word, counts in next_words.items():
            prob = counts / total_counts
            transition_probs[word][next_word] = prob
    
    return transition_probs

def main():
    """
    dumps calculated transition counts and probs into files for testing
    """

    # load config file
    with open("config.json", "r") as f:
        config = json.load(f)
    corpus_path = config["corpus_path"]      # path to corpus.txt file
    node_length = config["words_per_node"]   # number of previous words to consider when picking next the next word
    out_path = "data"     # path to folder for out files

    # get corpus
    with open(corpus_path, "r") as f:
        sentences = [message.split(" ") for message in json.load(f)]
    
    # generate dict where key: words, val: dict where key: next word, val: counts
    transition_counts = {}
    for sentence in sentences:
        update_counts(transition_counts, sentence, node_length)
    
    # calculate probabilities for transitions
    transition_probs = counts_to_probs(transition_counts)

    # dump counts and probs into .json files
    with open(os.path.join(out_path, "transition_counts.json"), "w") as f:
        json.dump(transition_counts, f)

    with open(os.path.join(out_path, "transition_probs.json"), "w") as f:
        json.dump(transition_probs, f)

if __name__ == "__main__":
    main()
