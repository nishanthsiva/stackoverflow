import requests
import json
import time
import re
import os
import csv
from bs4 import BeautifulSoup as BSHTML

def createMetaFile(question,path):
	mfile_w= open(path+"META_INFO.txt","w");
	mfile_w.write("question_id="+str(question['question_id'])+"\n")
	mfile_w.write("is_answered="+str(question['is_answered'])+"\n")
	mfile_w.write("answer_count="+str(question['answer_count'])+"\n")
	mfile_w.write("post_link="+question['link']+'\n')
	mfile_w.write("tags=")
	for tag in question['tags']:
		mfile_w.write(tag+",")
	mfile_w.write("\n")
	mfile_w.close()

def writeQuestionBody(question, path):
	qFile = open(path+'Question_'+str(question['question_id'])+'.txt','w')
	qFile.write('<title>'+question['title'].encode('utf8')+'</title>')
	qFile.write('<body>'+question['body'].encode('utf8')+'</body>')
	qCodeFile = open(path+'Question_Code_'+str(question['question_id'])+'.txt','w')
	qFile.close()
	BS = BSHTML(question['body'])
	for segment in BS.find_all('code'):
		qCodeFile.write("<code>"+str(segment.get_text().encode('utf8'))+"</code>\n")
	qCodeFile.close()

def writeAnswers(question, path):
	answer_count = 1
	for answer in question['answers']:
		folder_path = path+"Answer_"+str(question['question_id'])+"_"+str(answer_count)+"/"
		if not os.path.exists(os.path.dirname(folder_path)):
   			os.makedirs(os.path.dirname(folder_path))
		aFile = open(folder_path+'Answer_'+str(answer['answer_id'])+".txt",'w')
		aFile.write('<body>'+answer['body'].encode('utf8')+'</body>')
		aFile.close()
		aCodeFile = open(folder_path+'Answer_Code_'+str(answer['answer_id'])+".txt",'w')
		BS = BSHTML(answer['body'])
		for segment in BS.find_all('code'):
			aCodeFile.write("<code>"+str(segment.get_text().encode('utf8'))+"</code>\n")
		aCodeFile.close()
		answer_count += 1

def storeQuestion(question, programming_lang, year):
	folder_path = "vmh-96-share/stack-overflow/Questions/"+str(year)+"/"+programming_lang+"/Question_"+str(question['question_id'])+"/"
	if not os.path.exists(os.path.dirname(folder_path)):
   		os.makedirs(os.path.dirname(folder_path))
	createMetaFile(question, folder_path)	
	writeQuestionBody(question, folder_path)
	writeAnswers(question,folder_path+"/Answers/")
	mfile_w= open(folder_path+"META_INFO_JSON.txt","w");
	if 'answers' in question:
		del question['answers']
	if 'body' in question:
		del question['body']
	json.dump(question, mfile_w)
	mfile_w.close()

def processQuestions(questions,request_So_Far,programming_Lang, year):
	for q in questions:
		request_So_Far=request_So_Far+1
		codeflag=False
		if q['answer_count'] != 0:

			#Checking whether the question contains the code
			if q['body'].find('<code>') !=-1:
				codeflag=True
			#Checking whether the answer contains the code
			if not codeflag:
				for ans in q['answers']:
					if ans['body'].find('<code>')!=-1:
						codeflag=True
						break
			if codeflag:
				storeQuestion(q, programming_Lang, year)

def fetchQuestions(from_Date, to_Date,programming_Lang):
	has_More=True
	page_number = 1
	global request_So_Far
	global request_Limit
	url = ''
	while has_More and request_So_Far < request_Limit:
		request_So_Far=request_So_Far+1
		url="http://api.stackexchange.com/2.2/questions?key=sQVw3PIUoSA)Y5BJL2cWnw((&pagesize=100&fromdate=%d&todate=%d&order=desc&tagged=%s&sort=votes&site=stackoverflow&page=%d&filter=!-*7AsVmzB2CT" %(from_Date,to_Date,programming_Lang,page_number)
		#url="http://api.stackexchange.com/2.2/questions?&key=e1bXudmCMCrJpb1aN0cIFg((&pagesize=100&order=desc&sort=votes&site=stackoverflow&fromdate=%d&todate=%d&page=%d&filter=!-*7AsVmzB2CT"%(from_Date,to_Date,page_number)
		r=requests.get(url)
		time.sleep(0.10)
		response= r.json()
		print "--Quota Remaining " + str(response['quota_remaining']);
		questions= response['items']
		has_More=response['has_more']
		processQuestions(questions,request_So_Far,programming_Lang, 2015)
		page_number += 1
		break
	print programming_Lang
	print response['quota_remaining']
	print request_So_Far
	print has_More
	print page_number
	print url

def main():
	#Calling the API to request
	to_Date=1451606399
	from_Date=1420070400
	programming_Lang = ['java','c','c++','python']
	for lang in programming_Lang:
		fetchQuestions(from_Date,to_Date,lang)

request_Limit=10000
request_So_Far=0
if __name__ == '__main__':
	main()