import time
from typing import Dict


class DataItem:
    # 数据状态 start/running/finish
    status = "start"
    # 数据源
    origin = ""
    # 数据
    data = None
    # 更新时间
    update_time = time.time()

    def __init__(self, data=None, status="start", origin=""):
        self.data = data
        self.status = status
        self.origin = origin

    def to_dict(self):
        return {
            "status": self.status,
            "origin": self.origin,
            "data": self.data,
            "update_time": self.update_time
        }


class MemoryStorage:

    def __init__(self, ttl=1800):
        self.data: Dict[str, DataItem] = {}
        self.ttl = ttl

    def update(self, gen_id, **kwargs):
        item = self.data.get(gen_id, None)
        if not item:
            item = DataItem(**kwargs)
        else:
            if kwargs.get("data"):
                item.data = kwargs.get("data")
            if kwargs.get("status"):
                item.status = kwargs.get("status")
            if kwargs.get("origin"):
                item.origin = kwargs.get("origin")
        item.update_time = time.time()
        self.data[gen_id] = item
        # 触发清空历史记录操作 防止oom
        self._refresh()

    def get_data_item(self, gen_id) -> DataItem:
        return self.data.get(gen_id)

    def _refresh(self):
        _remove_id = []
        for gen_id in self.data.keys():
            item = self.data.get(gen_id)
            if time.time() - item.update_time > self.ttl:
                _remove_id.append(gen_id)
        for gid in _remove_id:
            self.data.pop(gid)
