#!/usr/bin/env python
########################################################
#           Python patent_political_firm
#           Author: Ian Durra
########################################################

import ujson as json
import sys
import os
import re
import collections
import csv

###############################################
######## Final Write Data to File #############
###############################################
###############################################

#Param inv:
#	dictionary containing patent data for inventors by year
#
#Param firm:
#	dictionary containing firm financial data
#
#Param pol:
#	dictionary containing political contributions
#
#Param f:
#	file object to be written to
#
#POST:
#	outputs merged dictionaries into a file given by
#	the f parameter
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def merge_data_to_file(inv, firm, pol, f):
	try:
		date = ""
		arr = []
		count = 0
		gvkey_matches = 0
		political = 0
		line = ""
		past_inv = ""
		past_fwd = ""
		r_consec_contr = "0"
		d_consec_contr = "0"
		i = {}
		p = {}
		#loop through inventors
		for key in sorted(inv):
			#reset/update counts
			r_consec_contr = "0"
			d_consec_contr = "0"
			arr = []
			#sort years
			for year in inv[key]:
				arr.append(int(year))



			#HANDLE SIC2 CODE IS CURRENTLY NOT OPERABLE!!!!!!!!!!!!!!!


			arr.sort()
			year = str(arr[0])
			#loop through inventors years/null years
			while year <= str(arr[-1]):
				line = ""
				#default assumption of no financial data
				financial = (",NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL," + 
					"NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL")
				#handle patent data
				if year in inv[key]:
					#readability
					i = inv[key][year]
					#store success variables
					past = assign_success_vars(i, past_inv, past_fwd, year, str(arr[0]))
					#num of patents
					line = (
						key + "," + year + "," + str(len(i["Patent"])) + "," + str(i["Class"]) + 
						"," + str(i["Bwk"]) + "," + str(i["Bwk_Class"]) + "," + str(i["Fwd"]) + 
						"," + str(i["Past_Inv"]) + "," + str(i["Past_Fwd"]) + ","
					)
					#handle linking of financial data
					if i["GVKey"] and i["GVKey"] in firm:
						gvkey_matches = gvkey_matches + 1
						financial = i["GVKey"] + "," + firm[i["GVKey"]]
				else:
					#handles success variables for inventors inactive years
					if str(int(year) - 1) in inv[key]:
						past_inv = int(past[0]) + int(len(inv[key][str(int(year) - 1)]["Patent"]))
						past_fwd = int(past[1]) + int(inv[key][str(int(year) - 1)]["Fwd"])
					line = (key + "," + year + ",0,,0,,0," + str(past_inv) + "," + str(past_fwd) + ",")
				#handle political contributions
				if key in pol and year in pol[key]:
					#tests non blank matches
					if pol[key][year]["DEM"]["total_contr"] or pol[key][year]["REP"]["total_contr"]:
						political = political + 1
					#readability
					r = pol[key][year]["REP"]
					d = pol[key][year]["DEM"]
					r_consec_contr = str(r["consecutive"])
					d_consec_contr = str(d["consecutive"])
					line = (
						line + str(r["total_contr"]) + "," + str(r["party_trans"]) + "," +
						str(r["candi_trans"]) + "," + str(d["total_contr"]) + "," + str(d["party_trans"]) + 
						"," + str(d["candi_trans"]) + "," + r_consec_contr + "," + d_consec_contr + ","
					)
				else:
					line = (line + "0,0,0,0,0,0," + r_consec_contr + "," + d_consec_contr + ",")
				#test for non-null values
				line = line + financial
				line = re.sub('(,,)', ',NULL,', line)
				f.write(line + "\n")
				year = str(int(year) + 1)
			#UI
			count = progress(inv, count, gvkey_matches, political)
	#handle exceptions
	except Exception as e:
		exception_helper(e)

#Param inv:
#	dictionary object within the inventor time series
#
#Param past_inv, past_fwd:
#	counts of past inventions and past fwd_citations
#
#Param year, year1:
#	String representations of years
#
#RETURN:
#	Helper method which assigns past success variables
#	Returns a tuple containing updated params past_inv and past_fwd
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def assign_success_vars(i, past_inv, past_fwd, year, year1):
	#first year in inventor career
	if year == year1:
		past_inv = str(len(i["Patent"]))
		past_fwd = str(i["Fwd"])
	else:
		past_inv = str(i["Past_Inv"])
		past_fwd = str(i["Past_Fwd"])
	#return tuple containing success variables
	return (past_inv, past_fwd)

