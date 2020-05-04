import json
import sqlite3 
import requests
import pandas as pd
from pandas.io import sql
from flask import Flask,request
from flask_restplus import Resource,Api,reqparse
import datetime

# if cannot run or import "importError", please input "pip3 install werkzeug~=0.16.1" again!!, thanks~



app = Flask(__name__)
api = Api(app,version="9.9",title="World Bank Economic Indicators",description="COMP9321 Assignment2 writen by YangLi z5133109")

#@api.route('/indicators')
#url="http://api.worldbank.org/v2/countries/all/indicators/NY.GDP.MKTP.CD?date=2012:2017&format=json&per_page=1000"
#NY.GDP.MKTP.CD


def write_in_sqlite(dataframe, database_file, table_name):
    """
    :param dataframe: The dataframe which must be written into the database
    :param database_file: where the database is stored
    :param table_name: the name of the table
    """

    cnx = sqlite3.connect(database_file)
    sql.to_sql(dataframe, name=table_name, con=cnx, if_exists="replace", index=False)


def read_from_sqlite(database_file, table_name):
    """
    :param database_file: where the database is stored
    :param table_name: the name of the table
    :return: A Dataframe
    """
    try:
        cnx = sqlite3.connect(database_file)
        return sql.read_sql('select * from ' + table_name, cnx)
    except:
        return None
        
def qsix_datatype(value):
	if value[0].isdigit():
		return value
	else:
		if value[0]=="-":
			return value
		else:
			return "+"+value[1:]

def check_input_order(input_list):
	temp=set()
	for i in input_list:
		temp.add(i.strip("+-"))

	if len(temp)==len(input_list):
		return True # all of orders are correct
	else:
		return False # it has reflect order like {+id,-id}

def check_number(num):
	new_num=num.strip("+-")
	# check the number is integer or not
	if new_num.isdigit() is False:
		return False
	# check the value range
	if int(new_num)<1 or int(new_num)>100:
		return False

	return True



@api.route('/collections')

