Resources
Created with
https://flask.palletsprojects.com/en/3.0.x/installation/
https://flask.palletsprojects.com/en/3.0.x/quickstart/


You will want to activate the virtual environment
D:\git\scribeserverpy\src>.venv\Scripts\activate
For windows use .\env\Scripts\activate

## Before starting we need to set up vertual env

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt  # Install all the libs.
```

## How to run

```
python -m flask run --host=0.0.0.0 -p 3000
```

## to update the requirements.txt

```
pip freeze > requirements.txt
```

`Note : this should be run after you remove the dependency from the env and run this in with in the env. `

## Here's how to share packages over python
https://stackoverflow.com/questions/42733542/how-to-use-the-same-python-virtualenv-on-both-windows-and-linux

pip freeze all libraries to a requirements.txt file.

pip freeze > requirements.txt

## Create the venv on each OS:

```
python -m venv env

source env/bin/activate

pip install -r requirements.txt # Install all the libs.
```

Note :-
Async Flask was installed using :- pip install 'flask[async]'