###############################################
############ Inventor Patent Data #############
###############################################
###############################################

#Param inv:
#	inventor time series dictionary object
#
#Param fileName:
#	file name for output
#
#POST:
#	adds inventor past success variables to larger
#	inventor time series and outputs results to JSON file
#	given by the fileName parameter
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def add_success_variables(inv, fileName):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		count = 0
		inventions = 0
		citations = 0
		length = 0
		arr = []
		#loop through inventor dataset
		for key in inv:
			arr = []
			inventions = 0
			citations = 0
			#loop through years
			for year in inv[key]:
				arr.append(int(year))
			arr.sort()
			for year in arr:
				year = str(year)
				#store number of patents
				length = len(inv[key][year]["Patent"])
				#update before for year before
				inv[key][year]["Past_Inv"] = inventions
				inv[key][year]["Past_Fwd"] = citations
				if length:
					inventions = inventions + len(inv[key][year]["Patent"])
					citations = citations + int(inv[key][year]["Fwd"])
			#UI
			count = progress(inv, count)
		print "Finished JSON encoding for " + fileName + "..."
		#put dictionary into json file
		put_into_json(inv, fileName)
	#handle exceptions
	except Exception as e:
		exception_helper(e)

#Param inv:
#	inventor time series dictionary object
#
#Param gvkey:
#	dictionary object containing gvkeys
#
#Param fileName:
#	file name for output
#
#POST:
#	Adds GVKey's to larger inventor time series
#	and outputs results to JSON file given by param fileName
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def merge_gvkey(inv, gvkey, fileName):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		count = 0
		matches = 0
		minimum = str(sys.maxint)
		temp = {}
		#loop through inventor dataset
		for key in inv:
			#loop through years
			for year in inv[key]:
				for patent in inv[key][year]["Patent"]:
					#handle data formatting
					patent = re.sub('[a-zA-Z]', '', patent)
					patent = patent.lstrip("0")

					#test code
					if patent in gvkey:
						matches = matches + 1

					if int(patent) < int(minimum):
						minimum = patent
						if minimum in gvkey:
							#stores first GVKey in terms of date
							temp = {"GVKey":gvkey[minimum]["GVKey"]}
					#DO THIS TWICE: to catch bad data, generate more matches
					if minimum in gvkey:
						#updates dictionary to store GVKey
						inv[key][year].update(temp)
						#matches = matches + 1
					else:
						inv[key][year].update({"GVKey":""})
				minimum = str(sys.maxint)
			#UI
			count = progress(inv, count, matches)
		print "Finished JSON encoding for " + fileName + "..."
		#put dictionary into json file
		put_into_json(inv, fileName)
	#handle exceptions
	except Exception as e:
		exception_helper(e)

#Param inv:
#	inventor time series dictionary object
#
#Param fileName:
#	file name for output
#
#POST:
#	creates the inventor time series dataset
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def inv_patent_class_count(inv, fileName):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		d = {}
		date = {}
		count = 0
		#loop through inventor dataset
		for key in inv:
			#loop through years
			for year in inv[key]:
				#create and populate sets
				p = set()
				c = set()
				#add unique number of patents
				add_elements_to_inv(p, inv[key][year]["Patent"])
				#add unique number of classes
				add_elements_to_inv(c, inv[key][year]["Class"])
				date = {year:{"Patent":p, "Class":len(c)}}
				#update dict
				if key in d:
					d[key].update(date)
				else:
					d[key] = date
			#UI
			count = progress(inv, count)
		print "Finished JSON encoding for " + fileName + "..."
		#put dictionary into json file
		put_into_json(d, fileName)
	#handle exceptions
	except Exception as e:
		exception_helper(e)

#Param inv:
#	dictionary object for merging
#
#Param fileName:
#	file name for output
#
#Param fwd:
#	dictionary object of fwd citations to merge
#
#Param bwk, cls
#	optional dictionary objects, bwk_cites and classes
#
#POST:
#	optional parameters allow this method to handle the
#	merging of the larger inventor time series with
#	the forward/backward citation dataset, including classes
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def merge_citation_inv_dictionaries(inv, fileName, fwd, bwk=None, cls=None):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		date = {}
		count = 0
		#loop through inventor dataset
		for key in inv:
			#loop through years
			for year in inv[key]:
				#if backwards citations
				if bwk:
					#create and populate backwards citations and their classes
					b = set()
					c = set()
					add_class_and_bwk_to_set(b, c, bwk, cls, inv[key][year]["Patent"])
					inv[key][year].update({"Bwk":len(b), "Bwk_Class":len(c)})
				else:
					#create and populate sets of fwd citations
					f = set()
					add_elements_to_set(f, fwd, inv[key][year]["Patent"])
					inv[key][year].update({"Fwd":len(f)})
			#UI
			count = progress(inv, count)
		print "Finished JSON encoding for " + fileName + "..."
		#put dictionary into json file
		put_into_json(inv, fileName)
	#handle exceptions
	except Exception as e:
		exception_helper(e)


