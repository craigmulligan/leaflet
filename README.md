# Leaflet

> Random weekly personalized plant based recipes

Getting started

# Init virtual-env.

```
poetry shell
```

# Install dependencies 

```
poetry install
```

# Run postgres

```
docker-compose up -d
```

Then run any of the commands below.

# Run test suite. 
```
flask dev test 
```

# Run test suite in watch mode.
```
flask dev test --watch
```

# Run dev server and worker

```
flask dev run
```

# Run dev server 
```
flask dev server
```

# Run dev worker 
```
flask dev worker 
```

# Format code
```
flask dev fmt 
```

# Type-check code
```
flask dev mypy
```

TODO:

* cleanup session use.
* cleanup auth tests. 
