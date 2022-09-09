import discord
import json
import re

from predict import generate_sentence
from generate import update_counts, counts_to_probs

def main():
    # load config
    with open("config.json", "r") as f:
        config = json.load(f)
    node_length = config["words_per_node"]
    kword = config["kword"]
    corpus_path = config["corpus_path"]
    checkpoint = config["checkpoint"]
    ignored_users = config["ignored_users"]
    learning = True if config["learning"] == "true" else False

    # load credentials
    with open("data/secret.json", "r") as f:
        creds = json.load(f)
    token = creds["token"]

    # load data
    corpus = []
    transition_probs = {}
    transition_counts = {}
    try:
        with open(corpus_path, "r") as f:
            corpus = json.load(f)
        for sentence in corpus:
            update_counts(transition_counts, sentence.split(" "), node_length)
        transition_probs = counts_to_probs(transition_counts)
    except FileNotFoundError:
        print(f"no corpus file at '{corpus_path}'... starting new empty corpus")

    # client setup
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # action on message
    message_count = 0
    @client.event
    async def on_message(message):

        # there is probably a better way to do this
        nonlocal message_count
        nonlocal corpus
        nonlocal transition_counts
        nonlocal transition_probs
        
        message_words = message.content.split(" ")

        # do nothing if message was posted by this bot
        if message.author == client.user:
            return

        # post a generated sentence if bot was mentioned
        elif kword in message_words:
            
            # remove keyword and pick a starting node
            message_words.remove(kword)
            if len(message_words) >= node_length:
                start_node = " ".join(message_words[-node_length:])
            else:
                start_node = None
            
            # generate a random sentence and post it
            sentence = generate_sentence(transition_probs, node_length, start_node)
            # print(start_node, " \t| ", sentence)
            if sentence is not None:
                await message.channel.send(re.sub("@", "", sentence)[:1999])
            else:
                await message.channel.send("Could not generate a sentence.")

        # learning
        elif learning:

            # steal the data <- possible GDPR violation :D
            if message.author.id not in ignored_users:
                
                #TODO: ADD MESSAGE CLEANUP HERE

                # add sentence to corpus
                corpus.append(message.content)

                # split for updating
                new_sentence = message.content.split(" ")

                # update counts, increment message_count
                update_counts(transition_counts, new_sentence, node_length)
                message_count += 1
                print(f"saving in: {checkpoint-message_count}")
                
                # save if checkpoint is reached
                if message_count == checkpoint:

                    # recalculate probs
                    transition_probs = counts_to_probs(transition_counts)
                    
                    # save corpus
                    with open(corpus_path, "w") as f:
                        json.dump(corpus, f)

                    # reset message_count
                    print("saved")
                    message_count = 0

    client.run(token)

if __name__ == "__main__":
    main()