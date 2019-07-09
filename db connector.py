import json
import sqlite3
from pandas.io.json import json_normalize
import time
from time import gmtime, strftime
import sqlalchemy
import pandas as pd
import collections
import collections

try:
    collectionsAbc = collections.abc
except AttributeError:
    collectionsAbc = collections

def db_storage(data_url, db_url):
	with open(data_url) as f:
		data = json.load(f)  #Load Json File as data
	def flatten(d, parent_key = "", sep = "_"):
		items = []
		for k, v in d.items():
			new_key = parent_key + sep + k if parent_key else k
			if isinstance(v, collectionsAbc.MutableMapping):
				items.extend(flatten(v, new_key, sep=sep).items())
			else:
				items.append((new_key, v))
		return dict(items)   #Function to flatten the dictionary in the dictionary object
	for x in data:
		data[x] = flatten(data[x])
	df = pd.DataFrame(data).T  #Transpose the dataframe to get what we want
	df["USER_BOOL"] = ["None" if df["USER_PROCESSES"][i] is None else "Empty" if len(df["USER_PROCESSES"][i]) == 0 else "Yes"
for i in range(0,df.shape[0])]  #Add a boolean column to identify if there are "empty", "none" and "user list" 3 senarios
	df = df.reset_index(drop = True).drop(["SUGGESTION"], axis = 1) #Drop the column "SUGGESTION"
	def user_table(df):
		user_df = pd.DataFrame()
		hist_l = []
		id_l = []
		for i in range(0,df.shape[0]):
			if df["USER_BOOL"][i] == "Yes":
				hist_l = hist_l + df["USER_PROCESSES"][i]
				id_l = id_l + [df.index[i]] * len(df["USER_PROCESSES"][i])
		user_df["History_ID"] = id_l
		user_df["USER"] = hist_l
		return user_df   #Create a table that stores all of the users along with the id generated in History table
	user_df = user_table(df)
	df = df.drop(["USER_PROCESSES"], axis=1) #Drop "USER_PROCESS" for storage concerns
	df["Index_ID"] = df.index.to_list() # Make a clear column as the primary key for History table
	connection = sqlite3.connect(db_url) #Connect to the db
	df.to_sql('History', con= connection,  if_exists = "replace", index = True)
	user_df.to_sql("User", con= connection,  if_exists = "replace", index = True) #Store the two tables
	print ("done")
