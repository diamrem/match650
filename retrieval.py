import sys
import csv
import os
import string
import lucene
from lucene import *
from update_index import *
#INDEX_DIR = "Tmp/REMOVEME.index-dir"
INDEX_DIR = "Tmp/preprocess_aff.index-dir"
STUDENT_PATH = "getData/student_data/"
MAX = 10
output = ""

def write_to_file(*args):
#each parameter will be split by \n
	global output

	for arg in args:
		print arg
		output+=arg
		output += "\n"
	
def explain_score(searcher, docID, query):
#returns the explanation object for a given
#query (student), docID(professor)
    explanation = searcher.explain(query, docID)
    write_to_file("Explanation Dump: ",explanation.toString())
    return explanation

def initial_searcher():
    lucene.initVM()
    indexDir = INDEX_DIR 
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_30)
    searcher = IndexSearcher(dir)
    return searcher, analyzer

def getQueryList(student,fieldList):
#fieldList is list of fields we want to use for scoring
#student is dictionary of student_profile info
#REQUIRES: student_profile must have interest and affiliation information
#EFF: returns a MultiFieldQuery object
    queryList = []
    for field in fieldList:
        fieldValue = ""
        if (student.get(field)):
            fieldValue = student[field]
        queryList.append(fieldValue)
    return queryList

def search_by_student(student, analyzer, searcher,fieldList):
    queries = getQueryList(student,fieldList) 
    query = MultiFieldQueryParser(Version.LUCENE_35,fieldList,analyzer).parse(Version.LUCENE_35,queries,fieldList,analyzer)
    hits = searcher.search(query, MAX)

    for hit in hits.scoreDocs:
        write_to_file(str(hit.score))
        doc = searcher.doc(hit.doc)
        write_to_file(doc.get("name"))
        write_to_file(doc.get("interest"))
        write_to_file('...................','...................')
        explain_score(searcher, hit.doc,query)

if __name__ == "__main__":
#cmd line:	python retrieval [resultFile] [fields]
#			python retrieval v3Explain.txt interest processed_aff
    searcher, analyzer = initial_searcher()
    file_list = os.listdir(STUDENT_PATH)
    fieldList = sys.argv[2:]
    
    resultName = sys.argv[1]
    resultFile = open(sys.argv[1],"w")
    hLine = '___________________________'

    for f in os.listdir(STUDENT_PATH):
        print 'opening', STUDENT_PATH + f
        reader = csv.reader(open(STUDENT_PATH + f, 'r'), delimiter=',', quotechar='"')
        for line in reader:
            student_profile = {}
            student_profile['name'] = line[0]
            student_profile['interest'] = line[1]
            student_profile['affiliation'] = line[2]
            student_profile['processed_aff'] = " ".join(rebuild_affiliation(line[2]))
            write_to_file('SEARCHING '+student_profile['name'])
            write_to_file('INTERESTS ARE '+student_profile['interest'])
            write_to_file('AFFILIATION IS '+student_profile['affiliation'])
            write_to_file('.......')
            write_to_file('RESULT IS:')
            search_by_student(student_profile, analyzer, searcher,fieldList)
            write_to_file(hLine,hLine,hLine)

    resultFile.write(output.encode("utf-8"))
    

