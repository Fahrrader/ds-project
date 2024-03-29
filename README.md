# ds-project: Distributed Systems File Sharing Project
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
1. Publish that to AWS instances. Don't forget to allow incoming connection through at least ports 12607 and 2377 - for Docker. 
    1. Where you want your naming node to be, type in the following command: `docker swarm init --advertise-addr <MANAGER-IP>` to set that as the manager node.
    1. Put there the *docker-compose.yml* for the naming server and launch it with `docker service create --replicas 1 --name ds-p fahrrader/ds-project-name-server python3 name_server.py`
    1. Next, for each worker server, place there the *docker-compose.yml* and launch it with the command you've been given after step 1 (naming server).
    1. Put there the *docker-compose.yml* for the storage server and launch it with `docker service create --replicas 10 --name ds-p fahrrader/ds-project-storage-server python3 storage_server.py [MANAGER-IP]`
    1. Do the same with other worker nodes, if you so desire.

## Architectural diagrams 

You can find the architectural diagrams of the project by the links below, or inside the *image* folder: 

[The system overall architecture](https://github.com/Fahrrader/ds-project/raw/master/image/Overall_view.png)

[Naming and storage servers communication](https://github.com/Fahrrader/ds-project/raw/master/image/naming-storage.png)

[User and naming server communication](https://github.com/Fahrrader/ds-project/raw/master/image/User-naming.png)


## Description of communication protocols

In our project we use TCP/IP protocol. The communication between the servers takes place on port 19609 and between the servers and clients on port 12607.

Using the first one we send pings — heartbeats — from storage to naming servers and their notifications (such as create, write, delete file, replicate).

Using port 12607 we send and receive such data as commands (initialize, create directory/file, delete directory/file, etc.) and data (file names, storage servers ips,
file data etc.) from clients to servers and name server to storage server.

Interface between name server and client is most exhaustive, including all of the commands. Often when working with directories or file information, name server will output the data stored on it — including the file structure and minimal amount of attributes about the files themselves.
Storage servers, however, have only four types of messages to look out for, apart from their heartbeats: *'create', 'write', 'read', 'delete'*. 
