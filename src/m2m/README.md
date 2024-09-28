# M2M

Machine-to-Machine (M2M) is an old school term that most consider to be synonymous with 
the Internet of Things (IoT).  IOT projects (& this one) connect securely to an enterprise 
message broker such as `HiveMQ` or `AWS IoT Broker` or `Mosquitto` or ...

Like most IoT projects, we use MQTT as the message transport layer.  The beauty
and simplicity of this is that we are a simple MQTT client that connects securely
(& outwardly) to a message broker to pass json &/or delimited messages over the HTTPS protocol.

What could be cleaner than a very small pure python listener that does exactly what is needed
to securely execute low-level commands on a **server**...  It works equally well with containers,
VMS's or physical servers (the term **machine** is used to generically refer to any of the three).   

It today in pgEdge as a very small/simple daemon; (1) on prem (even in air gapped systems), (2) in **ALL** Public Clouds, (3) in Private\Hybrid Clouds.
In other words it works today for **pgEdge** Platform & CLI.   As something else quite kewl our pgEdge
Cloud environment already uses and depends on an MQTT Broker.  Today the cloud only taks to the `Uhura` which (AFAIK)
smashes together cloud based telemetry tracking with simple MQ to create a (perfectly valid) thing that
our Cloud is using to do both.    This is 100% independant of that.

<img src=img/mqtt-cli-example.png>


## 1) Connect to a HiveMQ Cloud test broker (or use mosquitto or ...)

## 2) Record the BROKER_URL, _USER, & _PASSWORD in `env.sh` 

## 3) Run`m2m.py` to connect securely to an mqtt broker

## 4) Send commands to our m2m listener (and believe in secure magic)


