from abc import ABC


class Base(ABC):
    def export(self, data):
        raise NotImplementedError("Method not implemented")

    def response(self, file):
        raise NotImplementedError("Method not implemented")
