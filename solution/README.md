# Run the project with docker-compose (Linux)

On the terminal run (can be VSCode Terminal):
```
cd solution
make build
make up
```

- Make sure of the ports be open: 8100:5434:3000

In a new tab run followings command:

```
make migrate
```
at last in the same tab run:
```
make test
```

# Run the project without docker-compose (Linux)

On the terminal run (can be VSCode Terminal):
```
cd solution
virtualenv -p python3 .venv/
source solution/.venv/bin/activate
cd src
pip install -r requirements.txt
```

Now we change the DATABASE=default for sqlite3:

in development.py comment out the following lines like this:

```
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'backend_challenge',
#        'USER': 'backend_challenge',
#        'PASSWORD': '9quxdHbm',
#        'HOST': 'db',
#        'PORT': '5432',
#    }
#}
```

Now we can run the migrate command

```
python manage.py migrate
```

with this we can run and test the project

```
python manage.py runserver 0.0.0.0:8100
```
or
```
python manage.py test
```

About the API:

| URL                                |  Method  | Params  | Description      |
|------------------------------------|:--------:|:--------|-----------------|
| /api/v1/cars/                      |    GET   |    -    | List all cars         |
| /api/v1/cars/create_car            |    POST  |    -    | Create a new car and return his status |
| /api/v1/cars/{id}/                 |    GET   |    -    | Get one car                  |
| /api/v1/cars/{id}/create_tyre/     |    POST  |    -    | Create or replace tyres      |
| /api/v1/cars/{id}/get_car_status/  |    POST  |    -    | Get car status               |
| /api/v1/cars/{id}/maintenance/     |    POST  |{"replace_part": "_tyre"} <br/> {"replace_part": "_fuel"}   | Return info abouts the tyres or percetage of fuel      |
| /api/v1/cars/{id}/refuel/          |    POST  |{"quantity": 32}  | Return the current percetage of the car tank  |
| /api/v1/cars/{id}/trip/            |    POST  |{"distance": 282.2} | Return the Car and Trip infos      |
| /api/v1/tyres/                     |    GET   |    -             | List all tyres           |
| /api/v1/tyres/{id}/                |    GET   |    -             | Get one tyre             |
| /api/v1/tyres/create_tyre/         |    POST  |    -             | Create a new Tyre        |
| /api/v1/tyres/available/           |    GET   |    -             | List all available tyres |
| /api/v1/tyres/discarded/           |    GET   |    -             | List all discarded tyres |
| /api/v1/tyres/in_use/              |    GET   |    -             | List all in use tyres    |
