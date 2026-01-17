==========
Deployment
==========

This document describes important considerations for deploying Django FTP Server in a production environment.

Security
========

TLS/SSL Required
----------------

.. warning::

   Plain FTP transmits all data in clear text, including usernames and passwords. This means anyone who can intercept network traffic can read your credentials and file contents.

In production environments, you should always enable TLS/SSL encryption (FTPS). FTPS encrypts both the control and data connections, protecting credentials and file transfers from eavesdropping.

First, install the TLS dependencies::

   $ pip install django-ftpserver[tls]

This installs pyOpenSSL which is required for TLS/SSL support.

Configure TLS by specifying certificate and key files::

   $ python manage.py ftpserver --certfile=/path/to/cert.pem --keyfile=/path/to/key.pem

Or via settings::

   FTPSERVER_CERTFILE = '/path/to/cert.pem'
   FTPSERVER_KEYFILE = '/path/to/key.pem'

Firewall and Port Configuration
--------------------------------

FTP uses two types of connections:

* **Control connection**: The main port (default: 21) for commands and responses
* **Data connection**: Separate connections for actual file transfers

Active Mode vs Passive Mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^

FTP has two modes for establishing data connections:

**Active Mode (PORT)**

The client opens a port and tells the server to connect back to it. The server initiates the data connection from port 20 to the client's specified port.

.. mermaid::

   sequenceDiagram
       participant Client as FTP Client<br>(behind NAT)
       participant NAT as Client NAT/Firewall
       participant Server as FTP Server

       Client->>Server: Connect to port 21
       Server-->>Client: 220 Welcome

       Client->>Server: PORT 192,168,1,100,200,21<br>(internal IP, port 51221)
       Server-->>Client: 200 PORT command successful

       Client->>Server: LIST
       Note over Server,NAT: Server tries to connect<br>to client's internal IP
       Server-xNAT: Connect to 192.168.1.100:51221
       Note over Server,NAT: Connection blocked!<br>NAT doesn't allow<br>inbound connections

.. note::

   Active mode rarely works over the internet because:

   * The client is usually behind NAT, so the server cannot reach the client's private IP address
   * Client-side firewalls typically block incoming connections from the server

**Passive Mode (PASV)**

The server opens a port and tells the client to connect to it. The client initiates the data connection.

.. mermaid::

   sequenceDiagram
       participant Client as FTP Client<br>(behind NAT)
       participant Server as FTP Server

       Client->>Server: Connect to port 21
       Server-->>Client: 220 Welcome

       Client->>Server: PASV
       Server-->>Client: 227 Entering Passive Mode<br>(203,0,113,10,117,48)<br>= 203.0.113.10:30000

       Client->>Server: LIST
       Client->>Server: Connect to port 30000
       Note over Client,Server: Data connection established!<br>Client initiates all connections<br>(works with NAT)
       Server-->>Client: Directory listing

This mode works much better with NAT and firewalls because all connections are initiated by the client (outbound from the client's perspective).

.. important::

   For internet-facing FTP servers, **passive mode is strongly recommended**. Most modern FTP clients use passive mode by default.

Passive Mode Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

   FTP requires opening a range of ports for passive mode data connections, not just the control port.

You must configure and open a range of ports for passive mode::

   FTPSERVER_PASSIVE_PORTS = '30000-30100'

Make sure your firewall allows incoming connections on:

* The control port (e.g., 21 or your custom port)
* The entire passive port range (e.g., 30000-30100)

If the server is behind NAT, also configure the masquerade address so the server announces its public IP to clients::

   FTPSERVER_MASQUERADE_ADDRESS = 'your.public.ip.address'

Process Management
==================

.. important::

   It is strongly recommended to use a process management system that automatically restarts the FTP server process if it terminates unexpectedly.

Why Process Management is Important
------------------------------------

The FTP server is a long-running process that may terminate unexpectedly due to:

* Unhandled exceptions or bugs
* Out-of-memory conditions (OOM killer)
* Hardware failures or network issues
* Operating system updates or restarts

Without automatic restart, the FTP service will remain unavailable until someone manually restarts it. This can lead to:

* Service downtime going unnoticed
* Failed file transfers for clients
* Data synchronization issues

Using a process manager ensures that the FTP server is automatically restarted when it crashes, minimizing downtime and maintaining service availability.

Choose one of the following approaches:

Docker with PID 1
-----------------

Run the FTP server as PID 1 in a Docker container and configure Docker's restart policy::

   # Dockerfile
   FROM python:3.12
   # ... setup ...
   CMD ["python", "manage.py", "ftpserver", "0.0.0.0:21"]

.. code-block:: yaml

   # docker-compose.yml
   services:
     ftpserver:
       build: .
       restart: always
       ports:
         - "21:21"
         - "30000-30100:30000-30100"

systemd
-------

Create a systemd service unit file::

   # /etc/systemd/system/django-ftpserver.service
   [Unit]
   Description=Django FTP Server
   After=network.target

   [Service]
   Type=simple
   User=ftpuser
   WorkingDirectory=/path/to/your/project
   ExecStart=/path/to/venv/bin/python manage.py ftpserver 0.0.0.0:21
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

Enable and start the service::

   $ sudo systemctl enable django-ftpserver
   $ sudo systemctl start django-ftpserver

Supervisor
----------

Example supervisor configuration::

   # /etc/supervisor/conf.d/django-ftpserver.conf
   [program:django-ftpserver]
   command=/path/to/venv/bin/python manage.py ftpserver 0.0.0.0:21
   directory=/path/to/your/project
   user=ftpuser
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/django-ftpserver.log

Performance
===========

Disable Django Debug Mode
-------------------------

.. danger::

   In production environments, ``DEBUG`` must be set to ``False`` in your Django settings.

When Django's debug mode is enabled, it logs all database queries and keeps them in memory. This is an intentional memory leak for debugging purposes, but in a long-running FTP server process, it will cause memory usage to grow continuously until the process is terminated by the operating system.

Always ensure your production settings include::

   DEBUG = False

