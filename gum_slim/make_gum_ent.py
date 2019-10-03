import io, os, sys, re
from glob import glob


# TODO: add reddit to splits
dev_files = ["GUM_interview_peres","GUM_interview_cyclone","GUM_interview_gaming",
			   "GUM_news_iodine","GUM_news_defector","GUM_news_homeopathic",
			   "GUM_voyage_athens","GUM_voyage_isfahan","GUM_voyage_coron",
			   "GUM_whow_joke","GUM_whow_skittles","GUM_whow_overalls",
			   "GUM_fiction_beast","GUM_bio_emperor","GUM_academic_librarians",
			   "GUM_fiction_lunre","GUM_bio_byron","GUM_academic_exposure"]
test_files = ["GUM_interview_mcguire","GUM_interview_libertarian","GUM_interview_hill",
			   "GUM_news_nasa","GUM_news_expo","GUM_news_sensitive",
			   "GUM_voyage_oakland","GUM_voyage_thailand","GUM_voyage_vavau",
			   "GUM_whow_mice","GUM_whow_cupcakes","GUM_whow_cactus",
			   "GUM_fiction_falling","GUM_bio_jespersen","GUM_academic_discrimination",
			   "GUM_academic_eegimaa","GUM_bio_dvorak","GUM_fiction_teeth"]


gum_root = "/"  # PATH TO GUM ROOT HERE
enti_dep_path = gum_root + os.sep.join(['_build', 'utils', 'pepper', 'tmp',"entidep",'*.conll10'])

files = glob(enti_dep_path)

train = []
dev = []
test = []
output = []

for file_ in files:
	docname = os.path.basename(file_).replace(".conll10","")
	lines = io.open(file_,encoding="utf8").read().strip().split("\n")
	output.append("-DOCSTART- -X- -X- O")
	output.append("")
	for line in lines:
		if "\t" in line:
			fields=line.split()
			label = "O"
			if "ent_head" in fields[5]:
				label = fields[5].split("|")[0]
				label = label.split("=")[1]
				label = "B-" + label
			outline = " ".join([fields[1],fields[3],fields[7],label])
			output.append(outline)
		elif len(line) == 0:
			output.append("")

	output.append("")

	if docname in dev_files:
		dev += output
	elif docname in test_files:
		test += output
	else:
		train += output
	output = []




with io.open("dev.txt",'w',encoding="utf8",newline="\n") as f:
	f.write("\n".join(dev) + "\n")
with io.open("test.txt",'w',encoding="utf8",newline="\n") as f:
	f.write("\n".join(test) + "\n")
with io.open("train.txt",'w',encoding="utf8",newline="\n") as f:
	f.write("\n".join(train) + "\n")


# TODO: move generated files to ./gum_ent/