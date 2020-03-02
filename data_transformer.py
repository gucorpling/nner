import io, os, nltk, re, argparse, glob
from collections import defaultdict
# import stanfordnlp


os.chdir('.')

parser = argparse.ArgumentParser(description='Get GUM data')
parser.add_argument('--inputformat', '-i',default='tsv', choices=['tsv', 'ace', 'autoconllu', 'goldconllu'],
                    help='input format of GUM')
parser.add_argument('--outputformat', '-o',default='ace', choices=['goldslim', 'autoslim', 'ace', 'xml', 'autoconllu'],
                    help='output format of GUM')
parser.add_argument('--corpus', '-c',default='gum5', choices=['gum5', 'ace2005'],
                    help='which corpus we are using, gum5 or ace2005')

parser.add_argument('--datadir', '-d',default=os.path.normpath(r'./data/'),
                    help='where the entire datadir is located')
parser.add_argument('--sourcedir', '-s',default=os.path.normpath(r'../../../../GUM/amir_gumdev/_build/src/'),
                    help='where the source gum directory is located')


# Logan's relative path for sourcedir of GUM:  os.path.normpath(r'../../../../GUM/amir_gumdev/_build/src/')
# Logan's relative path to GUM in ace format: os.path.normpath(r'../data/ace/gum5/')

args = parser.parse_args()


# listtrain = io.open(os.path.join(args.datadir, 'split', 'gum5', 'files.train'), 'r', encoding='utf8').read().strip().split('\n')
# listdev = io.open(os.path.join(args.datadir, 'split', 'gum5', 'files.dev'), 'r', encoding='utf8').read().strip().split('\n')
# listtest = io.open(os.path.join(args.datadir, 'split', 'gum5', 'files.test'), encoding='utf8').read().strip().split('\n')


listtrain = io.open(os.path.join(args.datadir, 'split', 'gum5_testnoreddit', 'files.train.txt'), 'r', encoding='utf8').read().strip().split('\n')
listdev = io.open(os.path.join(args.datadir, 'split', 'gum5_testnoreddit', 'files.dev.txt'), 'r', encoding='utf8').read().strip().split('\n')
listtest = io.open(os.path.join(args.datadir, 'split', 'gum5_testnoreddit', 'files.test.txt'), encoding='utf8').read().strip().split('\n')






def GUMfilename2splitset(f):
    base =  os.path.splitext(os.path.basename(f))[0]
    if base in listtrain:
        return 'train'
    elif base in listdev:
        return 'dev'
    elif base in listtest:
        return 'test'
    else:
        raise Exception('filename not in GUM5')


def makedirifnotexist(f):
    if not os.path.exists(f):
        os.makedirs(f)

def removefilesindir(f):
    for f in glob.glob(os.path.join(f, '*')):
        if os.path.isfile(f):
            os.remove(f)


def concatgoldconllu():
    removefilesindir(os.path.join(args.datadir, 'goldconllu', args.corpus))
    for one_f in  sorted(glob.glob(os.path.join(args.datadir, 'goldconllu', args.corpus, 'not-to-release', '*.conllu'))):
        one_lines = io.open(one_f, 'r', encoding='utf8').read().replace('\r','').strip()
        one_lines = re.sub(r'#[^\t\n]+\n(\n*)', r'\1', one_lines)

        io.open(os.path.join(args.datadir, 'goldconllu', args.corpus, args.corpus + '.' + GUMfilename2splitset(one_f)), 'a', encoding='utf8').write(one_lines+'\n\n')