###############################################
############ Inventor Political ###############
###############################################
###############################################

#Param con:
#	political contributions dictionary object
#
#Param fec:
#	FEC matching database dictionary object
#
#Param fileName:
#	file name for output
#
#POST:
#	merges the contributions and FEC database
#	outputs results to JSON file given by param fileName
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def inventor_political_contributions_dataset(con, fec, fileName):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		d = {}
		category = ""
		party = ""
		total_contr = ""
		party_trans = ""
		candi_trans = ""
		#for each committee
		for com in fec:
			#for each inventor who donated to a committee
			for inv in fec[com]:
				#for each year inventor donated to the committee
				for year in fec[com][inv]:
					try:
						#store committee variables
						category = con[com]["type"]
						party = con[com]["party"]
						#update total contributions to committee
						total_contr = int(d[inv][year][party]["total_contr"]) + int(fec[com][inv][year]["amount"])
						d[inv][year][party]["total_contr"] = total_contr
						#if candidate
						if "h" in category.lower() or "p" in category.lower() or "s" in category.lower():
							d[inv][year][party]["candi_trans"] = int(d[inv][year][party]["candi_trans"]) + 1
						else:
							d[inv][year][party]["party_trans"] = int(d[inv][year][party]["party_trans"]) + 1
					except KeyError:
						#if inventor donated REP/DEM that year
						if com in con:
							#set/update desired variables
							total_contr = fec[com][inv][year]["amount"]
							tuple1 = set_trans_var_helper(candi_trans, party_trans, category)
							candi_trans = tuple1[0]
							party_trans = tuple1[1]
							#update dictionary
							if inv in d:
								#handles case where inventor donated to both parties in one year
								if year not in d[inv]:
									d[inv].update({year:{"REP":{},"DEM":{}}})
							else:
								d[inv] = {year:{"REP":{},"DEM":{}}}
							d[inv][year][party] = {"total_contr":total_contr, "party_trans":party_trans, 
								"candi_trans":candi_trans}
						else:
							#implies inventor donated to third party
							if inv not in d:
								d[inv] = {year:{"REP":{},"DEM":{}}}
		#adds consecutive year donation variable
		#dumps resulting dict into JSON file
		inventor_political_contributions_concecutive_variable(d, fileName)
	#handle exceptions
	except Exception as e:
		exception_helper(e)

#Param d:
#	dictionary object
#
#Param fileName:
#	file name for output
#
#POST:
#	adds consecutive years of political contributions variable
#	to the passed dictionary and outputs results to JSON file
#
def inventor_political_contributions_concecutive_variable(d, fileName):
	#Begin adding consecutive year donation variable
		print "Finished part 1 of 2 for " + fileName + " JSON encoding"
		dem = 0
		rep = 0
		d_contr = 0
		r_contr = 0
		#loop through key
		for key in d:
			dem = 0
			rep = 0
			#loop through year at key
			for year in sorted(d[key]):
				d_contr = 0
				r_contr = 0
				#set total contribution variables
				if d[key][year]["REP"]:
					r_contr = d[key][year]["REP"]["total_contr"] 
				if d[key][year]["DEM"]:
					d_contr = d[key][year]["DEM"]["total_contr"]
				#both empty
				if is_empty(d[key][year]["REP"]) and is_empty(d[key][year]["DEM"]):
						d[key][year]["REP"] = {"total_contr":r_contr, "party_trans":"0", "candi_trans":"0"}
						d[key][year]["DEM"] = {"total_contr":d_contr, "party_trans":"0", "candi_trans":"0"}
				else:
					#assign values, update counts
					if is_empty(d[key][year]["REP"]):
						d[key][year]["REP"] = {"total_contr":r_contr, "party_trans":"0", "candi_trans":"0"}
						dem = dem + 1
					elif is_empty(d[key][year]["DEM"]):
						d[key][year]["DEM"] = {"total_contr":d_contr, "party_trans":"0", "candi_trans":"0"}
						rep = rep + 1
					else:
						#handle case where inventor donated to both parties in same year
						rep = rep + 1
						dem = dem + 1
				#update key value pairs
				d[key][year]["REP"]["consecutive"] = rep
				d[key][year]["DEM"]["consecutive"] = dem
		print "Finished part 2 of 2 for " + fileName + " JSON encoding"
		#put dictionary into json file
		put_into_json(d, fileName)

