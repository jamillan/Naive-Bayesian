from __future__ import division
import collections
import math
import os
import json
import sys

size = 8
class Bayesian:
	def __init__(self,File):
		self.trainingFile = File
		self.features = {}      #all feature names and their possible values (including the class label)
		self.featureList = []       #this is to maintain the order of features as in the dat
		self.featureCounts = collections.defaultdict(lambda: 1)#contains tuples of the form (label, feature_name, feature_value)
		self.featureVectors = []        #contains all the values and the label as the last entry
		self.labelCounts = collections.defaultdict(lambda: 0)   #these will be smoothed late
		self.files = sys.stdin.read()
		self.files = self.files.split("\n")

		self.featureList.append("keywords")

 		nfile = self.files[0]
		data = json.loads(nfile)

#for j in range(len(files)-1):
		for j in range(1,len(self.files)-1):
			nfile =  self.files[j]
			data = json.loads(nfile)

			topic   = str("topic").encode("UTF-8")
			question= str("question").encode("UTF-8")
			excerpt = str("excerpt").encode("UTF-8")
			top   = data[topic]
			ques  = data[question]
			exc   = data[excerpt]
			top = top.encode("ascii", "ignore")
			ques = ques.encode("ascii", "ignore")
			exc = exc.encode("ascii", "ignore")

			words = ques + " " + exc
			words  = exc.split()

			for i in words:
				if len(i) > size:
					#self.featureCounts[(top,i)]+=1
		#			self.labelCounts[top]+=1
					buffer = []

					buffer.append(i)
					buffer.append(top)
					self.featureVectors.append(buffer)

			

#Training function
	def ClassifierTraining(self):
		for fv in self.featureVectors:
			self.labelCounts[fv[len(fv)-1]]+=1
			for counter in range(0,len(fv)-1):
				self.featureCounts[(fv[len(fv)-1], self.featureList[0], fv[counter])] += 1

		  



#		for label in self.labelCounts:
#			for feature in self.featureList[:len(self.featureList)-1]:
#				self.labelCounts[label] += len(self.features[feature])

#classifier
	def Classify(self,featureVector):
		probabilityPerLabel = {}
		for label in self.labelCounts:
			logProb = 0
			for featureValue in featureVector:

				logProb +=  math.log(self.featureCounts[(label, self.featureList[0], featureValue)]/self.labelCounts[label])

			probabilityPerLabel[label] = (self.labelCounts[label]/sum(self.labelCounts.values())) * math.exp(logProb)

		return max(probabilityPerLabel, key = lambda classLabel: probabilityPerLabel[classLabel])

	def GetValues(self):
		file = open(self.trainingFile,'r')
		for line in file:
			if line[0]!='@':#start of data
				self.featureVectors.append(line.strip().lower().split(','))
			else:
				if line.strip().lower().find('@data')==-1 and  (not line.lower().startswith('@relation')):
					self.featureList.append(line.strip().split()[1])
					self.features[self.featureList[len(self.featureList) - 1]] = line[line.find('{')+1: line.find('}')].strip().split(',')

		file.close()


	def TestClassifier(self,File):
		file = open(File , 'r')
		yes = 0
		no = 0
		precision_yes  = 0
		precision_no  = 0
		recall_yes  = 0
		recall_no  = 0
		pub = 0 
		nfile = self.files[0]
		nbr_tryouts = 0	
		labelcounts = collections.defaultdict(lambda:0)		
		precision_yes = collections.defaultdict(lambda:0)		
		recall_yes = collections.defaultdict(lambda:0)		
		for j in range(1,20218):
#		for j in range(2000,2150):
			nfile =  self.files[j]
			data = json.loads(nfile)

			topic   = str("topic").encode("UTF-8")
			question= str("question").encode("UTF-8")
			excerpt = str("excerpt").encode("UTF-8")
			top   = data[topic]	
			ques  = data[question]
			exc   = data[excerpt]
			top = top.encode("ascii", "ignore")
			ques = ques.encode("ascii", "ignore")
			exc = exc.encode("ascii", "ignore")

 			words = ques + " " + exc
			words  = exc.split()
			vector = []

			token = 0
			for i in words:
				if len(i) > size and token == 0:

					token += 1
					self.featureCounts[(top,i)]+=1
					self.labelCounts[top]+=1
 			#		buffer = []

 			#		buffer.append(i)
			#		buffer.append(top)
 					vector.append(i)
 					vector.append(top)

			if token != 0:
				nbr_tryouts = nbr_tryouts + 1
				labelcounts[top] +=1
				print "classifier: " + self.Classify(vector) + " given " + vector[len(vector) - 1] , "topic"    


				if self.Classify(vector) == top:
					precision_yes[top] = precision_yes[top] + 1

				if self.Classify(vector) !=top:
					recall_yes[top] = recall_yes[top] + 1


		total_precision = 0
		for label in labelcounts:
			total_precision += precision_yes[label]
			print "******Precision for topic ",label," : ",precision_yes[label] / labelcounts[label]
			print "******Recall for topic ",label," : ", recall_yes[label] / labelcounts[label]
		
		print "Global Precision : ", total_precision / nbr_tryouts
				


if __name__  == "__main__":
	dir = os.getcwd()

	model=Bayesian(dir + "/training.dat")
#	model.GetValues()
	model.ClassifierTraining()
	model.TestClassifier(dir + "/test.dat")

	
