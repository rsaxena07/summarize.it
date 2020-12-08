import numpy as np
import pandas as pd
import nltk

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class SummarizeItInference:
    
    def __init__(self):        
    
        self.dimension = 300
        self.glove_input_file = "glove\glove.6B." + str(self.dimension) + "d.txt"
    
        #generating stop words for english
        self.stop_words = set(stopwords.words('english'))

        # reading glove embeddings and storing them in a string
        embeddings_dict = {}
        with open(self.glove_input_file, 'r', encoding="utf-8") as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], "float32")
                embeddings_dict[word] = vector
        self.embeddings_dict = embeddings_dict
        
    # no functional use only used to verify proper creation of the object.
    def checkWord(self, word):
        embeds = self.embeddings_dict[word]
        print("Type of Embeddings: " + str(type(embeds)))
        print("First Embedding for " + word + " : " + str(embeds[0]))
        
        
    def average_context_embedding(self, filtered_words_list):
        total_found_words = 0
        document_embedding = np.zeros(self.dimension)
        for words in filtered_words_list:
            for word in words:
                if word in self.embeddings_dict:
                    document_embedding += self.embeddings_dict[word]
                    total_found_words += 1
                else: # can remove this else later
                    print(word + " not found")
        if total_found_words != 0:
            # to avoid division by 0
            document_embedding /= total_found_words
        self.document_embedding = document_embedding
        return
    
    def query(self, input_text, output_length_percent, keywords):
        
        if type(input_text) != str:
            print("invalid input_text. send proper string")
            return
            
        if output_length_percent<10 or output_length_percent>70:
            print("Invalid output percent (allowed between 10%-70%)")
            return
        
        self.output_length = len(input_text) * output_length_percent / 100
        print("--------- Input Length: " + str(len(input_text)) + "  Min Output Length: " + str(self.output_length) + " ----------")
        
        # remove after testing
        print ("Input: " + input_text)
        
        print("------Tokenization and removing stop words ---------")
        filtered_words_list = []
        sentences = sent_tokenize(input_text)
        for sentence in sentences:
            words = word_tokenize(sentence)

            filtered_words = [w.lower() for w in words if not w in self.stop_words]
            print(filtered_words) # remove print 
            filtered_words_list.append(filtered_words)
        
        print("------Average Context Calculation ---------")
        #generate average context
        self.average_context_embedding(filtered_words_list)

        
        print("------Sentence Scoring Begins ---------")
        sentence_scores = np.zeros(len(sentences))
        
        for idx, filtered_words_row in enumerate(filtered_words_list):
            found_words = 0
            score = 0
            for word in filtered_words_row:
                if word in self.embeddings_dict:
                    score += self.document_embedding.dot(self.embeddings_dict[word])
                    found_words += 1
                else:
                    print(word + " not found")
            
            if found_words != 0:
                score /= found_words
                sentence_scores[idx] = score
                print("Score for sentence " + str(idx) + " is: " + str(score))
                
        print("------ Generating Data-Frame ---------")
        sentences_lengths = [len(s) for s in sentences]
        sentences_dict = {'index': list(range(len(sentences))),
                'score': sentence_scores,
                'sentence': sentences,
                'filtered_words': filtered_words_list,
                'sentence_length': sentences_lengths}
        self.sentences_df = pd.DataFrame(data=sentences_dict).sort_values(by=['score'], ascending=False)
        print(self.sentences_df)
        
        print("------ Finding no of sentences in output ---------")
        score_wise_lengths = list(self.sentences_df['sentence_length'])
        op_sent_count = 0
        cumulative_length = 0
        while op_sent_count<len(sentences) and cumulative_length < self.output_length:
            cumulative_length += score_wise_lengths[op_sent_count]
            op_sent_count += 1
        print("total sentences in output: " + str(op_sent_count))
        
        output_text = " ".join(self.sentences_df[:op_sent_count].sort_values(by=['index'])['sentence'])
        
        print("=====================================================================")
        print("                    Final Summarization")
        print("=====================================================================")
        print ("Generated output: " + output_text)
        return output_text