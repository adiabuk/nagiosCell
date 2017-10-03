#!/usr/bin/perl -i

# Populates the hostnames of the nagios config files


use Sys::Hostname;
use File::Find;
use File::Path;
use File::Copy;
use Switch;

rmtree(["/etc/nagios"]);
`cd /tmp; tar zxvf /tmp/etcnagios.tgz`;
`cp -rvpf /tmp/etcnagios /etc/nagios`;
$host = hostname;
print $host ."\n";

my $pur, $env, $tin, $cell, $vm;
if ($host =~ /CHI(\w\w)(\w\w)(\d\d\d)(\w\w)(\d)(\w)(\d)/)
{
   $pur=lc($1);
   $env=lc($2);
   $tin=lc($3);
   $cell=lc($4);
   $cell2=lc($5);
   $mgt=lc($6);
   $vm=$7;
print "pur=$pur\n";
print "env=$env\n";
print "tin=$tin\n";
print "cell=$cell\n";
print "vm=$vm\n";
}
$shorthost=uc("CHI$pur$env$tin$cell$cell2$mgt$vm");

switch($cell)
{
case "sp" { $file = '/etc/nagios/cells/0/hosts.cfg.sp' }
case "cp" { $file = '/etc/nagios/cells/0/hosts.cfg.cp' }
case "ns" { $file = '/etc/nagios/cells/0/hosts.cfg.ns' }
case "dc" { $file = '/etc/nagios/cells/0/hosts.cfg.dc' }
case "cm" { $file = '/etc/nagios/cells/0/hosts.cfg.cm' }
else { $file = '/etc/nagios/cells/0/hosts.cfg' }
}

`mv /etc/nagios/cells/0/services.cfg.$cell /etc/nagios/cells/0/services.cfg`;
`mv $file /etc/nagios/cells/0/hosts.cfg`;

@ARGV = '/etc/nagios/cells/0/hosts.cfg';
while ( <> ) {
  s/{pur}/$pur/ ; 
  s/{env}/$env/ ; 
  s/{tin}/$tin/ ; 
  s/{cell}/$cell/ ;
  s/{cell2}/$cell2/ ; 
  s/{vm}/$vm/ ; 
  print;
}

`mv /etc/nagios/cells/0 /etc/nagios/cells/$shorthost`;
`/sbin/chkconfig nagios on`;
