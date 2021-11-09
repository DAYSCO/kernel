from app.exceptions import IDNotFoundError


class ActiveWorkingFiles:
    def __init__(self):
        self.working_files = list()

    def __getitem__(self, uid):
        for _ in self.working_files:
            if _.uid == uid:
                return _
        raise IDNotFoundError(uid)

    @property
    def keys(self):
        return [_.uid for _ in self.working_files]

    def add(self, wf):
        try:
            self.remove(wf.uid)
        except:
            pass
        self.working_files.append(wf)

    def remove(self, uid):
        if uid in self.keys:
            self.working_files.remove(self[uid])
