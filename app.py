#!/usr/bin/python
#pylint: disable=logging-not-lazy,import-error

from __future__ import print_function
import itertools
import logging
import logging.config
import optparse
import os
import os.path
import socket
import sys
import time

import nagios
import virt
import cobbler
import templates
import anawatch
import ltm
import database

from ConfigParser import ConfigParser, NoOptionError
import func.overlord.client as fc

CEGCFG = "config/legs.cfg"
LCONFIG = ConfigParser()
LCONFIG.optionxform = str

PARSER = optparse.OptionParser()
PARSER.add_option("-r", "--revision", type="int", dest="revision",
                  help="SVN revision number", default=None)
PARSER.add_option("-c", "--cell", type="string", action="store",
                  dest="cell_name", help="Cell name", default=None)
PARSER.add_option("-n", "--new", action="store_true", dest="new",
                  help="Create cell if it doesn't already exist",
                  default=False)
PARSER.add_option("-t", "--ticket", type="string", dest="ticket",
                  help="Jira ticket reference", default=None)
PARSER.add_option("-v", "--variable", type="string", action="append",
                  dest="variables",
                  help="Additional variables for build scripts", default=[])
PARSER.add_option("-d", "--delete", action="store_true",
                  dest="delete", help="Delete cell and all configs for it",
                  default=False)
PARSER.add_option("-L", "--list", type="string", action="store",
                  dest="list_pattern", help="list all cells", default=None)
PARSER.add_option("-l", "--leg", type="string", action="store", dest="leg",
                  help="Environmental leg to align to", default=None)
PARSER.add_option("--nolb", action="store_true", dest="nolb", default=False,
                  help="Don't change anything on load balancers")

PARSER.usage = ("%prog -c CELL_NAME -t TICKET -l LEG -v VARIABLE \n"
                "or use %prog with -h for help message")
PARSER.description = ("For more details visit to "
                      "http://trac/wiki/cellar")

(OPTIONS, _) = PARSER.parse_args()

try:
    LCONFIG.readfp(open(CEGCFG))
except IOError:
    print("[  0] - Config file %s don't exist" %(CEGCFG))
    sys.exit(140)
except Exception:
    print("[  0] - Can't read config %s" %(CEGCFG))
    sys.exit(140)

ENV = socket.gethostname().split('.')[1]
if not LCONFIG.has_section(ENV):
    print("[  0] - Section for environment %s does not exist" % ENV)
    sys.exit(140)

def domain():

    return '.'.join(socket.gethostname().split('.')[1:])

def environment():

    return socket.gethostname().split('.')[1]

def fix_cell_name(cellName):
    env = socket.gethostname().split('.')[1]
    if len(cellName) >= 12:
        try:
            lmap = LCONFIG.get(ENV, OPTIONS.leg)
            ncellName = cellName[0:12] + lmap
            return ncellName
        except NoOptionError:
            print("No Leg %s in %s environment configured" % (OPTIONS.leg, env))
            sys.exit(115)
    else:
        return None

def main():

    if OPTIONS.list_pattern:
        list_cells(OPTIONS.list_pattern)
    elif OPTIONS.delete:
        delete()
    else:
        create()

def list_cells():
    return 0

def list_revisions():
    sPRevs = os.listdir('/export/')
    return sPRevs

def delete():

    if OPTIONS.cell_name is None:
        PARSER.print_usage()
        print("[  0] Please specify a cell name")
        sys.exit(127)

    if OPTIONS.leg is None:
        print("[  0] No leg reference passed!")
        sys.exit(129)

    leg = str(OPTIONS.leg).upper()

    OPTIONS.cell_name = fix_cell_name(OPTIONS.cell_name)
    if OPTIONS.cell_name is None:
        print("[  0] Cellname too short")
        sys.exit(115)
    print("[  1] Converted cell name to %s according to rules" % OPTIONS.cell_name)

    logger = logging.getLogger("cellar")
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sysh = logging.handlers.SysLogHandler(address=('syslog', 514), facility='local5')
    # create formatter
    sh_formatter = logging.Formatter("%(asctime)s - " + OPTIONS.cell_name + " - %(message)s")
    sysh_formatter = logging.Formatter(OPTIONS.cell_name + " - %(message)s")
    # add formatter to sh
    sh.setFormatter(sh_formatter)
    sysh.setFormatter(sysh_formatter)
    # add sh to logger
    logger.addHandler(sh)
    logger.addHandler(sysh)

    logger.info("cellar delete starting")

    vmlist = templates.cell_template(str(OPTIONS.cell_name[10:12]))["vms"]
    for machine in vmlist:
        vmtmpl = templates.vm_template(machine)
        if "lbport" in vmtmpl and not OPTIONS.nolb:
            ltm.remove_member("pool-" + vmtmpl['profile'] + '-' +
                              leg, OPTIONS.cell_name + machine, vmtmpl['lbport'])
        cobbler.delete_system(OPTIONS.cell_name + machine)
        virt.delete_vm(machine, OPTIONS.cell_name, 0)

    mgt = "U1" if "CM" in OPTIONS.cell_name else "M1"
    nagios.remove_config_files(OPTIONS.cell_name + mgt + domain())
    m1_func_cert = ("/var/lib/certmaster/certmaster/certs/" +
                    OPTIONS.cell_name + mgt + domain())
    if os.path.exists(m1_func_cert):
        os.unlink(m1_func_cert)


