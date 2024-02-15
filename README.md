
# Robotless

## Description
This project helps recognize http clients by their fingerprints

### Now realized:

- **TLS** fingerprinting
- **WebGL** fingerprinting
- **Base Browser automation check**

Platform analyzes fingerprint and returns token, that contains short info about a client and his score

- **TRUSTED** - client has known good fingerprints and doesn't have blacklisted
- **UNTRUSTED** - client has unknown fingerprint, but not blacklisted
- **BLACKLISTED** - client has blacklisted fingerprint

### Stack:

- **python** with **django** - as main application with administration
- **mitmproxy** - as proxy for reading TLS client-hello messages
- **postgresql** - as main database
- **javascript** - as tool to collect fingerprints on browser side
- **docker** - as tool to collect TLS fingerprints of HTTP clients 
- **nginx** - as a server

### Installation

Short instructions:

1. install python 3.10
2. install requirements:
3. install postgresql
4. create ssl certificate
5. fill env variables from file .env.example
6. create database and apply migrations
7. seed database with command placed in backend (seeds.py)
8. route traffic to the mitmproxy port
9. run server with honcho

> Now service with demosite is up and ready to analyze traffic!
