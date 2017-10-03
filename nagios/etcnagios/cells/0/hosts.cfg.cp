define host{
    use             linux-server
    host_name       chi{pur}{env}{tin}{cell}{cell2}p{vm}
    alias           cpserver{vm}
    address         10.2.225.61
    hostgroups      linux,cp
}

define host{
    use             linux-server
    host_name       chi{pur}{env}{tin}{cell}{cell2}m{vm}
    alias           mgtserver{vm}
    address         10.2.225.1
    hostgroups      linux
}

