import os
import sys

import pandas as pd

from app.exceptions import PayloadError, MissingPayloadValueError


class Actions:

    @classmethod
    def execute(cls, ddf, payload):
        action = payload.get('action', '')
        indexes = list()
        _df = pd.DataFrame()

        if action == 'undo':
            payload = ddf.action_sequence[-1]

        params = payload.get('inputParams', [{}])
        if action != 'export':
            try:
                indexes = params[0]['indexes']
            except:
                raise PayloadError("indexes", "None")

        if action in ["upperCase", "lowerCase", "camelCase"]:
            ddf, payload_res = cls.format(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "changeType":
            ddf, payload_res = cls.change_type(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "concatenate":
            ddf, payload_res = cls.combine(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "remove":
            ddf, payload_res = cls.remove(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "formatDateTime":
            ddf, payload_res = cls.date_format(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "rename":
            ddf, payload_res = cls.rename(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "substitute":
            ddf, payload_res = cls.substitute(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "insertString":
            ddf, payload_res = cls.insert_string(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "validate":
            ddf, payload_res = cls.validate(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "undo":
            ddf, payload_res = cls.undo(
                ddf=ddf,
                payload=ddf.action_sequence[-1],
                indexes=indexes)
        elif action == "export":
            ddf, payload_res = cls.export(
                ddf=ddf,
                payload=payload)
        elif action == "updateValue":
            ddf, payload_res = cls.update_value(
                ddf=ddf,
                payload=payload,
                index=indexes)
        else:
            raise PayloadError("action", action)
        return ddf, payload_res

    @classmethod
    def validate(cls, ddf, payload, ids=None, indexes=None, legacy=True):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        try:
            valid_types = payload['inputParams'][0]['validType']
            if isinstance(valid_types, str):
                valid_types = [valid_types]
        except Exception:
            raise PayloadError("validType", "None")

        payload_res = dict()
        new_columns = list()
        for _index, _id in enumerate(ids):
            valid_type = valid_types[_index]
            if legacy:
                new_name = f"{ddf[_id].display_name}_validate"
                new_index = ddf[_id].index + 1
                series = ddf[_id].series
                new_name = ddf.new_column_name(new_name)
                series.name = new_name
                new_index = ddf.new_column(series=series,
                                           index=new_index)
                ddf[new_index].validate(custom_type=valid_type,
                                        legacy=False)
                new_columns.append(new_index)
            else:
                ddf[_id].validate(custom_type=valid_type, legacy=False)

        payload['newColumns'] = new_columns
        payload_res.update({"action": payload,
                            "new_columns": new_columns})
        return ddf, payload_res

    @classmethod
    def combine(cls, ddf, payload, ids=None, indexes=None):
        params = payload.get('inputParams', [{}])[0]
        try:
            join_char = params['joinChar']
        except:
            raise PayloadError("joinChar", "None")

        payload_res = dict()
        new_columns = list()

        if ids:
            indexes = [ddf[_id].index for _id in ids]
        elif indexes:
            pass
        else:
            raise MissingPayloadValueError('indexes')

        new_index = max(indexes) + 1
        first = True
        new_name = []
        new_series = pd.Series(["" for _ in range(ddf.row_count)])

        for index in indexes:
            if first:
                join_by = ""
            else:
                join_by = join_char
            new_series = new_series.str.cat(ddf[index].series,
                                            sep=join_by, na_rep='')
            first = False
            new_name.append(ddf[index].name)

        new_name.append("concatenate")
        new_name = "_".join(new_name)
        new_name = ddf.new_column_name(new_name)
        new_series.name = new_name
        i = ddf.new_column(series=new_series, index=new_index)
        new_columns.append(i)

        keep_original = params.get('keepOriginal', True)
        if not keep_original:
            for index in indexes:
                ddf[index].visible = False

        payload['newColumns'] = new_columns
        payload_res.update({"action": payload,
                            "new_columns": new_columns})
        return ddf, payload_res

    @classmethod
    def format(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        action = payload['action']
        params = payload.get('inputParams', [{}])[0]

        keep_original = params.get('keepOriginal', True)

        payload_res = dict()
        new_columns = list()

        for _id in ids:
            new_name = f"{ddf[_id].display_name}_{action}"
            new_index = ddf[_id].index + 1
            series = ddf[_id].series
            new_name = ddf.new_column_name(new_name)
            series.name = new_name
            new_index = ddf.new_column(series=series,
                                       index=new_index)
            ddf[new_index].format(casing=action)
            new_columns.append(new_index)

        if not keep_original:
            for _id in ids:
                ddf[_id].visible = False

        payload['newColumns'] = new_columns
        payload_res.update({"action": payload,
                            "new_columns": new_columns})
        return ddf, payload_res

    @classmethod
    def date_format(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        params = payload.get('inputParams', [{}])[0]

        keep_original = params.get('keepOriginal', True)

        try:
            new_datetime_format = params['datetimeFormat']
        except:
            raise PayloadError("datetimeFormat", "None")

        payload_res = dict()
        new_columns = list()

        for _id in ids:
            new_name = f"{ddf[_id].display_name}_date_format"
            new_index = ddf[_id].index + 1
            series = ddf[_id].series
            new_name = ddf.new_column_name(new_name)
            series.name = new_name
            new_index = ddf.new_column(series=series,
                                       index=new_index)
            ddf[new_index].date_format(date_format=new_datetime_format)
            new_columns.append(new_index)

        if not keep_original:
            for _id in ids:
                ddf[_id].visible = False

        payload['newColumns'] = new_columns
        payload_res.update({"action": payload,
                            "new_columns": new_columns})
        return ddf, payload_res

    @classmethod
    def substitute(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        params = payload.get('inputParams', [{}])[0]
        try:
            match_str = params.get('matchStr', " ")
        except:
            raise PayloadError("matchStr", "None")

        try:
            replace_str = params.get('replaceStr', " ")
        except:
            raise PayloadError("replaceStr", "None")

        keep_original = params.get('keepOriginal', True)

        payload_res = dict()
        new_columns = list()

        for _id in ids:
            new_name = f"{ddf[_id].display_name}_substitute"
            new_index = ddf[_id].index + 1
            series = ddf[_id].series
            new_name= ddf.new_column_name(new_name)
            series.name = new_name
            new_index = ddf.new_column(series=series,
                                       index=new_index)
            ddf[new_index].substitute(match_str=match_str,
                                      replace_str=replace_str)
            new_columns.append(new_index)

        if not keep_original:
            for _id in ids:
                ddf[_id].visible = False

        payload['newColumns'] = new_columns
        payload_res.update({"action": payload,
                            "new_columns": new_columns})

        return ddf, payload_res

    @classmethod
    def insert_string(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        params = payload.get('inputParams', [{}])[0]
        try:
            insert_str = params['insertString']
        except:
            raise PayloadError("insertString", "None")

        try:
            insert_index = params['insertIndex']
        except:
            raise PayloadError("insertIndex", "None")

        keep_original = params.get('keepOriginal', True)

        payload_res = dict()
        new_columns = list()

        for _id in ids:
            new_name = f"{ddf[_id].display_name}_updated"
            new_index = ddf[_id].index + 1
            series = ddf[_id].series
            new_name = ddf.new_column_name(new_name)
            series.name = new_name
            new_index = ddf.new_column(series=series,
                                       index=new_index)
            ddf[new_index].insert_string(insert_str=insert_str,
                                         insert_index=insert_index)
            new_columns.append(new_index)

        if not keep_original:
            for _id in ids:
                ddf[_id].visible = False

        payload['newColumns'] = new_columns
        payload_res.update({"action": payload,
                            "new_columns": new_columns})

        return ddf, payload_res

    @classmethod
    def remove(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        payload_res = dict()
        new_columns = list()

        for _id in ids:
            ddf[_id].update_visibility(False)

        payload_res.update({"action": payload,
                            "new_columns": new_columns})

        return ddf, payload_res

    @classmethod
    def rename(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        params = payload.get('inputParams', [{}])[0]
        try:
            display_names = params['displayNames']
        except:
            raise PayloadError("displayNames", "None")
        payload_res = dict()
        new_columns = list()
        schema = list()

        for _id, display_name in zip(ids, display_names):
            schema.append(ddf[_id].column_schema)
            display_name = ddf.new_column_name(name=display_name, limit=2)
            ddf[_id].change_display_name(display_name)

        payload['schema'] = schema
        payload_res.update({"action": payload,
                            "new_columns": new_columns})

        return ddf, payload_res

    @classmethod
    def change_type(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            ids = [ddf[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        params = payload.get('inputParams', [{}])[0]

        try:
            new_types = params['newType']
        except:
            raise PayloadError("newType", "None")

        payload_res = dict()
        new_columns = list()
        schema = list()

        for _id, new_type in zip(ids, new_types):
            schema.append(ddf[_id].column_schema)
            ddf[_id].update_custom_type(new_custom_type=new_type)

        payload['schema'] = schema
        payload_res.update({"action": payload,
                            "new_columns": new_columns})
        return ddf, payload_res

    @classmethod
    def undo(cls, ddf, payload, ids=None, indexes=None):
        if indexes:
            if not isinstance(indexes, list):
                indexes = [indexes]
            try:
                ids = [ddf[index].id for index in indexes]
            except:
                ids = [ddf._columns[index].id for index in indexes]

        if not ids:
            raise MissingPayloadValueError('indexes')

        action = payload['action']
        payload_res = dict()

        if action in ["upperCase", "lowerCase", "camelCase", "substitute",
                      "validate", "formatDateTime", "concatenate",
                      "insertString"]:
            remove_ids = [ddf[index].id for index in payload['newColumns']]

            for _id in remove_ids:
                ddf.remove_column(_id=_id)

            for index in indexes:
                ddf._columns[index].update_visibility(visible=True)

        elif action == "changeType":
            schemas = payload.get('schema', [])

            for _id, schema in zip(ids, schemas):
                custom_type = schema['customType']
                ddf[_id].update_custom_type(new_custom_type=custom_type)

        elif action == "remove":
            for index in indexes:
                ddf._columns[index].update_visibility(visible=True)

        elif action == "rename":
            schemas = payload.get('schema', [])

            for _id, schema in zip(ids, schemas):
                display_name = schema['customType']
                ddf[_id].change_display_name(new_name=display_name)

        elif action == "updateValue":
            _id = ddf[indexes].id
            old_value = payload.get('oldValue')
            row_index = payload['inputParams'][0].get('targetRowIndex')
            ddf[_id].update_value(
                row_index=row_index,
                new_value=old_value)

        payload_res.update({"action": payload})

        return ddf, payload_res

    @classmethod
    def export(cls, ddf, payload):
        params = payload.get('inputParams', [{}])
        try:
            file_format = params[0]['fileFormat']
        except:
            file_format = 'csv'

        try:
            show_index = params[0]['showIndex']
        except:
            show_index = False

        payload_res = dict()

        PLATFORM = sys.platform
        if PLATFORM in ['win32', 'cygwin', 'msys']:
            spl = "\\"
        elif PLATFORM in ['linux', 'linux2', 'darwin', 'os2', 'os2emx']:
            spl = "/"
        else:
            raise Exception(f"ERROR: sys.platform unknown {PLATFORM}")
        base_dir = f"{os.getcwd()}{spl}exports"
        try:
            os.mkdir(base_dir)
        except FileExistsError:
            pass

        file_path = f"{base_dir}{spl}"

        if file_format == 'csv':
            file_path = ddf.to_csv(destination=file_path,
                                   show_index=show_index)

        payload_res.update({
            "file_path": file_path})
        return ddf, payload_res

    @classmethod
    def update_value(cls, ddf, payload, ids=None, index=None):
        if index is not None:
            ids = ddf[index].id

        if not ids:
            raise MissingPayloadValueError('indexes')

        params = payload.get('inputParams', [{}])[0]
        try:
            row_index = params['targetRowIndex']
        except:
            raise PayloadError("targetRowIndex", "None")

        try:
            new_value = params['newValue']
        except:
            raise PayloadError("newValue", "None")

        payload_res = dict()

        old_value = ddf[ids].update_value(
            row_index=row_index,
            new_value=new_value)

        payload['oldValue'] = old_value
        payload_res.update({"action": payload,
                            "new_columns": []})

        return ddf, payload_res
