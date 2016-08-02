import yaml, box

#test
with open("tests/elevator.yaml", 'r') as stream:
    try:
        b = box.Box(yaml.load(stream)['statechart'])
        b.export()
    except yaml.YAMLError as exc:
        print(exc)
