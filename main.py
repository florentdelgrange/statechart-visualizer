import svgwriter
from sismic import io, model
from structures.box import RootBox

# test
with open("tests/elevator.yaml", 'r') as stream:
    statechart = io.import_from_yaml(stream)
    assert isinstance(statechart, model.Statechart)

svgwriter.export(RootBox(statechart=statechart))