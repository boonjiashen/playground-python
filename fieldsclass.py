import dataclasses
from typing import Optional


class Field(str):
    """Represents an attribute of fieldsclass

    If the field has values, also exposes the individual and set of values, e.g.,

    >>> my_field = Field("my_field", values=["val1", "val2"])
    >>> my_field.values
    {'val2', 'val1'}
    >>> my_field.val.val1
    'val1'
    >>> my_field.val.val2
    'val2'
    """
    class Val:
        pass

    def __new__(cls, obj, values=None):
        ret = super().__new__(cls, obj)
        if values:
            ret.values = set(values)
            ret.val = Field.Val()
            for val in values:
                setattr(ret.val, val, val)

        return ret


@dataclasses.dataclass
class FieldPlaceholder:
    values: Optional[list[str]] = None


def _field(*args, **kwargs):
    return FieldPlaceholder(*args, **kwargs)


def fieldsclass(clazz: type):
    """Decorates a class into a collection of fields, and optionally the values of those fields

    Useful to avoid repeating the same strings in the codebase, allows catching typos at
    test time as long as code coverage is high.

    Intended for constructing boto3 query objects and parsing its response objects.

    >>> @fieldsclass
    ... class F:
    ...     Status = fieldsclass.field(values=["Succeeded", "Failed"])
    ...     result = fieldsclass.field()
    ...     platform = fieldsclass.field(values=["arm64", "amd64"])
    ...
    >>> F.Status
    'Status'
    >>> F.Status.values
    {'Succeeded', 'Failed'}
    >>> F.Status.val.Succeeded
    'Succeeded'
    >>> F.Status.val.Failed
    'Failed'
    >>> F.result
    'result'
    >>> F.result.values
    Traceback (most recent call last):
      File "<ipython-input-45-eeaf69024f6d>", line 1, in <module>
        F.result.values
    AttributeError: 'Field' object has no attribute 'values'
    """
    class Decorated(clazz):
        pass
    for k, v in clazz.__dict__.items():
        if not isinstance(v, FieldPlaceholder):
            continue
        setattr(Decorated, k, Field(k, values=v.values))
    return Decorated


fieldsclass.field = _field


@fieldsclass
class F:
    myfield1 = fieldsclass.field()
    myfield2 = fieldsclass.field(values=["val1", "val2"])
    Status = fieldsclass.field(values=["PermanentFailure", "Succeeded"])


if __name__ == "__main__":

    for k, v in F.__dict__.items():
        if isinstance(v, FieldPlaceholder):
            print(k, v)
    print(F.__dict__)
    print(f"{F.myfield1=}")
    print(f"{F.myfield2=}")
    print(f"{F.myfield2.values=}")
    print(f"{F.myfield2.val.val1=}")
    print(f"{F.myfield2.val.val2=}")
    print(f"{F.Status.values=}")
    print(f"{F.Status.val.PermanentFailure=}")
    print(f"{F.Status.val.Succeeded=}")
    print(F)
