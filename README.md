# py-auth-api

A simple authentication API using Sanic, MongoDB and bcrypt.

## First run
```
pip3 install -r requirements.txt
```
You'll need to create a `config.json` file in the same directory with the following contents:
```json
{
  "MONGO_URL": "<url here>"
}
```
The default port is `6969`.


## Starting the API
```
python3 start.py
```
You're all set!

## But why?
I searched far and wide for something like this but couldn't find anything. So I did it myself.
Enjoy.
