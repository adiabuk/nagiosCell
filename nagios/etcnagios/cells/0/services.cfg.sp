

define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Check Apache
        check_command                   check_apache!10.2.225.11
        hostgroup_name                  web
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Connections port 8080
        check_command                   check_conn!8080
        hostgroup_name                	app
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Connections port 80
        check_command                   check_conn!80
        hostgroup_name                  web
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
        hostgroup_name                  app
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
        service_description             Disk IO Win
        check_command                   check_diskio_win
        hostgroup_name                       win
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             Oracle Port
        check_command                   check_remote_tcp!database-a!1526
        hostgroup_name                  app 
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             NSL Service
        check_command                   check_remote_http!nsl-a!/NSL/NSLService!80
        hostgroup_name                       app
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             JMX Heap
        check_command                   check_jmx_heap!
        hostgroup_name                       app 
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             JMX Threads
        check_command                   check_jmx_threads
        hostgroup_name 			app
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
	obsess_over_service		1
        service_description             DRM port
        check_command                   check_remote_tcp!10.2.225.31!50000
	hostgroup_name                	app 
        servicegroups                   cell0_services
        }

define service{
	use				generic-service
	obsess_over_service		1
	service_description		Local Apache instance
	check_command			check_remote_tcp!127.0.0.1!80
	hostgroup_name			web
	servicegroups			cell0_services
	}

define service{
	use				generic-service
	obsess_over_service		1
	service_description		Tomcat port accessible
	check_command			check_remote_tcp!10.2.225.21!8080
	hostgroup_name			web
	servicegroups			cell0_services
	}

#define service{
#        use                             generic-service
#        service_description             Disk Space
#        check_command                   check_disk
#        hostgroup_name                  linux
#        servicegroups                   cell0_services
#        }
define service{
        use                             generic-service
        service_description             Disk Space VarLog
        check_command                   check_disk_part!/var/log
        hostgroup_name                  linux
        servicegroups                   cell0_services
}

define service{
        use                             generic-service
        service_description             Disk Space Root
        check_command                   check_disk_part!/
        hostgroup_name                  linux
        servicegroups                   cell0_services
}

define service{
        use                             generic-service
        service_description             CPU Load
        check_command                   check_load
        hostgroup_name                       linux
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
        service_description             Memory Linux
        check_command                   check_mem
        hostgroup_name                  linux
        servicegroups                   cell0_services
        }
define service{
        use                             generic-service
        service_description             Memory
        check_command                   check_mem_win
        hostgroup_name                  win 
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
        service_description             Disk
        check_command                   check_disk_win
        hostgroup_name                  win
        servicegroups                   cell0_services
        }

define service{
        use                             generic-service
        service_description             CPU
        check_command                   check_cpu_win
        hostgroup_name                  win
        servicegroups                   cell0_services
        }

define service {

	use				generic-service
	obsess_over_service 		1
	service_description		Connections Established
	check_command			check_conn_all
	hostgroup_name			linux
	}
