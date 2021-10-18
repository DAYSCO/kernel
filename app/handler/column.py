import pandas as pd
from app.days.actions import Actions
from app.exceptions import PayloadError


class ColumnHandler:
    @classmethod
    def execute(cls, ddf, payload):
        action = payload['action']
        params = payload.get('inputParams', [{}])
        _df = pd.DataFrame()

        try:
            indexes = params[0]['indexes']
        except:
            raise PayloadError("indexes", "None")

        if action in ["upperCase", "lowerCase", "camelCase"]:
            ddf, payload_res = Actions.format(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "changeType":
            ddf, payload_res = Actions.change_type(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "concatenate":
            ddf, payload_res = Actions.combine(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "remove":
            ddf, payload_res = Actions.remove(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "formatDateTime":
            ddf, payload_res = Actions.date_format(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "rename":
            ddf, payload_res = Actions.rename(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "substitute":
            ddf, payload_res = Actions.substitute(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        elif action == "validate":
            ddf, payload_res = Actions.validate(
                ddf=ddf,
                payload=payload,
                indexes=indexes)
        else:
            raise PayloadError("action", action)
        return ddf, payload_res