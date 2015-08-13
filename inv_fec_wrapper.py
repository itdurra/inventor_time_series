#!/usr/bin/env python
########################################################
#           Python large_wrapper
#           Author: Ian Durra
########################################################
#
#Controller for patent_political_firm
#
import sys 
import os
import patent_political_firm
#conditional used for looping
d = None

#header for final csv file
header = (
	"Inv_Num,Year,Patents,Classes,Bwk_Citations,Bwk_Classes," +
	"Fwd_Citations,Past_Inventions,Past_Fwd_Citations," + 
	"Total_Republican_Donations,Republican_Transactions,Republican_Candidate_Transactions," +  
	"Total_Democratic_Donations,Democratic_Transactions,Democratic_Candidate_Transactions," + 
	"Republican_Unique_Years,Democrate_Unique_Years," + 
	"GVKey,datadate,fyear,indfmt,consol,popsrc,datafmt,conm,CURCD,ACT,ARTFS,AT,EMP,INVT," + 
	"LCT,LT,RECT,REVT,SEQ,TIE,XSGA,COSTAT,SIC,NI,XRD,t1,SumAT,SumEBIT,AvgRoA"
)

######################## Political Contributions #################
#Dependant databases used for political contributions dataset
committee = "Committee"
fec = "20150406 Inventor_FEC_matching"
political = "PoliticalContributions"
#filename for political contributions dataset
fileName = "inventor_political_contributions" 

######################## Inventor Patent Citations ###############
#Dependant databases used for inventor patent citations dataset
fwd = "FwdCitations"
bwk = "Citations"
inv = "Inventor"
cls = "Class"
gvkey = "GVKey"
#Transitional file names before combining JSON files
patent_class_temp = "Patent_Class_Temp"
patent_class_temp_fwd = "Patent_Class_Fwd"
patent_class_temp_bwk = "Patent_Class_Bwk"
patent_class_temp_gvkey = "Patent_Class_GVKey"
patent_class_temp_success = "Patent_Class_Success"
#filename for inventor patent dataset w/o classes for citations
fileName2 = "inventor_patent_citations"

######################## Firm Financials Data #####################
firm_rpt = "Financial"
#filename for firm financial data
fileName3 = "firm_financials"

######################## FINAL MERGE FILE NAME ####################
final_csv = "Inventor_Time_Political_Financial"


