
# TaggedCorpus seems outdated
# from flair.data import TaggedCorpus

import os, argparse
from flair.data import Corpus


from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings, FlairEmbeddings
from typing import List



parser = argparse.ArgumentParser(description='Get GUM data')
parser.add_argument('--corpus', '-c',default='gum5', choices=['gum5', 'ace2005'],
                    help='which corpus we are using, gum5 or ace2005')
parser.add_argument('--epochs', '-e',default=150, type=int,
                    help='maximum number of epochs')
parser.add_argument('--size', '-s',default=0.1, type=float,
                    help='downsize the corpus by how much')
parser.add_argument('--node', '-n',default='gpu', choices=['gpu', 'cpu', 'none'],
                    help='train on cpu or gpu')


args = parser.parse_args()



# 1. get the corpus
#corpus: TaggedCorpus = NLPTaskDataFetcher.load_corpus(NLPTask.CONLL_03,base_path="gum_slim").downsample(0.1)
# cols = {0: 'text', 1: 'pos', 2: 'func', 3: 'ent', 4: 'coref', 5: 'genre', 6: 'stype', 7:'subord',8:'ortho1',9: 'ortho2',10:'label'}
#corpus: TaggedCorpus = NLPTaskDataFetcher.load_corpus("conll_03",base_path="gum_slim")#.downsample(0.1)

# DONE: in flair's data_fetcher.py, add a corpus type:
#        if task == "gum_ent":  # AZ
#           columns = {0: 'text', 1: 'pos', 2: 'np', 3: 'ner'}
#           return NLPTaskDataFetcher.load_column_corpus(data_folder, columns, tag_to_biloes='ner')



# corpus: TaggedCorpus = NLPTaskDataFetcher.load_corpus("gum_ent",base_path="gum_slim")#.downsample(0.1)

corpus: Corpus = NLPTaskDataFetcher.load_corpus(args.corpus,base_path=os.path.normpath('./data/autoslim/')).downsample(args.size)
# corpus: Corpus = NLPTaskDataFetcher.load_corpus(os.path.normpath('./data/autoslim/gum5/'))#.downsample(0.1)


print(corpus)

# 2. what tag do we want to predict?
tag_type = 'ner'

# 3. make the tag dictionary from the corpus
tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)
print(tag_dictionary.idx2item)

# 4. initialize embeddings
embedding_types: List[TokenEmbeddings] = [

    WordEmbeddings('glove'),

    # comment in this line to use character embeddings
    # CharacterEmbeddings(),

    # comment in these lines to use flair embeddings
    FlairEmbeddings('news-forward'),
    FlairEmbeddings('news-backward'),
]

embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

# 5. initialize sequence tagger
from flair.models import SequenceTagger

tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                        embeddings=embeddings,
                                        tag_dictionary=tag_dictionary,
                                        tag_type=tag_type,
                                        use_crf=True)

# 6. initialize trainer
from flair.trainers import ModelTrainer

trainer: ModelTrainer = ModelTrainer(tagger, corpus)

# 7. start training
trainer.train('resources/taggers/example-ner',
              learning_rate=0.1,
              mini_batch_size=32,
              max_epochs=args.epochs,
              embeddings_storage_mode=args.node)




# 8. plot training curves (optional)
# from flair.visual.training_curves import Plotter
# plotter = Plotter()
# plotter.plot_training_curves('resources/taggers/example-ner/loss.tsv')
# plotter.plot_weights('resources/taggers/example-ner/weights.txt')