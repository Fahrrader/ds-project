# ds-project: Distributed Systems File Sharing Application

Made by 3rd year students of Innopolis University:
- Farhad Khakimov, SE-02
- Oydinoy Zufarova, SE-01

## Installation guide

There are three options available, varying from easy to not-so-much:
1. Download *client.py* or *docker-compose.yml* from the 'client' folder.
Launch using `python3 client.py [server IP]` or `docker-compose up`. 
Make sure you have access to the terminal, and don't forget to initialize your directory.
You can give the server address yourself as an argument in the command line, 
or use the default one, leading to an [AWS EC2 instance](ec2-50-19-187-186.compute-1.amazonaws.com).
1. Download *ds-project.yml* and *client.py*, launch with `docker stack deploy -c ds-project.yml [name of your application]`
and `python3 client.py [server IP]`. You can use that with docker machines, for example.
1. Publish that to AWS instances. 
    1. Where you want your naming node to be, type in the following command: `docker swarm init --advertise-addr <MANAGER-IP>` to set that as the manager node.
    1. Put there the *docker-compose.yml* for the naming server and launch it with `docker service create --replicas 1 --name ds-p fahrrader/ds-project-name-server python3 name_server.py`
    1. Next, for each worker server, place there the *docker-compose.yml* and launch it with the command you've been given after step 1 (naming server).
    1. Put there the *docker-compose.yml* for the storage server and launch it with `docker service create --replicas 10 --name ds-p fahrrader/ds-project-storage-server python3 storage_server.py [MANAGER-IP]`
    1. Do the same with other worker nodes.
