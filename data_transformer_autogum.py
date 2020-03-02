import io, os, re, argparse, glob
from collections import defaultdict
# import stanfordnlp


os.chdir('.')

parser = argparse.ArgumentParser(description='Get GUM data')
parser.add_argument('--inputformat', '-i',default='tsv', choices=['tsv'],
                    help='input format of GUM')
parser.add_argument('--outputformat', '-o',default='ace', choices=['ace'],
                    help='output format of GUM')

parser.add_argument('--datadir', '-d',default=os.path.normpath(r'./data/'),
                    help='where the entire datadir is located')

# /Users/loganpeng/Dropbox/Fall_2019/RA_Amir/NNER/nested-ner-2019-bert/data

parser.add_argument('--sourcedir', '-s',default=os.path.normpath(r'./data/GUM6tsv/'),
                    help='where the source directory is located')

parser.add_argument('--mode', '-m',default='train-dev-test', choices=['train-dev-test', 'test'],
                    help='where the source directory is located')


# /Users/loganpeng/Dropbox/GUM/gumby/
# os.path.normpath(r'../../../../GUM/amir_gumdev/_build/src/')

args = parser.parse_args()


def makedirifnotexist(f):
    if not os.path.exists(f):
        os.makedirs(f)


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






def toace(tokens, entities, f):
    with io.open(f, 'a', encoding='utf8') as fout:
        assert len(tokens) == len(entities)
        for line_id in range(len(tokens)):
            fout.write(' '.join(tokens[line_id])+'\n')
            fout.write('|'.join(['%d,%d %s' % (x[0], x[1], x[2]) for x in entities[line_id]])+'\n\n')





if __name__ == "__main__":
    assert args.inputformat == 'tsv' and args.outputformat == 'ace'


    
    if args.mode == 'train-dev-test':
        makedirifnotexist(os.path.join(args.datadir, 'gum6'))
    
        listdev = io.open(os.path.join(args.datadir, 'split', 'gum6_allnewintrain', 'files.dev'), 'r',
                          encoding='utf8').read().strip().split('\n')
        listtest = io.open(os.path.join(args.datadir, 'split', 'gum6_allnewintrain', 'files.test'),
                           encoding='utf8').read().strip().split('\n')
        
        globresults = sorted(glob.glob(os.path.join(args.sourcedir, '*.tsv')))


        trainfile = os.path.join(args.datadir, 'gum6', 'gum6.train')
        devfile = os.path.join(args.datadir, 'gum6', 'gum6.dev')
        testfile = os.path.join(args.datadir, 'gum6', 'gum6.test')

        if os.path.isfile(trainfile):
            os.remove(trainfile)
        if os.path.isfile(testfile):
            os.remove(testfile)
        if os.path.isfile(devfile):
            os.remove(devfile)

        for f in globresults:
            basenamenoext = os.path.basename(f).replace('.tsv', '')
            
            tokens, entities = fromtsv(f)

            if basenamenoext in listdev:
                toace(tokens,entities, devfile)
            if basenamenoext in listtest:
                toace(tokens, entities, testfile)
            else:
                toace(tokens, entities, trainfile)
        
        

    elif args.mode == 'test':
        # corpora = ['GUM_test_webannotsv_xrenner', 'GUMBY_sample_webannotsv_gold', 'GUMBY_sample_webannotsv_xrenner']
        # corpora = ['gum_xrenner_shibuya_tsv','gum_xrenner_no_shibuya_tsv', 'autogum_xrenner_shibuya_tsv', 'autogum_xrenner_no_shibuya_tsv']
        corpora = ['xrenner_autogum_entities_tsv', 'xrenner_gumtest_entities_tsv']
        corpora = ['gold', 'submission']
    
        for corpus in corpora:
            
            outputfile = os.path.join(args.datadir, corpus, corpus + '.test' )
    
    
            makedirifnotexist(os.path.join(args.datadir, corpus))
            if os.path.isfile(outputfile):
                os.remove(outputfile)
    
            # for in_f in sorted(glob.glob(args.datadir + os.sep +  '*')):
            for in_f in sorted(glob.glob(os.path.join(args.sourcedir, corpus, '*'))):
                tokens, entities = fromtsv(in_f)
                toace(tokens,entities, outputfile)
    
            print('o Done! Check %s for outputs.' % (outputfile))