class Q1(Resource):
	#question1 and question3
	@api.response(200,"OK")
	@api.param('order_by', '{+id,+creation_time,+indicator,-id,-creation_time,-indicator}', default='+id')
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('order_by', type=str, required=True,nullable=False,action="append")
		args = parser.parse_args()
		order_type = args.get("order_by")

		temp=order_type[0].split(",")

		target_list=["+id","+creation_time","+indicator","-id","-creation_time","-indicator"]

		for i in temp: #check invalid input(not include reflect correct input)
			if i not in target_list:
				return "Invalid input!", 406

		flag=check_input_order(temp)

		if flag is False:
			return "Invalid input!",405

		database_file="z5133109.db"
		table_name="assignment2"

		query_df=read_from_sqlite(database_file, table_name)

		if query_df is None:
			return "Database doesn't exist!",404

		col_list=[]
		asd_list=[]
		for i in temp:
			col_list.append(i[1:])
			if i[0]=="+":
				asd_list.append(True)
			else:
				asd_list.append(False)

		total=[]

		temp_df=query_df.sort_values(by=col_list,ascending=asd_list)

		for i in temp_df.iterrows():
			temp_dict=dict()
			temp_dict["uri"]="/collections/{}".format(i[1]["id"])
			temp_dict["id"]="{}".format(i[1]["id"])
			temp_dict["creation_time"]="{}".format(i[1]["creation_time"])
			temp_dict["indicator"]="{}".format(i[1]["indicator_id"])
			total.append(temp_dict)

		return total,200


	@api.doc(description="Add a new indicator")
	@api.response(201, 'Created')
	@api.param('indicator_id', 'An indicator_id according to http://api.worldbank.org/v2/indicators')
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('indicator_id',type=str,required=True)
		args = parser.parse_args()
		indicator_id = args.get("indicator_id")

		database_file="z5133109.db"
		table_name="assignment2"

		qu_df=read_from_sqlite(database_file, table_name)

		if qu_df is not None and indicator_id in qu_df["indicator_id"].values:
			temp_df=qu_df[qu_df["indicator_id"]==indicator_id]

			return { "uri":"/indicators/{}".format(int(temp_df["id"])),
					 "id":"{}".format(int(temp_df["id"])),
					 "indicator_id":"{}".format(indicator_id),
					 "creation_time":"{}".format(temp_df["creation_time"].values[0])
			}, 233

		url="http://api.worldbank.org/v2/countries/all/indicators/"+indicator_id+"?date=2012:2017&format=json&per_page=1000"
		response=requests.get(url)
		data=response.json()

		if len(data)==1:
			return "indicator id doesn't exist in the data source", 404
		# {		single-data structure
  # 			"indicator": {
  #   			"id": "NY.GDP.MKTP.CD",
  #   			"value": "GDP (current US$)"
 	# 		},
  # 			"country": {
  #   			"id": "1A",
  #   			"value": "Arab World"
  # 		},
  # 			"countryiso3code": "ARB", it contain None value
  # 			"date": "2017",
  # 			"value": 2586506133266.57,
  # 			"unit": "", no-meaning value
  # 			"obs_status": "", meaningless value
  # 			"decimal": 0, meaningless value
		# }
		entries=[]
		for i in data[1]:
			if not i["value"]:
				continue
			entry_dic=dict()
			entry_dic["country_value"]=i["country"]["value"]
			entry_dic["date"]=i["date"]
			entry_dic["value"]=i["value"]
			entries.append(entry_dic)

		atom_collection={}
		atom_collection["id"]=0
		atom_collection["indicator_id"]=indicator_id
		atom_collection["indicator_value"]=data[1][0]["indicator"]["value"]
		atom_collection["creation_time"]=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-7] + 'Z'
		atom_collection["entries"]=json.dumps(entries)

		#df=pd.DataFrame(atom_collection,index=[1])

		if qu_df is None:
			atom_collection["id"]=1
			df=pd.DataFrame(atom_collection,index=[1])
			write_in_sqlite(df, database_file, table_name)
			return { "uri":"/indicators/{}".format(atom_collection["id"]),
					 "id":"{}".format(atom_collection["id"]),
					 "indicator_id":"{}".format(indicator_id),
					 "creation_time":"{}".format(atom_collection["creation_time"])
			}, 201
		else:
			last_id=qu_df["id"].values[-1]
			atom_collection["id"]=last_id+1
			df=pd.DataFrame(atom_collection,index=[1])
			query_df=qu_df.append(df, ignore_index=True)
			write_in_sqlite(query_df, database_file, table_name)
			return { "uri":"/indicators/{}".format(atom_collection["id"]),
					 "id":"{}".format(atom_collection["id"]),
					 "indicator_id":"{}".format(indicator_id),
					 "creation_time":"{}".format(atom_collection["creation_time"])
			}, 201


@api.route('/collections/<int:id>')
@api.response(200,"OK")
@api.param('id')
class Q2(Resource):
	def delete(self,id):
		parser = reqparse.RequestParser()
		# parser.add_argument('id',type=int)
		# args = parser.parse_args()
		# query_id = args.get("id")
		query_id=id

		database_file="z5133109.db"
		table_name="assignment2"

		query_df=read_from_sqlite(database_file,table_name)
		if query_df is None:
			return "Database does not exist!", 404

		if query_id in query_df["id"].values:
			temp_df=query_df[query_df["id"]!=query_id]
			write_in_sqlite(temp_df, database_file, table_name)
			return { "message":"The colelction {} was removed from the database!".format(query_id),
					 "id":"{}".format(query_id)
			}, 200
		else:
			return "Data does not exist!",404


	def get(self,id):
		query_id=id

		database_file="z5133109.db"
		table_name="assignment2"

		query_df=read_from_sqlite(database_file,table_name)
		if query_df is None:
			return "Database does not exist!", 404

		if query_id not in query_df["id"].values:
			return "Id doesn't exist!", 404
		
		temp_df=query_df[query_df["id"]==query_id]
		rel_dict=dict()

		rel_dict["id"]="{}".format(temp_df["id"].values[0])
		rel_dict["indicator"]="{}".format(temp_df["indicator_id"].values[0])
		rel_dict["indicator_value"]="{}".format(temp_df["indicator_value"].values[0])
		rel_dict["creation_time"]="{}".format(temp_df["creation_time"].values[0])
		rel_dict["entries"]= json.loads(temp_df["entries"].values[0])

		return rel_dict, 200

