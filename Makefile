clean:
	rm -rf build dist
	rm -rf __pycache__ **/__pycache__
	rm -rf *.pyc **/*.pyc
	rm -rf jsonfeed_wrapper.egg-info

appengine-example:
	python3 examples/appengine.py

cloud-function-example:
	functions-framework --source "examples/cloud-function.py" --target "main"