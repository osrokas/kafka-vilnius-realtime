# Vilnius GPS Coordinates of Vilnius Public Transport GPS Coordinates
https://www.stops.lt/vilnius/gps_full.txt

# To create Docker image run:
```
docker compose up -d
```

# To run the app locally, you can use the following command:
```
docker run -i -t <your_docker_image_name> /bin/bash
```

# To run the producer and consumer, you can use the following commands:
```
python -m producers.gps_data
```

# To run the consumer, you can use the following command:
```
python -m consumers.gps_data
```

# To run app locally, you can use the following command:
```
streamlit run app.py
```

# Add postgis extension to the database:
```
CREATE EXTENSION postgis;
```
# Add postgis_topology extension to the database:
```
CREATE EXTENSION postgis_topology;
```

# To create alembic versioning directory:
```
alembic init alembic
```

# Add geoalchemy2 to alembic/script.py.mako:
```
import geoalchemy2
```

# To create a new migration, run the following command:
```
alembic revision --autogenerate -m "migration message"
```
# To apply the created migration, use the command:
```
alembic upgrade head
```