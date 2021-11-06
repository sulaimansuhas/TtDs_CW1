import xml.etree.ElementTree as xml
import re
from math import log10
from stemming.porter2 import stem
stop_words = open("englishST.txt","r")
chop = lambda x: x[:-1]
stop_words = list(map(chop,stop_words.readlines()))
index={}
def tokenization(text):
    return list(filter(None,re.split("[^a-zA-Z]",text)))
    #possible exception could be to do dates like 16th, or remove them completely

def case_folding(text):
    return text.lower()

def stopping(words,l_o_sw):
    new_words = words
    for i in l_o_sw:
        new_words = list(filter(lambda x: x!=i,new_words))
    return new_words

def stem_list_of_words(l_o_w):
    return list(map(stem,l_o_w))




def add_to_index(text_to_add, doc_no, index):
    bag_of_words = stem_list_of_words(stopping(tokenization(case_folding(text_to_add)),stop_words))
    for i in range(len(bag_of_words)):
        if bag_of_words[i] in index:
            index[bag_of_words[i]][0]+=1
            if doc_no in index[bag_of_words[i]][1]:
                index[bag_of_words[i]][1][doc_no].append(i+1)
            else:
                index[bag_of_words[i]][1][doc_no] = [i+1] #the first occurence of a word in a document will be at the start of the list anyway and then we addpend to it          
        else:
            index[bag_of_words[i]] = [1, {doc_no:[i+1]}]
    return index
tree = xml.parse("collections/trec.sample.xml")
root = tree.getroot()
list_of_all_docs = []
for doc in root:
    text = doc.find('TEXT').text.replace("\n", " ").replace("\t"," ")
    doc_no = doc.find('DOCNO').text
    list_of_all_docs.append(doc_no)
    headline = doc.find('HEADLINE').text.replace("\n", " ").replace("\t"," ")
    index = add_to_index(headline+text, doc_no, index)
    print(doc_no + " DONE")


#print(list(index.keys())[100])
#print(index[list(index.keys())[100]])

def proximity_search(term1,term2,proximity,index):
    set_of_docs = []
    term1docs = index[term1][1]
    term2docs = index[term2][1]
    set1 = set(term1docs.keys())
    set2 = set(term2docs.keys())
    common_docs = list(set1 & set2)
    for i in common_docs:
        list_of_occurences1 = index[term1][1][i]
        list_of_occurences2 = index[term2][1][i]
        for j in list_of_occurences1:
            for k in list_of_occurences2:
                if abs(j - k ) <= int(proximity):
                    set_of_docs.append(i)
                    break
            else:
                continue
            break
    return set_of_docs


def term_search(term,index):
    try:
        [index[term][1].keys()]
    except:
        print("term not found")



def boolean_search(query, index):
    query = re.split("( |\\\".*?\\\"|'.*?')", query)
    query = list(filter(lambda x: x!=""  and x!=" ",query))
    if "AND" in query:
        term1 = query[:query.index('AND')]
        term2 = query[query.index('AND')+1:]
        not_in = 0
        if 'NOT' in term1:
            not_in=1
            if term1[1][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term1[1])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(term1[1])),index)

            if term2[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term2[0])))
               #should I add stop word removal here??
               docs2 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs2 = term_search(stem(case_folding(term2[0])),index)
            #make docs not against a list of total docs which we have to write code to make
        elif 'NOT' in term2:
            not_in=2
            if term2[1][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term2[1])))
               #should I add stop word removal here??
               docs2 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs2 = term_search(stem(case_folding(term2[1])),index)
            
            if term1[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term1[0])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(term1[0])),index)
            #make docs not against a list of total docs which we have to write code to make

        else:
            if term2[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term2[0])))
               #should I add stop word removal here??
               docs2 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs2 = term_search(stem(case_folding(term2[0])),index)
            
            if term1[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term1[0])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(term1[0])),index)
        if not_in == 1:
            docs1 = list((set(list_of_all_docs)-set(docs1)))
        else:
            docs2 = list((set(list_of_all_docs)-set(docs2)))
        
        return list(set(docs1) & set(docs2))
    elif "OR" in query:
        term1 = query[:query.index('OR')]
        term2 = query[query.index('OR')+1:]
        not_in = 0
        if 'NOT' in term1:
            not_in=1
            if term1[1][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term1[1])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(term1[1])),index)

            if term2[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term2[0])))
               #should I add stop word removal here??
               docs2 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs2 = term_search(stem(case_folding(term2[0])),index)
            
            #make docs not against a list of total docs which we have to write code to make
        elif 'NOT' in term2:
            not_in=2
            if term2[1][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term2[1])))
               #should I add stop word removal here??
               docs2 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs2 = term_search(stem(case_folding(term2[1])),index)
            
            if term1[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term1[0])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(term1[0])),index)
            #make docs not against a list of total docs which we have to write code to make

        else:
            if term2[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term2[0])))
               #should I add stop word removal here??
               docs2 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs2 = term_search(stem(case_folding(term2[0])),index)
            
            if term1[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(term1[0])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(term1[0])),index)
            #make docs not against a list of total docs which we have to write code to make
        if not_in == 1:
            docs1 = list((set(list_of_all_docs)-set(docs1)))
        elif not_in ==2:
            docs2 = list((set(list_of_all_docs)-set(docs2)))
        
        return list(set(docs1) | set(docs2))
    else:
        if 'NOT' in query:
            if query[1][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(query[1])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(query[1])),index)
            
            return list((set(list_of_all_docs)-set(docs1)))
        else:
            if query[0][0] == '"' :
               search_terms = stem_list_of_words(tokenization(case_folding(query[0])))
               #should I add stop word removal here??
               docs1 = proximity_search(search_terms[0], search_terms[1],1,index)
            else:
                docs1 = term_search(stem(case_folding(query[0])),index)

            return docs1 