if __name__ == "__main__":
	response = ""
	print("Starting Controller For 'patent_political_firm.py'")
	while True:
		#loop while variable not set
		if not d:

			#user interactions
			print "Would you like to create JSON files? (Enter 'Y' or 'N')"
			response = sys.stdin.readline()
			if "y" in response.lower():

				#user interactions
				print "Would you like to create the " + fileName3 + " JSON file? (Enter 'Y' or 'N')"
				response = sys.stdin.readline()
				if "y" in response.lower():
					#create gvkey JSON file from .rpt
					r = open("./time_inventor_series/" + firm_rpt + ".rpt", "r")
					patent_political_firm.firm_rpt_json(r, firm_rpt)
					r.close()

				#user interactions
				print "Would you like to create the " + committee +" JSON file? (Enter 'Y' or 'N')"
				response = sys.stdin.readline()
				if "y" in response.lower():
					#opens .csv file as read only
					f = open("./data/" + committee + ".csv", "r")
					#create json files
					patent_political_firm.contributions_data_json(f, committee)
					f.close()

				#user interactions
				print "Would you like to create the " + fec +" JSON file? (Enter 'Y' or 'N')"
				response = sys.stdin.readline()
				if "y" in response.lower():
					#opens .csv file as read only
					f = open("./data/" + fec + ".csv", "r")
					#create json files
					patent_political_firm.fec_data_json(f, fec)
					f.close()

				#user interactions
				print "Would you like to create the " + fileName + " JSON file? (Enter 'Y' or 'N')"
				response = sys.stdin.readline()
				if "y" in response.lower():
					#user interactions
					print "Now loading necessary JSON files..."
					#load json files
					c = patent_political_firm.load_from_json(committee)
					f = patent_political_firm.load_from_json(fec)	
					#call method to combine dictionaries
					patent_political_firm.inventor_political_contributions_dataset(c, f, fileName)
					#memory
					c = {}
					f = {}

				#user interactions
				print "Would you like to create the " + fileName2 + " JSON file? (Enter 'Y' or 'N')"
				response = sys.stdin.readline()
				if "y" in response.lower():
					print "Would you like to re-create the dependant JSON files? (Enter 'Y' or 'N')"
					response = sys.stdin.readline()
					if "y" in response.lower():
						#create class JSON file from .rpt
						r = open("./time_inventor_series/" + cls + ".rpt", "r")
						patent_political_firm.class_rpt_json(r, cls)
						r.close()
						#create inventor JSON file from .rpt
						r = open("./time_inventor_series/" + inv + ".rpt", "r")
						patent_political_firm.inventor_rpt_json(r, inv)
						r.close()
						#create fwd citations JSON file from .rpt
						r = open("./time_inventor_series/" + fwd + ".rpt", "r")
						patent_political_firm.citations_rpt_json(r, fwd)
						r.close()
						#create bwk citations JSON file from .rpt
						r = open("./time_inventor_series/" + bwk + ".rpt", "r")
						patent_political_firm.citations_rpt_json(r, bwk)
						r.close()
						#create gvkey JSON file from .rpt
						r = open("./time_inventor_series/" + gvkey + ".rpt", "r")
						patent_political_firm.gvkey_rpt_json(r, gvkey)
						r.close()

					#user interactions
					print "Would you like to create the " + patent_class_temp + " JSON file? (Enter 'Y' or 'N')"
					response = sys.stdin.readline()
					if "y" in response.lower():
						#load json files
						inv = patent_political_firm.load_from_json(inv)
						#create new JSON file
						patent_political_firm.inv_patent_class_count(inv, patent_class_temp)
						inv = {}

					#user interactions
					print "Would you like to merge the dictionaries into a JSON file? (Enter 'Y' or 'N')"
					response = sys.stdin.readline()
					if "y" in response.lower():
						#user interactions
						print "Would you like to merge the forward citations? (Enter 'Y' or 'N')"
						response = sys.stdin.readline()
						if "y" in response.lower():
							print "Now loading necessary JSON files..."
							#load necessary JSON files
							inv = patent_political_firm.load_from_json(patent_class_temp)
							fwd_d = patent_political_firm.load_from_json(fwd)
							#merge fwd citations
							patent_political_firm.merge_citation_inv_dictionaries(inv, patent_class_temp_fwd, fwd_d)
							#clear dictionary for memory conservation
							fwd_d = {}
							inv = {}

						#user interactions
						print "Would you like to merge the backwards citations data? (Enter 'Y' or 'N')"
						response = sys.stdin.readline()
						if "y" in response.lower():
							print "Now loading necessary JSON files..."
							#load necessary JSON files
							inv = patent_political_firm.load_from_json(patent_class_temp_fwd)
							bwk_d = patent_political_firm.load_from_json(bwk)	
							cls_d = patent_political_firm.load_from_json(cls)
							#merge backwards citation
							patent_political_firm.merge_citation_inv_dictionaries(inv, patent_class_temp_bwk, None, bwk_d, cls_d)
							#clear dictionary for memory conservation
							bwk_d = {}
							cls_d = {}
							inv = {}

						#user interactions
						print "Would you like to merge the GVKey data? (Enter 'Y' or 'N')"
						response = sys.stdin.readline()
						if "y" in response.lower():
							print "Now loading necessary JSON files..."
							#load necessary JSON files
							inv = patent_political_firm.load_from_json(patent_class_temp_bwk)
							gvkey_d = patent_political_firm.load_from_json(gvkey)	
							#merge backwards citation
							patent_political_firm.merge_gvkey(inv, gvkey_d, patent_class_temp_gvkey)
							#clear dictionary for memory conservation
							gvkey_d = {}
							inv = {}

						#user interactions
						print "Would you like to add the inventor success variables? (Enter 'Y' or 'N')"
						response = sys.stdin.readline()
						if "y" in response.lower():
							print "Now loading necessary JSON files..."
							#load necessary JSON files
							inv = patent_political_firm.load_from_json(patent_class_temp_gvkey)
							#merge backwards citation
							patent_political_firm.add_success_variables(inv, patent_class_temp_success)
							#clear dictionary for memory conservation
							inv = {}
			
			#user interactions
			print "Beginning final merge of JSON files!"
			print "Now loading necessary JSON files..."
			inv = patent_political_firm.load_from_json(patent_class_temp_success)
			firm = patent_political_firm.load_from_json(firm_rpt)
			pol = patent_political_firm.load_from_json(fileName)
			
			#end loop
			d = True
		try:
			#clear file and open in append mode
			open("./" + final_csv + ".csv", "w").close()
			f = open("./" + final_csv + ".csv", "a")
			#add header to csv
			f.write(header + "\n")
			#call method to perform final merge
			patent_political_firm.merge_data_to_file(inv, firm, pol, f)
			f.close()

			print "Finished Program"
		except Exception as e:
			#print exception type with line number
			print e
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
		#repeat/kill the script upon user interaction
		print "Press enter to re-run the script, or CTRL-C to exit"
		sys.stdin.readline()
		reload(patent_political_firm)