#Param f:
#	file object, read only
#
#Param fileName:
#	file name for output
#
#POST:
#	converts .csv file into JSON file (FEC matching database)
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def fec_data_json(f, fileName):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		d = {}
		arr = []
		index = 0
		amount = ""
		#csv library handles delimeters within data
		for arr in csv.reader(f, delimiter=',', quotechar='"'):
			#handles rpt decoding
			#line = rpt_decode_helper(",")
			#handles csv file headers
			if index != 0:
				#formats year i.e. 99, 02 into 1999, 2002
				arr[17] = add_year_prefix(arr[17])
				arr[1] = arr[1][:-1]
				if arr[17] != "":
					#tries to catch improperly formatted data
					if len(arr) == 53:
						#if committe exists in dictionary
						if arr[1] in d:
							#if inventor in committee dictionary
							if arr[25] in d[arr[1]]:
								if arr[17] in d[arr[1]][arr[25]]:
									#store amount of donation for readability
									amount = d[arr[1]][arr[25]][arr[17]]["amount"]
									d[arr[1]][arr[25]][arr[17]] = {"amount":int(amount) + int(arr[19])}
								else:
									d[arr[1]][arr[25]].update({arr[17]:{"amount":arr[19]}})
							else:
								d[arr[1]].update({arr[25]:{arr[17]:{"amount":arr[19]}}})
						else:
							#new key value pair
							d[arr[1]] = {arr[25]:{arr[17]:{"amount":arr[19]}}}
					else:
						print len(arr) + " " + arr[17]
						print "Indicates fundamental problem w/ .xslx file"
			index += 1
		print "Finished creating " + fileName + " object!"
		#put dictionary into json file
		put_into_json(d, fileName)
	except Exception as e:
		exception_helper(e)

#Param f:
#	file object, read only
#
#Param fileName:
#	file name for output
#
#POST:
#	converts .csv file into JSON file (Political Contributions)
#
#Exception:
#	catches exceptions to avoid crashing controller program
#
def contributions_data_json(f, fileName):
	print "Beginning JSON encoding for " + fileName + "..."
	try:
		d = {}
		arr = []
		for line in f:
			#handles rpt decoding
			line = rpt_decode_helper(line)
			arr = []
			#file is delimited by "|"
			arr = line.split("|")
			#arbitrary test to avoid blank data
			if len(arr) == 15 and (arr[10].upper() == "REP" or arr[10].upper() == "DEM"):
				try:
					#attempts to add values to existing key-value pairs
					d[arr[0]] = {"type":arr[9], "party":arr[10]}
				except KeyError:
					#this error should never throw as keys are always unique
					print "Fatal Error in " + fileName + " JSON transfer"
		print "Finished creating " + fileName + " object!"
		#put dictionary into json file
		put_into_json(d, fileName)
	except Exception as e:
		exception_helper(e)



###############################################
############ JSON HELPER METHODS ##############
###############################################
###############################################

#Param fileName:
#	file name used throughout program
#
#Return:
#	returns dictionary read from JSON file
#
def load_from_json(fileName):
	with open("./json/" + fileName + ".json") as f:
		obj = json.load(f)
		print "Succesfully loaded '" + fileName + "' from JSON file!"
		f.close()
		return obj

#Param fileName:
#	file name used throughout program
#
#Param d:
#	dictionary object
#
#POST:
#	Clears existing JSON file
#	puts dictionary object into JSON file
#	using desired file name as parameter
#
def put_into_json(d, fileName):
	open("./json/" + fileName + ".json", "w").close()
	with open("./json/" + fileName + ".json", "w") as j:
		print "Attempting to write '" + fileName + "' into JSON file..."
		json.dump(d, j)


###############################################
########### FORMATTING HELPER METHODS #########
###############################################
###############################################

#Param year:
#	String representing date in format '03-MAY-01'
#
#Return:
#	returns a 4 digit year i.e. '2001' as a string
#	will return a empty string if data is improperly formatted
#
def add_year_prefix(year):
	year = year[-2:]
	#checks that data is in correct format
	if year.isdigit():
		if int(year) <= 15 or year == "00":
			year = "20" + year
		else:
			year = "19" + year
		return year
	else:
		return ""