def gethead(entities, dependencies):

    """

    :param entities:
    :param dependencies:
    :return:
    """
    assert len(entities) == len(dependencies)

    slims = [[] for i in range(len(dependencies))]
    non_ideal_head_count = 0


    # set default slim to O
    for sent_id in range(len(dependencies)):
        for tok_id in range(len(dependencies[sent_id])):
            slims[sent_id].append([dependencies[sent_id][tok_id][1], dependencies[sent_id][tok_id][4], dependencies[sent_id][tok_id][7], 'O'])


    for sent_id in range(len(entities)):
        for ent in entities[sent_id]:
            ent_start, ent_end, ent_type = ent

            # filter tokens in dependencies
            toks_in_ent = [x for x in dependencies[sent_id] if int(x[0])-1>=ent_start and int(x[0])-1<ent_end]
            head = [x for x in toks_in_ent if (int(x[6]) == 0 or (int(x[6])-1>=0 and int(x[6])-1<ent_start) or int(x[6])-1>=ent_end) and x[7]!='punct']

            if len(head) != 1:
                non_ideal_head_count += 1


            if len(head) > 1:
                # simple version: arbitrarily choosing the rightmost
                head = head[-1:]
            elif len(head) == 0:
                # remove the condition that head cannot be punct
                head = [x for x in toks_in_ent if (int(x[6]) == 0 or (int(x[6]) - 1 >= 0 and int(x[6]) - 1 < ent_start) or int(x[6]) - 1 >= ent_end)]



            # a few fine-grained head filtering processes:
            # if len(head) > 1:
            #
            #     # prioritize clause > argument > others
            #
            #     # clausal
            #     if 'root' in [x[7] for x in head]:
            #         head = [x for x in head if x[7]=='root']
            #
            #     if 'conj' in [x[7] for x in head]:
            #         head = [x for x in head if x[7]=='conj']
            #
            #     elif 'ccomp' in [x[7] for x in head]:
            #         head = [x for x in head if x[7] == 'ccomp']
            #
            #
            #     # arguments
            #     elif 'nsubj' in [x[7] for x in head]:
            #         head = [x for x in head if x[7]=='nsubj']
            #
            #     elif 'obj' in [x[7] for x in head]:
            #         head = [x for x in head if x[7]=='obj']
            #
            #
            #     elif 'appos' in [x[7] for x in head]:
            #         head = [x for x in head if x[7]=='appos']
            #
            #
            #     elif 'nmod' in [x[7] for x in head]:
            #         head = [x for x in head if x[7]=='nmod']
            #
            #     elif 'obl' in [x[7] for x in head]:
            #         head = [x for x in head if x[7] == 'obl']
            #
            #         ## remove verbal modifiers
            #         head = [x for x in head if not x[4].startswith('V')]
            #
            #     if len(head) > 1:
            #         ## choose only one from SAME deprels
            #         for i in head[1:]:
            #             if i[6] == head[0][6]:
            #                 head.remove(i)
            #
            #


            assert len(head) == 1

            slims[sent_id][int(head[0][0])-1][3] = 'B-%s' % (ent_type)

    print(in_f, 'arbitrary head decision due to improper auto UD parse', non_ideal_head_count)

    return slims




def fromtsv(f):
    if isinstance(f, str):
        lines = io.open(f, 'r', encoding='utf8').read().replace('\r', '').strip().split('\n')
    elif isinstance(f, list):
        lines = f

    tokens = []
    entities = []
    fakeid = 10000

    for line_id, line in enumerate(lines):
        if '\t' in line:
            fields = line.strip().split('\t')
            tok_id = int(fields[0].split('-')[1])-1
            sent_id = int(fields[0].split('-')[0])-1

            if tok_id == 0:
                curr_sent = sent_id
                line_tokens = []
                line_entity_dict = defaultdict(lambda: [9999, 0, ''])

            line_tokens.append(fields[2])

            if fields[3] != '_':
                tok_entities = [re.split('[\[\]]', x.strip()) for x in fields[3].strip().split('|')]
                for ent in tok_entities:
                    if len(ent) == 1:
                        line_entity_dict[fakeid] = [tok_id, tok_id+1, ent[0]]
                        fakeid += 1
                    else:
                        if line_entity_dict[ent[1]][0] > tok_id:
                            line_entity_dict[ent[1]][0] = tok_id
                            if line_entity_dict[ent[1]][2] == '':
                                line_entity_dict[ent[1]][2] = ent[0]

                        if line_entity_dict[ent[1]][1] <= tok_id:
                            line_entity_dict[ent[1]][1] = tok_id+1
                            if line_entity_dict[ent[1]][2] == '':
                                line_entity_dict[ent[1]][2] = ent[0]

        if line=='' or line_id == len(lines)-1:
            if line_id == len(lines)-1:
                print()
            try:
                tokens.append(line_tokens)
                entities.append(list(line_entity_dict.values()))
                line_tokens = []
                line_entity_dict = defaultdict(lambda: [9999, 0, ''])


            except:
                pass


    return tokens, entities





