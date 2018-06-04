#-*-encoding:utf-8-*-

import sys,json,re

def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

def replacenth(string, sub, wanted, n):
	where = [m.start() for m in re.finditer(sub, string)][n-1]
	before = string[:where]
	after = string[where:]
	after = after.replace(sub, wanted, 1)
	newString = before + after
	return newString

def getBracketSentence(sen, wordO, neO, morphO):

	ret = []

	checked = 0
	for word in wordO:    # word가 개체명보다 크니까 먼저 loop!
		word['text'] = word['text']
		word['begin'] = int(word['begin'])
		word['end'] = int(word['end'])
		isNe = False
		neText = word['text']
		
		for ne in neO:    
			if word['begin'] > ne['end']: continue    # 지금 단어가 개체명보다 뒤에 있으면 다음 개체명 보기 
			elif word['end'] < ne['begin']: break     # 지금 단어가 개체명보다 앞에 있으면 다음 단어 보기 
			ne_str = ne['text']    # 개체명
			ne_type = ne['type']    # 태그
			if word['begin'] <= ne['begin'] and word['end'] >= ne['end']:    # 지금 보고 있는 단어가 개체명일 때
				#한 번 나타나면 바로 치환 가능
				if word['text'].count(ne_str)==1:
					neText = neText.replace(ne_str, '<%s:%s>'%(ne_str, ne_type))
				#여러번 나타날 때, 시작위치가 같으면 최초 1회만 치환
				elif word['begin'] == ne['begin']:
					neText = neText.replace(ne_str, '<%s:%s>'%(ne_str, ne_type), 1)
				elif word['end'] == ne['end']: #끝 위치가 같으면 마지막 1회만 치환
					neText = rreplace(neText, ne_str, '<%s:%s>'%(ne_str, ne_type), 1)
				else: #여러번인데 가운데 일 때. 최초 1회만 치환(기존에 NE인 것은 하지 않는다.)
					count = 0
					indices = [0]
					i = 1
					while 1:
						try:
							indices.append(neText.index(ne_str, indices[-1]+1))
							count += 1
						except Exception as e:
							break
					if len(indices)==1:
						i = 0
						pass
					else:
						neIndex = indices[i]
						while neText[neIndex-1]=='<': #개체명 바로 앞 문자가 꺽쇠면
							i+=1
							if i == count: break
							neIndex = indices[i]
					neText = replacenth(neText, ne_str, '<%s:%s>'%(ne_str, ne_type), i)
				isNe = True
				checked = 0
			elif word['begin'] <= ne['begin'] and word['end'] < ne['end']: #ne가 시작될 때. 개체명이 한 어절 이상일 
				if ' ' in ne_str:
					nestr = ne_str.split()[0]
					if nestr in word['text']:
						neText = rreplace(neText, nestr, '<%s'%(nestr),1)
						checked += 1
						isNe = True
				else:
					neText = neText.replace(ne_str, '<%s'%(ne_str))
			elif word['begin'] > ne['begin'] and word['end'] >= ne['end']: #ne가 끝날 떄.
				if ' ' in ne_str:
					for el in ne_str.split()[checked:]:
						if el in word['text']:
							neText = neText.replace(el, '%s:%s>'%(el, ne_type))
							checked += 1
							break
				else:
					neText = neText.replace(ne_str, '%s:%s>'%(ne_str, ne['type']))
				isNe = True
				checked = 0
		
		if not isNe:
			ret.append(word['text'])
		else:
			ret.append(neText)

	return '$%s'%' '.join(ret)

def getMorphs(wordO, morphO):
	mBegin = int(word['begin'])
	mEnd = int(word['end'])
	morphs = []
	for morphIndex in range(mBegin, mEnd+1):
		morph = morphO[morphIndex]
		morphs.append({'lemma':morph['lemma'], 'mid':morph['id'], 'pos':morph['type'], 'wid':wordO['id']+1})
	return morphs

def appendNEs(morphs, neO):
	for aMorph in morphs:
		for aNe in neO:
			if aNe['begin'] <= aMorph['mid'] and aNe['end'] >= aMorph['mid']:
				if aNe['begin'] == aMorph['mid']:
					aMorph['ne'] = 'B-%s'%aNe['type']
				else:
					aMorph['ne'] = 'I-%s'%aNe['type']
	for aMorph in morphs:
		if not 'ne' in aMorph:
			aMorph['ne'] = 'O'

	return morphs

if __name__=='__main__':
	if len(sys.argv)==1:
		print (sys.argv[0], 'INPUT_CORPUS')
		sys.exit(0)

	jO = json.loads(open(sys.argv[1], encoding='utf-8').read())

	sens = jO['sentence']

	for sen in sens:
		#print ('; %s' % (sen['text']))
		#print (getBracketSentence(sen['text'], sen['word'], sen['NE'], sen['morp']))
		for word in sen['word']:
			morphs = getMorphs(word, sen['morp'])
			morphs = appendNEs(morphs, sen['NE'])
			for morph in morphs:
				lemma = morph['lemma']
				ne = morph['ne']
				wid = morph['wid']
				pos = morph['pos']
				#print ('%s\t%s\t%s\t%s' % (wid, lemma, pos, ne))
				print('%s/%s %s' % (lemma, pos, ne))
		print()
