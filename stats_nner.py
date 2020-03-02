import os, io, re, argparse
from collections import defaultdict


def reader(d, f):
	lines = io.open(datadir + d + os.sep + d + '.' + f, 'r', encoding='utf8').read().replace('\r','').split('\n')

	tot = 0

	for lid, line in enumerate(lines):
		if lid % 3 == 0:
			freqdict[d+'.'+f]['tok'] += len(line.strip().split())
		elif lid %3 == 2:
			freqdict[d+'.'+f]['line'] += 1
		elif line!='':
			entities = line.strip().split('|')
			tot += len(entities)
			entities = [re.split('[, ]', x) for x in entities]



			# with sorted tuple
			entities = [[int(x[0]), int(x[1]), x[2], 1] for x in entities]
			entities = sorted(entities, key=lambda x: (x[0], -x[1]))

			if len(entities)>1:
				for ie in range(1, len(entities)):
					if lid==5365 and ie==7:
						print()
					for previe in range(ie-1, -1, -1):
						if entities[ie][0] == entities[previe][0] and entities[ie][1] == entities[previe][1]:
							entities[ie][3] = entities[previe][3]
							print("Repeated entities: ", d, f, lid, entities[previe], entities[ie])
							freqdict[d + '.' + f]['repeated'] += 1
							break

						elif entities[ie][1] <= entities[previe][1]:
							entities[ie][3] = entities[previe][3]+1
							break


						if entities[previe][0]<entities[ie][0] and entities[ie][0] < entities[previe][1] and entities[previe][1]<entities[ie][1]:
							print("Overlapping entities: ", d, f, lid, entities[previe], entities[ie])
							break


			for e in entities:
				if e[3] >= 5:
					print("Deep nesting: ", d, f, lid, e, entities)

				freqdict[d + '.' + f]['length' + str(e[1] - e[0]) + 'ent'] += 1
				freqdict[d + '.' + f]['level' + str(e[3]) + 'ent'] += 1
				freqdict[d+'.'+f]['totalent'] += 1


	print(tot)













			# older method
			# entities = [[int(x[0]), int(x[1]), x[2]] for x in entities]
			#
			# for e in entities:
			# 	freqdict[d+'.'+f]['length'+str(e[1]-e[0])+'ent'] += 1
			# 	parents = [x for x in entities if (x[0]<=e[0] and x[1]>=e[1] and x!=e)]
			# 	freqdict[d+'.'+f]['level'+str(len(parents)+1)+'ent'] += 1
			# 	freqdict[d+'.'+f]['totalent'] += 1
			#
			# 	# error detection
			# 	errors = [x for x in entities if (x[0]<e[0] and x[1]<e[1] and e[0]<x[1] and e!=x)]
			# 	if len(errors)>0:
			# 		freqdict[d+'.'+f]['errorent'] += 1
			# 		print("Problematic entities: ", d,f,lid, e, errors)
			#



if __name__ == "__main__":

	os.chdir('.')
	#
	# parser = argparse.ArgumentParser()
	# parser.add_argument('--dataset', '-d', default='ace2005', choices=['ace2005', 'gum5'], help='Input dataset')
	# args = parser.parse_args()

	# print('0 Processing dataset ' + args.dataset)

	datadir = os.path.normpath(r'./data/ace/') + os.sep

	freqdict = defaultdict(lambda: defaultdict(int))


	reader('ace2005', 'train')
	reader('ace2005', 'dev')
	reader('ace2005', 'test')
	reader('gum5', 'train')
	reader('gum5', 'dev')
	reader('gum5', 'test')

	keys = set()
	for v in freqdict.values():
		keys = keys.union(set(v.keys()))
	keys = sorted(list(keys))

	fstat = io.open(r'stats_nner.tsv', 'w', encoding='utf8')
	fstat.write('\t'.join(['data']+keys)+'\n')
	for c in ['ace2005', 'gum5']:
		for s in ['train', 'dev', 'test']:
			fstat.write(c+'.'+s+'\t'+'\t'.join([str(freqdict[c+'.'+s][x]) for x in keys])+'\n')
	fstat.close()


	print('DONE!')



	