def fromace(f):
    if isinstance(f, str):
        lines = io.open(f, 'r', encoding='utf8').read().replace('\r', '').split('\n')
    elif isinstance(f, list):
        lines = f

    tokens = []
    entities = []

    for i in range(len(lines)//3):
        line_tokens = lines[3*i].split()
        line_entities = [re.split('[, ]', x.strip()) for x in lines[3*i+1].strip().split('|')]
        if line_entities[0] == ['']:
            line_entities = []
        else:
            line_entities = [[int(x[0]), int(x[1]), x[2]] for x in line_entities]
        line_entities = sorted(line_entities, key=lambda x: (x[0], x[1]))
        tokens.append(line_tokens)
        entities.append(line_entities)


    return tokens, entities




def fromconllu(f):
    if isinstance(f, str):
        lines = io.open(f, 'r', encoding='utf8').read().replace('\r', '').strip()
        dependencies = [x.split('\n') for x in re.split(r'\n\n+', lines)]
    elif isinstance(f, list):
        dependencies = f

    # remove non-tab sentences
    for sent in dependencies:
        for tok in sent:
            if '\t' not in tok:
                sent.remove(tok)

    # split by tab
    # remove non-tab sentences
    for sent_id in range(len(dependencies)):
        for tok_id in range(len(dependencies[sent_id])):
            dependencies[sent_id][tok_id] = dependencies[sent_id][tok_id].split('\t')
            assert len(dependencies[sent_id][tok_id]) == 10

    while [] in dependencies:
        dependencies.remove([])

    return dependencies



def toace(tokens, entities, f):
    with io.open(f, 'a', encoding='utf8') as fout:
        assert len(tokens) == len(entities)
        for line_id in range(len(tokens)):
            fout.write(' '.join(tokens[line_id])+'\n')
            fout.write('|'.join(['%d,%d %s' % (x[0], x[1], x[2]) for x in entities[line_id]])+'\n\n')



def toxml(tokens, entities, f):
    with io.open(f, 'a', encoding='utf8') as fout:
        assert len(tokens) == len(entities)
        for line_id in range(len(tokens)):
            for tok_id in range(len(tokens[line_id])):
                if tok_id == 0:
                    fout.write('<s>\n')

                for ent in [x for x in entities[line_id] if x[0]==tok_id]:
                    fout.write('<entity entity="%s">\n' % (ent[2]))

                fout.write('%s\n' % (tokens[line_id][tok_id]))

                for ent in [x for x in entities[line_id] if x[1]-1 == tok_id]:
                    fout.write('</entity>\n')

                if tok_id == len(tokens[line_id]) - 1:
                    fout.write('</s>\n')



def toconllu(tokens, entities, conllu_f):
    doc = nlp("\n".join([' '.join(x) for x in tokens]))
    conllu_output = doc.conll_file.conll_as_string()
    with io.open(conllu_f, 'a', encoding='utf8') as fout:
        fout.write(conllu_output)




def toslim(entities, dependencies, slim_f):


    slims = gethead(entities, dependencies)

    with io.open(slim_f, 'a', encoding='utf8') as fout:
        fout.write("-DOCSTART- -X- -X- O\n\n")

        for sent in slims:
            fout.write('\n'.join([' '.join(x) for x in sent])+'\n\n')





if __name__ == "__main__":
    if args.inputformat == 'ace' and args.outputformat == 'xml':
        outputdir = os.path.join(args.datadir, 'xml', args.corpus)
        makedirifnotexist(outputdir)
        removefilesindir(outputdir)

        for in_f in sorted(glob.glob(os.path.join(args.datadir, 'ace', args.corpus, '*'))):
            tokens, entities = fromace(in_f)
            toxml(tokens,entities,os.path.join(outputdir, os.path.basename(in_f)))

        print('o Done! Check %s for outputs.' % (outputdir))




    elif args.inputformat == 'tsv' and args.outputformat == 'xml' and args.corpus == 'gum5':
        outputdir = os.path.join(args.datadir, 'xml', args.corpus)
        makedirifnotexist(outputdir)
        removefilesindir(outputdir)

        # for in_f in sorted(glob.glob(args.datadir + os.sep +  '*')):
        for in_f in sorted(glob.glob(os.path.join(args.sourcedir, 'tsv', '*'))):
            tokens, entities = fromtsv(in_f)
            toxml(tokens,entities, os.path.join(outputdir, args.corpus+'.'+GUMfilename2splitset(in_f)))

        print('o Done! Check %s for outputs.' % (outputdir))





    elif args.inputformat == 'tsv' and args.outputformat == 'ace' and args.corpus == 'gum5':
        outputdir = os.path.join(args.datadir, 'ace', args.corpus)
        makedirifnotexist(outputdir)
        removefilesindir(outputdir)

        # for in_f in sorted(glob.glob(args.datadir + os.sep +  '*')):
        for in_f in sorted(glob.glob(os.path.join(args.sourcedir, 'tsv', '*'))):
            tokens, entities = fromtsv(in_f)
            toace(tokens,entities, os.path.join(outputdir, args.corpus + '.'+GUMfilename2splitset(in_f)))

        print('o Done! Check %s for outputs.' % (outputdir))




    elif args.inputformat == 'ace' and args.outputformat == 'autoconllu':

        config = {
            'processors': 'tokenize,mwt,pos,lemma,depparse',
            'tokenize_pretokenized': True
        }
        nlp = stanfordnlp.Pipeline(**config)



        conllu_outputdir = os.path.join(args.datadir, 'autoconllu', args.corpus)

        makedirifnotexist(conllu_outputdir)

        removefilesindir(conllu_outputdir)


        for in_f in sorted(glob.glob(os.path.join(args.datadir, 'ace', args.corpus, '*'))):
            tokens, entities = fromace(in_f)
            toconllu(tokens,entities,os.path.join(conllu_outputdir, os.path.basename(in_f)))

        print('o Done! Check %s for outputs.' % (conllu_outputdir))


    elif args.inputformat == 'autoconllu' and args.outputformat == 'autoslim':
        slim_outputdir = os.path.join(args.datadir, 'autoslim', args.corpus)
        makedirifnotexist(slim_outputdir)
        removefilesindir(slim_outputdir)

        for in_f in sorted(glob.glob(os.path.join(args.datadir, 'autoconllu', args.corpus, '*'))):
            dependencies = fromconllu(in_f)
            _, entities = fromace(os.path.join(args.datadir, 'ace', args.corpus, os.path.basename(in_f)))

            toslim(entities, dependencies, os.path.join(slim_outputdir, os.path.basename(in_f)))

        print('o Done! Check %s for outputs.' % (slim_outputdir))


    elif args.inputformat == 'goldconllu' and args.outputformat == 'goldslim' and args.corpus == 'gum5':
        slim_outputdir = os.path.join(args.datadir, 'goldslim', args.corpus)
        makedirifnotexist(slim_outputdir)
        removefilesindir(slim_outputdir)

        # concatenate gold conllu files
        concatgoldconllu()




        for in_f in sorted(glob.glob(os.path.join(args.datadir, 'goldconllu', args.corpus, '*'))):
            if os.path.isfile(in_f):
                dependencies = fromconllu(in_f)
                _, entities = fromace(os.path.join(args.datadir, 'ace', args.corpus, os.path.basename(in_f)))

                toslim(entities, dependencies, os.path.join(slim_outputdir, os.path.basename(in_f)))

        print('o Done! Check %s for outputs.' % (slim_outputdir))









    else:
        raise Warning('Wrong arg inputs!\n No data transformation took place.')















