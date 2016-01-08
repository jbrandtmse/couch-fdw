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
create foreign table couch_specific_couchdb_view (
	"key" character varying ,
	"value" character varying,
	"_runtime_error" character varying,
	"p_startkey" character varying,
	"p_endkey" character varying,
	"p_group" character varying,
	"p_group_level" character varying,
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



   [ccs]: <http://nicolaisi.github.io/couchquery/>
   [sjs]: <https://pypi.python.org/pypi/simplejson/>
   [mcs]: <http://multicorn.org>