from .base import Base


class Exporter:
    __export_class = None

    def __init__(self, export_class: Base):
        self.__export_class = export_class()

    def export(self, data):
        return self.__export_class.export(data=data)
