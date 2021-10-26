class ConnectionManager:
    def __init__(self, obj):
        self.obj = obj

    def close(self):
        if "close" in [method_name for method_name in dir(self.obj)
                       if callable(getattr(self.obj, method_name))]:
            self.obj.close()
        elif "inner" in vars(self.obj):
            ConnectionManager(self.obj.inner).close()
        elif "session" in vars(self.obj):
            ConnectionManager(self.obj.session).close()
        else:
            raise Exception("could not close.")
