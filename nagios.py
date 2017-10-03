"""
Update Nagios cental server
"""

import logging
import socket
import func.overlord.client as fc

LOGGER = logging.getLogger("cellar")

def domain():
    """ get domain name """

    return '.'.join(socket.gethostname().split('.')[1:])

def environment():
    """
    Determine envionment from hostname
    """

    env = socket.gethostname().split('.')[1]
    mapper = {"dev": "DV",
              "nft": "NF",
              "test": "TT",
              "io": "IT",
              "prd": "PD"
             }
    try:
        return mapper[env]
    except KeyError:
        LOGGER.error("No such Environment")

def remove_config_files(source):
    """ Delete current config files """

    dest = "CHISP" + environment() + "SRV01" + "." + domain()
    sourcefolder = source.split(".")[0].upper()
    LOGGER.info("sourcefolder=/tmp/" +sourcefolder + "." + domain() + "/nagios.tgz")

    server = fc.Client(dest)
    LOGGER.info("Removing Nagios Configs for cell")

    # Delete Directory
    server.command.run("rm -rf /etc/nagios/cells/" + sourcefolder + "/")
    print "/etc/nagios/cells/"+sourcefolder+"/"

    # Restart Nagios
    server.command.run("/etc/init.d/nagios reload")

def get_config_files(source):
    LOGGER.info("Starting Nagios deployment")

    dest = "CHISP" + environment() + "SRV01" + "." + domain()
    sourcefolder = source.split(".")[0].upper()
    server = fc.Client(dest)
    client = fc.Client(source)

    LOGGER.debug("Gathering nagios config files from %s" % source)
    client.command.run("tar zcvf /tmp/nagios.tgz /etc/nagios/cells/*")

    remotesource = '/tmp/nagios.tgz'
    localfolder = '/tmp/'

    LOGGER.debug("Pulling nagios files from  management server")
    client.local.getfile.get(remotesource, localfolder)

    LOGGER.debug("Sending nagios tarball to " + dest)
    LOGGER.info("sourcefolder=/tmp/" +sourcefolder + "." + domain() + "/nagios.tgz")
    print server.local.copyfile.send("/tmp/" + sourcefolder + "." + domain() +
                                     "/nagios.tgz", "/tmp/nagios.tgz")

    LOGGER.debug("Extracting nagios config files to " + dest)
    server.command.run("tar zxvf /tmp/nagios.tgz -C / --exclude .svn "
                       "--exclude servicegroups.cfg")
    server.command.run("sed -i 's/.*check_command.*/\tcheck_command\t\t\t"
                       "service-is-stale/g' /etc/nagios/cells/"
                       + sourcefolder + "/services.cfg")
    server.command.run("rm /etc/nagios/cells/" + sourcefolder +
                       "/hostgroups.cfg")
    server.command.run("rm /etc/nagios/cells/" + sourcefolder +
                       "/services.cfg")

    LOGGER.debug("Restarting Nagios agent on " + dest)
    server.command.run("/etc/init.d/nagios restart")
    LOGGER.info("Finished Nagios deployment")
