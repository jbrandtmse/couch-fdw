# coding=utf-8
from multicorn import ForeignDataWrapper
from couchquery import Database
import simplejson as json
import traceback
import sys

"""
Method to insert the parameters from quals object in the record output
"""


def insert_quals_in_output(line, quals):
    for qual in quals:
        # if qual.field_name.startswith('p_'):
        line[qual.field_name] = qual.value


"""
Class that wraps postgresql calls to couchdb views/documents
"""


class CouchDBForeignDataWrapper(ForeignDataWrapper):
    """
    Reference to p_ parameters

    https://wiki.apache.org/couchdb/HTTP_view_API
    """

    def __init__(self, options, columns):
        super(CouchDBForeignDataWrapper, self).__init__(options, columns)
        self.columns = columns
        self.options = options
        # if HOST not provided, assumes that is localhost
        self.host = self.options.pop('host', 'http://localhost:5984')

        # if target view not provided, assumes that is the 'all' view
        self.target_view = self.options.pop('target_view', 'all')
        self.has_sub_package = '.' in self.target_view
        self.sub_package = self.target_view.split('.')[0] if self.has_sub_package else None
        self.target_view = self.target_view.split('.')[1] if self.has_sub_package else self.target_view

        # the database to access
        self.database = self.options.pop('database', '')
        self.connection_string = self.host + self.database

    def execute(self, quals, columns):

        # the row to return
        line = {}

        # noinspection PyBroadException
        try:
            # instantiate the database object
            db = Database(self.connection_string)

            debug = ''

            view_container = db.views

            # if the call is for a view
            if self.has_sub_package:

                # build the params object that will be passed to couchdb call, filled with default parameters
                params = {'startkey': None, 'endkey': {}, 'group': False, 'reduce': False}

                # check provided keys against expected keys
                provided_keys = [int(qual.field_name.split('_')[1]) for qual in quals if qual.field_name.startswith('key_')]

                expected_keys = [number for number in range(len(provided_keys))]

                error = False
                # if the provided keys not fitting with expected keys, return a blank line with the error description
                if not all(k in expected_keys for k in provided_keys):
                    error = True
                    line['_runtime_error'] = "Keys doesn't follow a correct sequence key_0 ... key_1 ... " + str(provided_keys) + ' ' + str(expected_keys)
                    insert_quals_in_output(line, quals)
                    yield line

                # and then get out
                if error is True:
                    return

                last_used_index = -1

                # clean and replace if needed the default parameters
                startkey = {}
                endkey = {}

                # portion of code to build the keys object to pass as parameters to the view call
                for qual in quals:
                    # deal with named key parameters
                    if qual.field_name.startswith('key_'):
                        last_used_index = qual.field_name.split('_')[1]
                        startkey[last_used_index] = qual.value
                        endkey[last_used_index] = qual.value
                    # deal with other parameters
                    if qual.field_name.startswith('p_'):
                        params[qual.field_name.split('_')[1]] = eval(qual.value) if qual.value != '' else qual.value

                # if provided a single key
                if last_used_index != -1:

                    params['startkey'] = []
                    params['endkey'] = []

                    for i in range(0, int(last_used_index)):
                        params['startkey'].append(startkey[str(i)])
                        params['endkey'].append(endkey[str(i)])

                    params['endkey'].append({})

                view_container = getattr(view_container, self.sub_package)

                # do the view call with the params object as parameters
                result = getattr(view_container, self.target_view)(**params)
            else:
                # do the 'all' call
                result = getattr(view_container, self.target_view)()

            # this case covers views call
            if self.has_sub_package:
                # read the return from the call and fill the line object with the values
                for key, value in result.items():
                    # deal with the 'value'
                    line['value'] = value if not isinstance(value, dict) else json.dumps(value)
                    # deal with the 'key'
                    line['key'] = key

                    # split the 'key' into named output values
                    for column_name in columns:
                        if column_name.startswith('key_'):
                            column_index = int(column_name.split('_')[1])
                            parsed_key = eval(str(key))
                            # and then fill the correct output column
                            line[column_name] = parsed_key[column_index]

                    # insert the quals into output
                    insert_quals_in_output(line, quals)
                    # yield the line to the postgresql call
                    yield line

            # this case covers the 'all' call
            else:
                # set the column values
                for record in result:
                    for column_name in columns:
                        # if a '_doc' columm is provided, put the jsonified record to output column
                        if column_name == '_doc':
                            line[column_name] = json.dumps(record)
                        else:
                            if column_name == '_runtime_error':
                                line[column_name] = debug
                            else:
                                line[column_name] = record.get(column_name, None) if record is not None else None

                    # insert the quals into output
                    insert_quals_in_output(line, quals)
                    # yield the line to the postgresql call
                    yield line
        except:
            # in case of any exception, insert the exception in the column _runtime_error
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # insert the quals into output
            insert_quals_in_output(line, quals)

            # format the message
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            # if column _runtime_error is defined, set the formatted exception in the column
            if '_runtime_error' in self.columns:
                line['_runtime_error'] = error_message
                yield line
