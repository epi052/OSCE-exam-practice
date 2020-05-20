from pathlib import Path

from boofuzz import *

tgt_ip = "127.0.0.1"
tgt_port = 9999  # vulnserver

# put the csv beside this script, regardless of where its ran from
fuzz_dir = Path(__file__).parent.resolve()  
txt_file = Path(fuzz_dir) / "fuzz_logs.txt"

# one logger to console, the other to a CSV
loggers = [FuzzLoggerText(file_handle=txt_file.open('w'))]  # only logging to a txt file drastically improved speed on my VM

# client for process_monitor.py
client = pedrpc.Client(tgt_ip, 26002)

# used by process_monitor.py to know how to restart vulnserver
# list of list structure suggested here: https://github.com/jtpereyda/boofuzz/issues/261#issuecomment-475082950
start_vulnserver = [["C:\\users\\vagrant\\desktop\\vulnserver\\vulnserver.exe"]]
kill_vulnserver = [['powershell -c "stop-process -name vulnserver -force"']]

connection = SocketConnection(tgt_ip, tgt_port, proto="tcp")

# using stop_commands requires a change to boofuzz\utils\process_monitor_pedrpc_server.py
# @@ -202,12 +202,13 @@ class ProcessMonitorPedrpcServer(pedrpc.Server):
#          if len(self.stop_commands) < 1:
#              self.debugger_thread.stop_target()
#          else:
# -            for command in self.stop_commands:
# -                if command == "TERMINATE_PID":
# -                    self.debugger_thread.stop_target()
# -                else:
# -                    self.log("Executing stop command: '{0}'".format(command), 2)
# -                    os.system(command)
# +            for command_list in self.stop_commands:
# +                for command in command_list:
# +                    if command == "TERMINATE_PID":
# +                        self.debugger_thread.stop_target()
# +                    else:
# +                        self.log("Executing stop command: '{0}'".format(command), 2)
# +                        os.system(command)
options = {"start_commands": start_vulnserver, "stop_commands": kill_vulnserver, "proc_name": "vulnserver.exe"}
target = Target(connection=connection, procmon=client, procmon_options=options)

# for fuzzing to not crap out every few hundred test cases, i added an additional socket error to be passed on instead of raised
#   errno.ECONNRESET
# boofuzz\monitors\pedrpc.py
# 259: if e.errno == errno.ENOTCONN or e.errno == errno.ECONNRESET:
session = Session(target=target, restart_interval=150, fuzz_loggers=loggers)

s_initialize("vulnserver-fuzzcase")  # arbitrary name for overall fuzz case

# fuzzing directives go here
s_string("KSTET", fuzzable=False)  # change me 
s_delim(" ", fuzzable=False)
s_string("something")

req = s_get("vulnserver-fuzzcase")

session.connect(req)

print(f"fuzzing with {req.num_mutations()} mutations")

session.fuzz()  # do the thing!