@api.route('/collections/<int:id>/<int:year>/<string:country>')
@api.response(200,"OK")
# @api.param('id')
# @api.param('year')
# @api.param('country')
class Q5(Resource):
	def get(self,id,year,country):

		query_id=id

		database_file="z5133109.db"
		table_name="assignment2"

		query_df=read_from_sqlite(database_file,table_name)
		if query_df is None:
			return "Database does not exist!", 404

		if query_id not in query_df["id"].values:
			return "Data doesn't exist!", 404

		temp_df=query_df[query_df["id"]==query_id]

		rel_dict=dict()
		rel_dict["id"]="{}".format(temp_df["id"].values[0])
		rel_dict["indicator"]="{}".format(temp_df["indicator_id"].values[0])

		temp_jsdata=json.loads(temp_df["entries"].values[0])

		for i in temp_jsdata:
			if int(i["date"])==year and i["country_value"]==country:
				rel_dict["country"]="{}".format(i["country_value"])
				rel_dict["year"]="{}".format(i["date"])
				rel_dict["value"]="{}".format(i["value"])
				break

		return rel_dict, 200


parser = reqparse.RequestParser()
parser.add_argument('q',type=str,nullable=True)	
@api.route('/collections/<int:id>/<int:year>')
@api.response(200,"OK")
class Q6(Resource):
	@api.param("q","+N (or simply N) or -N")
	@api.expect(parser, validate=True)
	def get(self,id,year):
		args = parser.parse_args()
		query_act = args.get("q")

		query_id=id

		database_file="z5133109.db"
		table_name="assignment2"

		query_df=read_from_sqlite(database_file,table_name)
		if query_df is None:
			return "Database does not exist!", 404

		if query_id not in query_df["id"].values:
			return "Data doesn't exist!", 404
			
		if query_act is not None:
			if check_number(query_act) is False:
				return "Invalid input of q!", 404

		rel_dict=dict()
		temp_df=query_df[query_df["id"]==query_id]

		rel_dict["indicator"]="{}".format(temp_df["indicator_id"].values[0])
		rel_dict["indicator_value"]="{}".format(temp_df["indicator_value"].values[0])

		if query_act is None:
			entries=[]
			rel_dict["entries"]=entries
			return rel_dict, 200
		else:

			temp_jsdata=json.loads(temp_df["entries"].values[0])

			col_list=["value"]
			asd_list=[]

			if query_act[0].isdigit():
				asd_list.append(False)
			else:
				if query_act[0]=="+":
					asd_list.append(False)
				else:
					asd_list.append(True)
			flag_num=int(query_act.strip("+-"))

			it_df=pd.DataFrame.from_records(temp_jsdata)
			it_df=it_df[it_df["date"]==str(year)]
			it_df=it_df.sort_values(by=col_list,ascending=asd_list)

			sp_df=it_df[:flag_num]

			entries=[]
			for i in sp_df.iterrows():
				temp_dict=dict()
				temp_dict["country"]="{}".format(i[1]["country_value"])
				temp_dict["value"]="{}".format(i[1]["value"])
				entries.append(temp_dict)
			rel_dict["entries"]=entries

			return rel_dict, 200



if __name__ == '__main__':
	app.run(debug=True)
