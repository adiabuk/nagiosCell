define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Connections port 8080
        check_command                   check_conn!8080
        hostgroup_name                	cp
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Ping check
        check_command                   check_ping!100.0,50%!200.0,60%
        hostgroup_name                  *
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Local Tomcat port
        check_command                   check_remote_tcp!127.0.0.1!8080
        hostgroup_name                  cp
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Disk IO
        check_command                   check_diskio
        hostgroup_name                  linux
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
	obsess_over_service		1
        service_description             JMX Heap
        check_command                   check_jmx_heap!
        hostgroup_name                  cp 
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             JMX Threads
        check_command                   check_jmx_threads
        hostgroup_name 			cp
        servicegroups                   cell0_services
        }


define service{
        use                             generic-service
        service_description             Disk Space
        check_command                   check_disk
        hostgroup_name                  linux
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
        service_description             CPU Load
        check_command                   check_load
        hostgroup_name                  linux
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
        service_description             Memory Linux
        check_command                   check_mem
        hostgroup_name                  linux
        servicegroups                   cell0_services
        }


define service {

	use				generic-service
	obsess_over_service 		1
	service_description		Connections Established
	check_command			check_conn
	hostgroup_name			*
	}