#Param line:
#	Line of rpt file
#
#POST:
#	removes .rpt newline characters
#	which interfere w/ JSON encode
#
def rpt_decode_helper(line):
	line = line.replace('\r', '')
	line = line.replace('\n', '')
	line = line.replace('\\', '')
	return line

###############################################
############ GENERAL HELPER METHODS ###########
###############################################
###############################################

#Param candi_trans:
#	integer counting number of transactions to candidates
#
#Param party_trans:
#	integer counting number of transactions to party
#
#Param category:
#	string representation of political position ((s|h|p) == candidate)
#
#RETURN:
#	returns a tuple containing updated candi_trans and party_trans variables
#
def set_trans_var_helper(candi_trans, party_trans, category):
	if "h" in category.lower() or "p" in category.lower() or "s" in category.lower():
		candi_trans = 1
		party_trans = 0
	else:
		candi_trans = 0
		party_trans = 1
	return (candi_trans, party_trans)

#Param d:
#	Dictionary object
#
#Param count
#	Counts iterations over object
#
#Param gvkey
#	optional parameter to print
#
#Param political
#	optional parameter to print
#
#POST:
#	updates user on progress of operation 
#	by printing to console every 100000 iterations
#
#RETURN:
#	updates count variable +1
#	
def progress(d, count, gvkey="", political=""):
	if (count % 100000 == 0 or count == len(d) - 1) and count != 0:
		string = "Finished " + str(count) + " of " + str(len(d))
		if gvkey:
			string = string + ", gvkey_matches = " + str(gvkey)
		if political:
			string = string + ", political_matches = " + str(political)
		print string
	return count + 1

#Param d:
#	Dictionary object
#
#Param key
#	Key to be removed
#
#POST:
#	removes value from dictionary object
#
def remove_value(d, key):
	if key in d:
		d[key] = {}

#Param b:
#	set object where bwk_citations should be added
#
#Param c:
#	set object where class' should be added
#
#Param bwk:
#	database from where bwk_citations are extracted
#
#Param cls:
#	database from where class' are extracted
#
#Param keyset:
#	iterable keyset used to extract keys
#
#POST:
#	adds items from iterable object to multiple sets
#
def add_class_and_bwk_to_set(b, c, bwk, cls, keyset):
	for key in keyset:
		if key in bwk:
			for element in bwk[key]:
				b.add(element)
				if element in cls:
					c.add(cls[element])

#Param destination:
#	set object where elements should be added
#
#Param data:
#	database from where items are extracted
#
#Param keyset:
#	iterable keyset used to extract keys
#
#POST:
#	adds items from iterable object to set
#
def add_elements_to_set(destination, data, keyset):
	for key in keyset:
		if key in data:
			for element in data[key]:
				destination.add(element)

#Param destination:
#	set object where elements should be added
#
#Param keyset:
#	iterable keyset used to extract keys
#
#POST:
#	adds items from iterable object to set
#
def add_elements_to_inv(destination, keyset):
	for key in keyset:
		destination.add(key)

#Param any_structure:
#	object to test
#
#Return:
#	returns true if object is empty
#
def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

#Param e:
#	Exception object
#
#POST:
#	print exception type with line number and sys info
#
def exception_helper(e):
	print e
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno)


###############################################
############ RPT TO JSON METHODS ##############
###############################################
###############################################

#Param f
#	file object, read only
#
#Param fileName
#	fileName for pulling rpt file
#	and naming new JSON file
#
#POST:
#	decodes RPT file, and places into JSON file
#
#Exception:
#	catches Exceptions to avoid crashing controller
#
def citations_rpt_json(f, fileName):
	print "Attempting to create the " + fileName + " JSON object!"
	try:
		d = {}
		arr = []
		index = 0
		#loop through file
		for line in f:
			#handles rpt encoding
			line = rpt_decode_helper(line)
			#handles header line
			if index != 0:
				arr = []
				arr = line.split(",")
				#handles invalid data
				if len(arr) == 3:
					try:
						#attempts to add values to existing key-value pairs
						d[arr[0]].append(arr[1])
					except KeyError:
						#creates new key value pairing
						d[arr[0]] = [arr[1]]
			index += 1
		print "Finished creating " + fileName + " JSON object!"
		#put dictionary into json file
		put_into_json(d, fileName)
	except Exception as e:
		#print exception type with line number
		exception_helper(e)

