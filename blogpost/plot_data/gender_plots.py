import sys,csv,re,math
import numpy as np

B=10000

metadata={}
docIdsByYear={}
knownAuthorsByYear={}
docIdsByYearWithKnownAuthor={}
seenDocs={}

genderdict={"f": 0, "m": 1}
roledict={"agent": 0, "patient": 1, "mod": 2, "poss": 3, "speaking": 4, "characters": 5}
data={}


def readmeta(filename):
	seen={}
	with open(filename, 'rb') as f:
		reader = csv.reader(f)
		next(reader)
		for row in reader:
			docid=row[0]
			date=int(row[5])
			authgender=row[7]
			author=row[3]
			title=row[9]
			enumcron=row[8]

			if date not in knownAuthorsByYear:
				knownAuthorsByYear[date]=[]

			if authgender != "u" and docid not in seen:
				knownAuthorsByYear[date].append(docid)
				seen[docid]=1


			metadata[docid]=(date, authgender, title, author)


def read(filenames):
	for filename in filenames:
		with open(filename, 'rb') as f:
			reader = csv.reader(f)
			next(reader)
			for row in reader:
				docid=row[0]
				date=int(row[1])
				gender=row[2]
				role=row[3]
				count=int(row[4])

				authgender='u'
				if docid in metadata:
					(date, authgender, title, author)=metadata[docid]

				if date not in docIdsByYear:
					docIdsByYear[date]=[]
					docIdsByYearWithKnownAuthor[date]=[]

				# skip if character gender is unknown
				if gender == "u":
					continue

				if docid not in seenDocs:
					seenDocs[docid]=1
					docIdsByYear[date].append(docid)
					
					if authgender != 'u':
						docIdsByYearWithKnownAuthor[date].append(docid)

				if docid not in data:
					data[docid]=np.zeros((2,6))

				# multivolume works appear as multiple books with the same docid, so append counts rather than assign
				data[docid][genderdict[gender],roledict[role]]+=count


def resampleAuthorCharacterCounts(year):

	resample=np.random.choice(docIdsByYearWithKnownAuthor[year], len(docIdsByYearWithKnownAuthor[year]))
	counts=np.zeros((2,2))
	for docid in resample:
		(date, authorgender, title, author)=metadata[docid]

		datum=data[docid]

		counts[genderdict[authorgender],0]+=np.sum(datum[0,0:4])
		counts[genderdict[authorgender],1]+=np.sum(datum[1,0:4])

	w_author=counts[0,0]/np.sum(counts[0,])
	m_author=counts[1,0]/np.sum(counts[1,])

	return w_author, m_author


def resampleAuthor(year):

	resample=np.random.choice(knownAuthorsByYear[year], len(knownAuthorsByYear[year]))

	counts=np.zeros(2)
	for docid in resample:
		(date, authorgender, title, author)=metadata[docid]

		counts[genderdict[authorgender]]+=1

	return counts[0]/np.sum(counts)


def resampleNumCharacter(year):

	resample=np.random.choice(docIdsByYear[year], len(docIdsByYear[year]))
	counts=np.zeros(2)
	for docid in resample:
		datum=data[docid]

		counts[0]+=datum[0,5]
		counts[1]+=datum[1,5]

	return counts[0]/np.sum(counts)

def resampleSpeech(year):

	resample=np.random.choice(docIdsByYear[year], len(docIdsByYear[year]))
	counts=np.zeros(2)
	for docid in resample:
		datum=data[docid]

		# only use agent + patient + mod + poss counts
		counts[0]+=datum[0,4]
		counts[1]+=datum[1,4]

	return counts[0]/np.sum(counts)

def resampleTotalCounts(year):

	resample=np.random.choice(docIdsByYear[year], len(docIdsByYear[year]))
	counts=np.zeros(2)
	for docid in resample:
		datum=data[docid]

		# only use agent + patient + mod + poss counts
		counts[0]+=np.sum(datum[0,0:4])
		counts[1]+=np.sum(datum[1,0:4])

	return counts[0]/np.sum(counts)


def resampleYearDouble(year, samplingMethod):
	w_means=[]
	m_means=[]
	for b in range(B):
		(w_mean, m_mean)=samplingMethod(year)
		if not math.isnan(w_mean):
			w_means.append(w_mean)
		if not math.isnan(m_mean):
			m_means.append(m_mean)
		
	print "%s\t%s\t%s" % (year, '\t'.join("%.3f" % x for x in np.percentile(w_means, [2.5, 50, 97.5])), '\t'.join("%.3f" % x for x in np.percentile(m_means, [2.5, 50, 97.5])))


def resampleYear(year, samplingMethod):
	means=[]
	for b in range(B):
		mean=samplingMethod(year)
		means.append(mean)
	print "%s\t%s" % (year, '\t'.join("%.3f" % x for x in np.percentile(means, [2.5, 50, 97.5])))

# ex. Usage: python gender_plots.py fig1_ci filtered_fiction_metadata.csv post22_character_data.csv pre23_character_data.csv 
chart=sys.argv[1]
readmeta(sys.argv[2])
read(sys.argv[3:])

if chart == "fig1_ci":
	for year in range(1800,2008):
		resampleYear(year, resampleTotalCounts)

elif chart == "author_ci":
	for year in range(1800,2008):
		resampleYear(year, resampleAuthor)

elif chart == "speech":
	for year in range(1800,2008):
		resampleYear(year, resampleSpeech)

elif chart == "numcharacter":
	for year in range(1800,2008):
		resampleYear(year, resampleNumCharacter)

elif chart == "authorcharacter":
	for year in range(1800,2008):
		resampleYearDouble(year, resampleAuthorCharacterCounts)

