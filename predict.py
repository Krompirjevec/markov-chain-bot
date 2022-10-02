import json
import random
from generate import update_counts, counts_to_probs

def random_step(transition_probs, node):
    """
    randomly chooses next word for given node based on transition_probs

    params:
        transition_probs: dict with structure {node1: {next_word1: prob1, next_word2: prob2, ...}, node2:...}
        node: string (consiting of one or multiple words)
    
    returns:
        next_word: string (consisting of one word) or None if string is not a key in transition probs
    """
    
    # roll and pick
    if node in transition_probs:
        words, probs = list(transition_probs[node]), list(transition_probs[node].values())
        roll = random.random()
        roll_idx = 0
        while roll > 0:
            roll -= probs[roll_idx]
            roll_idx += 1
        return words[roll_idx-1]
    else:
        return None

def generate_sentence_fixed_length(transition_probs, length, node_length, start_node=None, force_length=True):
    """
    generates a sentence with a length of length words

    params:
        transition_probs: dict with structure {node1: {next_word1: prob1, next_word2: prob2, ...}, node2:...}
        length: int of desired length for a sentence
        node_length: number of words in each string node
        start_node: string (consiting of one or multiple words) to use as a start of a sentence
        force_length: bool if True cuts of sentence to length words, if False naturaly finishes sentence after length has been reached

    returns:
        sentence: string of length words or more (depending on force_length)
    """

    # find start node
    if start_node == None or start_node not in transition_probs:
        node = random_step(transition_probs, ".")
    else:
        node = start_node

    # generate sentence
    sentence = generate_sentence(transition_probs, node_length, node)
    while len(sentence.split(" ")) < length:
        sentence += ". " + generate_sentence(transition_probs, node_length, None)
    
    return " ".join(sentence.split(" ")[:length]) if force_length else sentence

def generate_sentence(transition_probs, node_length, start_node=None, patience=10):
    """
    generates a sentence of arbitrary length - sentence ends when next node is terminating for patience times
    
    params:
        transition_probs: dict with structure {node1: {next_word1: prob1, next_word2: prob2, ...}, node2:...}
        node_length: number of words in each string node
        start_node: string (consiting of one or multiple words) to use as a start of a sentence
        patience: number of times to try to find a continuation of a sentence - useful for corpuses with short sentences
    
    returns:
        sentence: string with arbitrary number words
    """

    # check if transition probs is empty
    if not transition_probs:
        return None

    # find start node
    if start_node == None or start_node not in transition_probs:
        node = random_step(transition_probs, ".")
    else:
        node = start_node

    #generate sentence
    sentence = []
    while True:
        #print(node, end=" | ")

        # append first word of node
        sentence.append(node.split(" ")[0])

        # look for patience amount of times to find a next node that is not None (not found) or terminator
        for _ in range(patience):
            next_node = random_step(transition_probs, node)
            if next_node != "." and next_node != None:
                break
        
        # end sentence if next node not found or is terminator
        if next_node == "." or next_node == None:
            break

        # update node
        if node_length > 1:
            node = " ".join(node.split(" ")[1:]) + " " + next_node
        else:
            node = next_node

        # check if sentence is too long
        if len(sentence) > 1000:
            break

    # append remaining words if needed
    if node_length > 1:
        sentence.extend(node.split(" ")[-node_length+1:])

    return " ".join(sentence)

def main():
    """
    prints random sentence from corpus - slow with large corpora due to long calculating time
    """

    # load config
    with open("config.json", "r") as f:
        config = json.load(f)
    node_length = config["words_per_node"]
    corpus_path = config["corpus_path"]

    # load transition dict
    with open(corpus_path, "r") as f:
        corpus = json.load(f)
    
    # generate transition probs
    transition_counts = {}
    for sentence in corpus:
        update_counts(transition_counts, sentence.split(" "), node_length)
    transition_probs = counts_to_probs(transition_counts)

    print("\n", generate_sentence(transition_probs, node_length))

if __name__ == "__main__":
    main()
