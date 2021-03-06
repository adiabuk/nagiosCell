define host{
    use             linux-server
    host_name       chi{pur}{env}{tin}{cell}{cell2}a{vm}
    alias           appserver{vm}
    address         10.2.225.21
    hostgroups      linux,app
}

define host{
    use             linux-server
    host_name       chi{pur}{env}{tin}{cell}{cell2}m{vm}
    alias           mgtserver{vm}
    address         10.2.225.1
    hostgroups      linux
}

define host{
    use             windows-server
    host_name       chi{pur}{env}{tin}{cell}{cell2}d{vm}
    alias           drmserver{vm}
    address         10.2.225.31
    hostgroups      win
}

define host{
    use             linux-server
    host_name       chi{pur}{env}{tin}{cell}{cell2}w{vm}
    alias           webserver{vm}
    address         10.2.225.11
    hostgroups      linux,web
}

