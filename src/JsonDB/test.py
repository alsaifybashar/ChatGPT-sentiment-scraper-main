import json

from dataclasses import dataclass,asdict,is_dataclass

@dataclass
class T:
    a:int

    def to_json(self):
        return asdict(self)

    @staticmethod
    def from_json(json_dct):
      return T(json_dct["a"])




class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if is_dataclass(o):
                return asdict(o)
            return super().default(o)

t = T(1)
j = json.dumps(t, cls=EnhancedJSONEncoder)

print(j.__repr__())

n_t = json.loads(j, object_hook=T.from_json)
#print(n_t.__repr__())
print(n_t)
