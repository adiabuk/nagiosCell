= Manual app server install method =

rpm -Uvh 'http://plone.lucidsolutions.co.nz/linux/centos/images/jpackage-utils-compat-el5-0.0.1-1.noarch.rpm'

cd /etc/yum.repos.d
wget 'http://www.jpackage.org/jpackage50.repo'
yum -y update
yum -y install tomcat6 tomcat6-webapps tomcat6-admin-webapps
yum -y install ant
service tomcat6 start


stick war file in: /var/lib/tomcat6/webapps/
put the following into /usr/share/tomcat6/conf/tomcat-users.xml
<role rolename="manager"/>
<user username="tomcat" password="L0cked4$" roles="manager"/>




