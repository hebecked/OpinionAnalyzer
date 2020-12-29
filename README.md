# OpinionAnalyzer

In order to run the project you need to have docker and docker-compose installed on your local machine. If this pre-conditions are true, just run "./run.sh" inside the project folder from the command line, and the project should build itself and run dockerized on your machine.

Ports :8080 and :5432 need to be freed before building the project in order for Grafana and Postgres to be allocated in those ports. If you cannot free this ports, you need to change the ports then inside the docker-compose.yml so that the project can be started correctly. 

If you want to see the database relations you need to bind a database interface to the postgresql image (usually through the port :5432). 

If you want to see Dashboards or Grafana itself, just open your browser (tested with Chrome and Firefox only at the moment) and type into the url field "localhost:8080". This should lead you to Grafana. Grafana might also ask you for login details. Because we have not set the login-credentials so far, please use "admin:admin" as login. 

Common docker commands for a succesfull build:

"docker ps": To see which containers are running <br>
"docker volume list": To see the volumes created <br>
"docker logs {$container_name}": To see a snapshot of the current and past logs <br>
"docker logs --follow {$container_name}": To see all logs from the past, present and future <br>
"docker volume prune": To reset the database <br>
"docker system prune": To reset the network
 