def weight_of_term(term,document,index):
    termfrequency = len(index[term][1][document])
    documentfrequency = index[term][0]
    weight = 1 + log10(termfrequency)
    weight = weight * log10((len(list_of_all_docs))/documentfrequency)
    return weight


def TFDIF_search(query,index):
    document_weights = {}
    for i in query:
        docs = list(index[i][1].keys())
        for doc in docs:
            if doc not in document_weights:
                document_weights[doc] = weight_of_term(i,doc,index)
            else:
                document_weights[doc]+= weight_of_term(i,doc,index)
    return document_weights



    





def term_search(term,index):
    return list(index[term][1].keys())

def read_queries(txtfile,index):
    file_write = ""
    file = open(txtfile, "r")
    queries = file.readlines()
    queries = list(map(lambda y: y[(y.index(" ") + 1):],list(map(lambda x: x.replace('\n',''),queries))))
    print(queries)
    query_no = 1
    for i in queries:
        if(i[0]=="#"):
            print("here goes the proximity search")
            proximity=i[1]
            terms = i[1:].split("(")[1]
            list_of_terms = stem_list_of_words(tokenization(case_folding(terms)))
            result = (proximity_search(list_of_terms[0],list_of_terms[1],proximity,index))
            for j in result:
                file_write += str(query_no) + "," + j + "\n"

        else:
            print("boolean searches go here")
            result = (boolean_search(i,index))
            for j in result:
                file_write += str(query_no) + "," + j + "\n"
        query_no +=1

    f = open("results.boolean.txt", "w")
    f.write(file_write)
    f.close()

def tfdif_queries(txtfile,index):
    file_write = ""
    file = open(txtfile, "r")
    queries = file.readlines()
    queries = list(map(lambda x : tokenization(x), queries))
    query_no = 1
    for i in queries:
        i = list(map(lambda x: case_folding(x), i))
        i = stopping(i,stop_words)
        i = stem_list_of_words(i)
        result = TFDIF_search(i,index)
        sorted_result = sorted(result, reverse = True, key = lambda x: result[x])
        if len(sorted_result) > 150: sorted_result = sorted_result[:150]
        for j in sorted_result:
            file_write+= str(query_no)+","+j+","+str(result[j]) +"\n"
        query_no +=1
    f = open("results.ranked.txt", "w")
    f.write(file_write)
    f.close()


#read_queries("queries.lab2.txt")

read_queries("queries.lab2.txt",index)

def print_index(index):
    file_write = ""
    for i in index:
        file_write += (i+":"+str(index[i][0])+"\n")
        for j in index[i][1]:
            doc_list = ",".join(list((map(lambda x : str(x),index[i][1][j]))))
            file_write+=("\t"+j+": " + doc_list+ "\n")
    f = open("index.txt", "w")
    f.write(file_write)
    f.close()