#Param f
#	file object, read only
#
#Param fileName
#	fileName for pulling rpt file
#	and naming new JSON file
#
#POST:
#	decodes RPT file, and places into JSON file
#
#Exception:
#	catches Exceptions to avoid crashing controller
#
def inventor_rpt_json(f, fileName):
	print "Attempting to create the " + fileName + " JSON object!"
	try:
		d = {}
		arr = []
		index = 0
		year = ""
		temp = ""
		uClass = []
		#loop through file
		for line in f:
			#handles rpt encoding
			line = rpt_decode_helper(line)
			#handles header line
			if index != 0:
				arr = []
				arr = line.split(",")
				#handles invalid data
				if len(arr) == 6:
					#parse class variable
					uClass = arr[5].split("/");
					arr[5] = uClass[0]
					try:
						#attempts to add values to existing key-value pairs
						d[arr[0]][arr[4]]["Patent"].add(arr[3])
						d[arr[0]][arr[4]]["Class"].add(arr[5])
					except KeyError:
						#utilizes sets to store only distinct values
						p = set()
						c = set()
						p.add(arr[3])
						c.add(arr[5])
						temp = {}
						temp = {arr[4]:{"First":arr[1], "Last":arr[2], "Patent":p, "Class":c}}
						if arr[0] in d:
							#inventor key exists, year doesn't
							d[arr[0]].update(temp)
						else:
							#inventor key does not exist
							d[arr[0]] = temp
			index += 1
		print "Finished creating " + fileName + " JSON object!"
		#put into json file
		put_into_json(d, fileName)
	except Exception as e:
		#print exception type with line number
		exception_helper(e)

#Param f
#	file object, read only
#
#Param fileName
#	fileName for pulling rpt file
#	and naming new JSON file
#
#POST:
#	decodes RPT file, and places into JSON file
#
#Exception:
#	catches Exceptions to avoid crashing controller
#
def firm_rpt_json(f, fileName):
	print "Attempting to create the " + fileName + " JSON object!"
	try:
		d = {}
		tuple1 = ()
		index = 0
		#loop through file
		for line in f:
			#handles rpt encoding
			line = rpt_decode_helper(line)
			#handles header line
			if index != 0:
				tuple1 = ()
				tuple1 = line.partition(",")
				#handles invalid data
				if tuple1[0] and tuple1[2]:
					d[tuple1[0]] = tuple1[2]
			index += 1
		print "Finished creating " + fileName + " JSON object!"
		#put into json file
		put_into_json(d, fileName)
	except Exception as e:
		#print exception type with line number
		exception_helper(e)

#Param f
#	file object, read only
#
#Param fileName
#	fileName for pulling rpt file
#	and naming new JSON file
#
#POST:
#	decodes RPT file, and places into JSON file
#
#Exception:
#	catches Exceptions to avoid crashing controller
#
def gvkey_rpt_json(f, fileName):
	print "Attempting to create the " + fileName + " JSON object!"
	try:
		d = {}
		arr = []
		index = 0
		#loop through file
		for line in f:
			#handles rpt encoding
			line = rpt_decode_helper(line)
			#handles header line
			if index != 0:
				arr = []
				arr = line.split(",")
				#handles invalid data
				if len(arr) == 3:
					d[arr[0]] = {"PDPass":arr[1], "GVKey":arr[2]}
			index += 1
		print "Finished creating " + fileName + " JSON object!"
		#put into json file
		put_into_json(d, fileName)
	except Exception as e:
		#print exception type with line number
		exception_helper(e)


#Param f
#	file object, read only
#
#Param fileName
#	fileName for pulling rpt file
#	and naming new JSON file
#
#POST:
#	decodes RPT file, and places into JSON file
#y
#Exception:
#	catches Exceptions to avoid crashing controller
#
def class_rpt_json(f, fileName):
	print "Attempting to create the " + fileName + " JSON object!"
	try:
		d = {}
		arr = []
		index = 0
		#loop through file
		for line in f:
			#handles rpt encoding
			line = rpt_decode_helper(line)
			#handles header line
			if index != 0:
				arr = []
				arr = line.split(",")
				#handles invalid data
				if len(arr) == 2:
					d[arr[0]] = arr[1]
			index += 1
		print "Finished creating " + fileName + " JSON object!"
		#put into json file
		put_into_json(d, fileName)
	except Exception as e:
		#print exception type with line number
		exception_helper(e)

