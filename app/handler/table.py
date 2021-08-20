import json

from app.exceptions import PayloadError
from app.manager import Exporter

class TableHandler:
    @classmethod
    def execute(cls, df, schema, payload, uid):
        action = payload['action']
        params = payload.get('inputParams', [{}])
        if action == "export":
            show_index = params[0].get('showIndex', False)
            file_path = Exporter.to_csv(
                df=df,
                show_index=show_index,
                schema=schema,
                uid=uid)
        else:
            raise PayloadError("action", action)
        return json.dumps({"file_path": file_path})

    @classmethod
    def undo(cls, df, schema):
        if len(schema['ActionSequence']):
            action_details = schema['ActionSequence'][-1]
            action = action_details['action']
            keep_original = True
            new_schema = remove_indexes = indexes = list()

            if action in ["upperCase", "lowerCase", "camelCase", "substitute",
                          "validate"]:
                indexes = action_details['indexes']
                remove_indexes = [i + index for i, index in
                                  zip(range(1, len(indexes) + 1), indexes)]
                keep_original = action_details.get('keeOriginal',
                                                   keep_original)
                df, new_schema = cls._remove(df=df, indexes=indexes,
                                             remove_indexes=remove_indexes,
                                             keep_original=keep_original)
            elif action == "concatenate":
                indexes = action_details['indexes']
                remove_indexes = [max(indexes) + 1]
                keep_original = action_details.get('keeOriginal',
                                                   keep_original)
                df, new_schema = cls._remove(df=df,
                                             indexes=indexes,
                                             remove_indexes=remove_indexes,
                                             keep_original=keep_original)
            elif action == "changeType":
                indexes = action_details['indexes']
                schema = action_details['schema']
                for index, schema_value in zip(indexes, schema):
                    _schema = {
                        'index': index,
                        'customType': schema_value['customType']
                    }

                    new_schema.append(_schema)
            elif action == "remove":
                indexes = action_details['indexes']
                for index in indexes:
                    _schema = {
                        "index": index,
                        "visible": True,
                    }
                    new_schema.append(_schema)
            elif action == "formatDateTime":
                indexes = action_details['indexes']
                schema = action_details['schema']
                for index, schema_value in zip(indexes, schema):
                    _schema = {
                        'index': index,
                        'datetimeFormat': schema_value['datetimeFormat']
                    }
                    new_schema.append(_schema)
            elif action == "rename":
                indexes = action_details['indexes']
                schema = action_details['schema']
                for index, schema_value in zip(indexes, schema):
                    _schema = {
                        "index": index,
                        "displayNames": schema_value['displayNames'],
                    }
                    new_schema.append(_schema)
            return df, new_schema, indexes, remove_indexes

    @staticmethod
    def _remove(df, indexes=None, remove_indexes=None, keep_original=True):
        """TODO: update pandas dtype associated with custom type
        """

        new_schema = []
        if indexes:
            df.drop(df.columns[remove_indexes], axis=1, inplace=True)
        if not keep_original:
            for index in indexes:
                _schema = {
                    "index": index,
                    "visible": True,
                }
                new_schema.append(_schema)
        return df, new_schema
