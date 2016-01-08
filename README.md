```
                                          oooo                 .o88o.       .o8                   
                                          `888                 888 `"      "888                   
 .ooooo.   .ooooo.  oooo  oooo   .ooooo.   888 .oo.           o888oo   .oooo888  oooo oooo    ooo 
d88' `"Y8 d88' `88b `888  `888  d88' `"Y8  888P"Y88b           888    d88' `888   `88. `88.  .8'  
888       888   888  888   888  888        888   888  8888888  888    888   888    `88..]88..8'   
888   .o8 888   888  888   888  888   .o8  888   888           888    888   888     `888'`888'    
`Y8bod8P' `Y8bod8P'  `V88V"V8P' `Y8bod8P' o888o o888o         o888o   `Y8bod88P"     `8'  `8'     
```                                                                                                  
                                                                                                  
# couch-fdw
 couch-fdw is a simple Foreign Data Wrapper to access (read-only) CouchDB databases inside PostgreSQL
 
## Major Feature
  - Query mapreduce views with SQL ```SELECT```statements with parameters like ```startkey, endkey, reduce, group, grouplevel, limit```
  
## TBI
  - Write support
  - Dynamic queries (create a CouchDB temporary view at runtime)  support
 
## Dependencies
  - [multicorn][mcs]
  - [simplejson][sjs]
  - [couchquery][ccs]
 
## Installation
  - ```git clone https://github.com/mdaparte/couch-fdw.git```
  - ```python setup.py install```

## Usage

###  #1 Defining the Foreign Data Wrapper extension
 - Once in the postgresql you have to reference the extension and the foreign data wrapper like the code above 
```sql
create extension if not exists multicorn;
drop server if exists multicorn_couchdb cascade;

-- THIS LINE CREATES THE COUCHDB FOREIGN DATA WRAPPER IN THE DATABASE
create server multicorn_couchdb foreign data wrapper multicorn
options (
  wrapper 'couchfdw.CouchDBForeignDataWrapper'
);
```

### #2 Creating the foreign tables
 - With the extension referenced, the next step is to build the foreign tables, this way (to reference the whole database, not a specific view):
```sql
create foreign table couch_all (
	"_id" character varying ,
	"_rev" character varying ,
	"_doc" json,
	"_runtime_error" character varying
	
) server multicorn_couchdb options(
	host 'http://localhost:5984/',
	database   'databasename',
	target_view 'all'
);
``` 
 - or this way (to reference a mapreduce view in particular):
```sql
create foreign table couch_mapreduceview (
	"key" character varying ,
	"value" character varying,
	"_runtime_error" character varying,
	"p_startkey" character varying,
	"p_endkey" character varying,
	"p_group" character varying,
	"p_group_level" integer,
	"p_reduce" character varying,
	"key_0_key_name" integer,
	"key_1_key_name" integer,
	"key_2_key_name" integer
) server multicorn_couchdb options(
	host 'http://localhost:5984/',
	database   'databasename',
	target_view 'view_container.mapreduceview'
);
```
 - NOTE : The ```p_```, ```key_N``` and ```_runtime_error``` columns are special.
 
### #3 Querying the foreign tables
 - You can query the foreign tables following some basic rules described below:
 1. the parameters that will be passed to the CouchDB are the columns (defined in the table) with the pattern starting with ```p_``` (like ```p_group, p_reduce, p_grouplevel``` and so on);
 2. The ```startkey``` and ```endkey``` can be filled manually or inferred from the ```key_N``` columns;
 3. When querying and using the ```WHERE``` clause, the special ```key_N``` columns will be converted to the ```startkey``` and ```endkey``` properties, so you yave to fill the key columns following the order ```key_0_... key_1_... ```, otherwise, the query will not run and the wrapper will fill the ```_runtime_error``` column with the description of the error.
 

```sql

  select * from couch_mapreduceview 
  where
  key_0_key_name = 2 and key_1_key_name = 63 and key_2_key_name = 27
  and p_group = 'True' and p_reduce = 'True' and p_group_level = 3
  
``` 
 
## Final Considerations

 - This is a 5 hour project, that I've started cause i didn't succeded to found a simple solution to do this. Feel free to ask, to comment and TO USE!! 
 - Pull requests are welcome! 


   [ccs]: <http://nicolaisi.github.io/couchquery/>
   [sjs]: <https://pypi.python.org/pypi/simplejson/>
   [mcs]: <http://multicorn.org>