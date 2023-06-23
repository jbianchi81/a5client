# a5 api client library

## Install

    $ git clone https://github.com/jbianchi81/a5client.git
    $ cd a5client
    $ python3 -m venv .
    $ source bin/activate
    $ python3 -m pip install .
    $ python3 create_dirs.py

## Use

    $ python3
    >>> import a5client.a5 as a5
    >>> client = a5.Crud({"url": "A5_API_ENDPOINT_URL", "token": "YOUR_PERSONAL_TOKEN"})
    >>> series = client.readSeries(var_id=2)
    >>> data = client.readSerie(29, "2020-01-01T03:00:00.000Z", "2021-01-01T03:00:00.000Z")
