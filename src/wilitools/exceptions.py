class UnexistRecord(Exception):
    def __init__(self, table:str, columns:list[str]=[], values:list=[]):
        wheres = []
        for c, v in zip(columns, values):
            wheres.append("{}={}".format(c, v))
        super().__init__("table " + table + " has no record where " + ", ".join(wheres))