def create():

    if OPTIONS.cell_name is None:
        PARSER.print_usage()
        print("[  0] Please specify a cell name")
        sys.exit(127)

    if OPTIONS.leg is None:
        print("[  0] No leg reference passed!")
        sys.exit(129)

    leg = str(OPTIONS.leg).upper()

    OPTIONS.cell_name = fix_cell_name(OPTIONS.cell_name)
    if OPTIONS.cell_name is None:
        print("[  0] Cellname too short")
        sys.exit(115)
    print("[  1] Converted cell name to %s according to rules" % OPTIONS.cell_name)

    logger = logging.getLogger("cellar")
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sysh = logging.handlers.SysLogHandler(address=('syslog', 514),
                                          facility='local5')
    # create formatter
    sh_formatter = logging.Formatter("%(asctime)s - " + OPTIONS.cell_name +
                                     " - %(message)s")
    sysh_formatter = logging.Formatter(OPTIONS.cell_name + " - %(message)s")
    # add formatter to sh
    sh.setFormatter(sh_formatter)
    sysh.setFormatter(sysh_formatter)
    # add sh to logger
    logger.addHandler(sh)
    logger.addHandler(sysh)

    if OPTIONS.ticket is None:
        logger.exception("[  0] No ticket reference passed!")
        sys.exit(126)

    if OPTIONS.variables:
        cProps = {}
        for var in OPTIONS.variables:
            cProps[var.split("=")[0]] = var.split("=")[1]

        if 'MCC' not in cProps:
            if OPTIONS.cell_name[10:12] == 'SP' or OPTIONS.cell_name[10:12] == 'DC':
                logger.exception("[  0] SP or DC cell chosen, but DC group "
                                 "not specified. Use -v MCC= to specify.")
                sys.exit(128)
        if 'SAM' in cProps:
            test = cProps['SAM'].lower()
            if test not in ['live', 'stub']:
                logger.exception("[  0] SAM variable should be used with "
                                 "either 'live' or 'stub' value")
                sys.exit(129)
        if 'MPP' in cProps:
            test = cProps['MPP'].lower()
            if test not in ['live', 'stub']:
                logger.exception("[  0] MPP variable should be used with "
                                 "either 'live' or 'stub' value")
                sys.exit(129)
        if 'LIVETV' in cProps:
            test = cProps['LIVETV'].lower()
            if test not in ['live', 'stub']:
                logger.exception("[  0] LIVETV variable should be used with "
                                 "either 'live' or 'stub' value")
                sys.exit(129)
        if 'PLAYER' not in cProps:
            logger.exception("[  0] Player revision not specified. "
                             "Use -v PLAYER= to specify")
            sys.exit(123)
        if cProps['PLAYER'] not in list_revisions():
            logger.exception("[  0] Player revision %s not found!"
                             % cProps['PLAYER'])
            logger.exception("[  0] %s: %s" %("Available revisions are",
                             ", ".join(list_revisions())))
            sys.exit(124)

    logger.info("[  1] cellar build starting")
    found_revision = os.path.realpath(__file__).split('/')[-3]
    start_time = int(time.time())
    # Check that revision exists
    revision = OPTIONS.revision
    if OPTIONS.revision:
        if found_revision == "trunk":
            if not os.path.isdir("/export/infrastructure/%d" % OPTIONS.revision):
                logger.exception("[  4] Revision not found! %d" % OPTIONS.revision)
                sys.exit(124)
            else:
                logger.info("[  5] Building revision %s" % OPTIONS.revision)
        else:
            logger.exception("[  3] Can not specify a revision when running "
                             "from a deployed version!")
            sys.exit(139)
    else:
        if found_revision == "trunk":
            revision = None
        else:
            revision = found_revision
        logger.info("[  8] Building revision %s" % revision)

    # Check that physical machine exists in Cobbler

    tin_fqdn = OPTIONS.cell_name[0:10] + '.' + domain()
    tin_name = OPTIONS.cell_name[0:10]

    mgt = "U1" if "CM" in OPTIONS.cell_name else "M1"

    m1_func_cert = "/var/lib/certmaster/certmaster/certs/" + OPTIONS.cell_name + mgt + domain()
    if os.path.exists(m1_func_cert):
        logger.info("[  9] Deleting func certificate %s" % m1_func_cert)
        os.unlink(m1_func_cert)
    else:
        logger.info("[  9] Cell not previously registered with func")

    vmtmpl = {}
    vmlist = templates.cell_template(str(OPTIONS.cell_name[10:12]))["vms"]
    for vm in vmlist:
        vmtmpl[vm] = templates.vm_template(vm)
        if "lbport" in vmtmpl[vm] and not OPTIONS.nolb:
            ltm.offline_member("pool-" + vmtmpl[vm]['profile'] +
                               '-' + leg, OPTIONS.cell_name + vm,
                               vmtmpl[vm]['lbport'])


    # Check for systems and create if it doesn't exist
    do_cobbler_sync = False
    for i, vm in enumerate(vmlist):
        while os.path.isfile("/var/lock/cellar.lock"):
          time.sleep(5)
          print("Lockfile found - sleeping for 5 seconds")
        open("/var/lock/cellar.lock", "a")
        if not OPTIONS.new and not cobbler.system_exists(OPTIONS.cell_name + vm):
            logger.exception("[ %d] System %s%s does not already exist, "
                             "not permitted to create it."
                             % (10 + 3*i, OPTIONS.cell_name, vm))
            sys.exit(125)
        cobbler.delete_system(OPTIONS.cell_name + vm)
        cobbler.add_system(OPTIONS.cell_name + vm, revision,
                           OPTIONS.ticket, leg, 10 + 3*i, OPTIONS.variables)
        do_cobbler_sync = True
        os.remove("/var/lock/cellar.lock")
    if do_cobbler_sync:
        logger.info("[ 25] Synchronizing Cobbler data")
        cobbler.sync()

    for i, vm in enumerate(vmlist):
        logger.info("[ %d] Deleting VM %s if it already exists" % (26 + i, OPTIONS.cell_name + vm))
        virt.delete_vm(vm, OPTIONS.cell_name, 26 + i)

    mgt = "U1" if "CM" in OPTIONS.cell_name else "M1"

    nagios.remove_config_files(OPTIONS.cell_name + mgt + domain())

    # Group VM templated by their stage number,
    # and iterate through each stage until all nodes in that stage are
    # fully installed and back up again.
    for stage, vms in itertools.groupby(sorted(vmtmpl.iteritems(),
                                               key=lambda(k, v): v["stage"]),
                                               key=lambda(k, v): v["stage"]):
        pc = 30 + 20 * stage
        logger.info("[ %d] Installing VM's on stage %d" % (pc, stage))
         # can only iterate through the vms object once,
         # seems to be destructive in its reading.
         # This copy can be reused. Don't understand why.
        vmx = list(vms)

        for i, (vm, data) in enumerate(vmx):
            virt.install_vm(vm, OPTIONS.cell_name, pc + i + 2)
            logger.info("[ %d] VM %s is now installing"
                        % (pc + i + 2, OPTIONS.cell_name + vm))

        # wait for all vm's to become shutdown and then restart
        # and give them a short head start
        anamon_list = []
        for vm, data in vmx:
            if data["anamon"]:
                logger.info("[ %d] Watching anamon logs for %s" % (pc + 3, OPTIONS.cell_name + vm))
                anawatch.purge(OPTIONS.cell_name + vm)
                anamon_list.append(OPTIONS.cell_name + vm)
        anawatch.watch_anaconda(anamon_list)

        status = ""
        while status != "shutdown":
            time.sleep(5)
            status = "shutdown"
            for vm, data in vmx:
                # logic needs improving for multiple staged systems:
                vmstatus = virt.vm_status(vm, OPTIONS.cell_name)
                if vmstatus != "shutdown":
                    status = vmstatus
                logger.info("[ %d] Status of %s: %s" % (pc + 10, OPTIONS.cell_name + vm, vmstatus))
         # could be in previous loop to allow different restart times,
         # not all at same time per stage.
        for i, (vm, data) in enumerate(vmx):
            logger.info("[ %d] Starting installed VM %s%s" % (pc + 11 + i, OPTIONS.cell_name, vm))
            virt.create_vm(vm, OPTIONS.cell_name, pc + 11 + i)

        anamon_list = []
        for i, (vm, data) in enumerate(vmx):
            if data["anamon"]:
                logger.info("[ %d] Watching messages logs for %s"
                            % (pc + 15 + i, OPTIONS.cell_name + vm))
                anamon_list.append(OPTIONS.cell_name + vm)
        anawatch.watch_messages(anamon_list)

    logger.info("[ 80] All VMs successfully built")


    cell_type = OPTIONS.cell_name[10:12]


    mgt = "U1." if "CM" in OPTIONS.cell_name else "M1."

    nagios.get_config_files(OPTIONS.cell_name + mgt + domain())

    if OPTIONS.variables and 'MCC' in cProps:
        if  cell_type == 'SP' or cell_type == 'DC':
            for vm in vmlist:
                if vm == 'A1' or vm == 'C1':
                    fullname = '%s%s' %(OPTIONS.cell_name, vm)
                    database.generateQrtzTables(fullname)

    for vm in vmlist:
        if 'lbport' in vmtmpl[vm] and not OPTIONS.nolb:
            ltm.add_member("pool-" + vmtmpl[vm]['profile'] + '-' +
                           leg, OPTIONS.cell_name + vm, vmtmpl[vm]['lbport'])
            ltm.enable_member("pool-" + vmtmpl[vm]['profile'] + '-' +
                              leg, OPTIONS.cell_name + vm, vmtmpl[vm]['lbport'])

    length = int(time.time()) - start_time
    logger.info("[100] Build of %s complete, in %d:%02d. It's been magical."
                % (OPTIONS.cell_name, length/60, length%60))

    sys.exit(0)
