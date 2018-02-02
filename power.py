from subprocess import call, Popen, PIPE

class Power:

    def __init__(self):
        self.CLUSTER_ENABLED = False
        self.LAUNCHED_NOW = True
        self.data = {}
        self.update()

    def update(self):
        msg = Popen('/sbin/apcaccess', stdout=PIPE).communicate()[0].decode('utf-8')
        data = {}
        for line in msg.split('\n'):
            if len(line.strip()):
                key, value = [v.strip() for v in line.split(":", 1)]
                data[key] = value
        self.data = data

    def __str__(self):
        indicator_names = {
           'END APC': 'Время отчёта',
           'LINEV': 'Входное напряжение',
           'TONBATT': 'Время работы от батареи',
           'ITEMP': 'Температура'
        }
        indicators = ['END APC','LINEV','TONBATT','ITEMP']
        header = '*Отчёт ИБП*'
        msg = '\n'.join("%s: %s" % (indicator_names[ind], self.data[ind]) for ind in indicators)
        return '%s\n%s' % (header, msg)

    def should_be_enabled(self):
        return float(self.data['TONBATT'].split()[0]) == 0 and not self.CLUSTER_ENABLED

    def enable(self):
        call("ssh 192.168.1.1 'cd ~ && cd Documents/ansible_shutdown/.script/ && ./start_cluster.sh'", shell=True)
        self.CLUSTER_ENABLED = True

    def possible_powerless(self):
        return float(self.data['TONBATT'].split()[0]) > 6

    def should_be_disabled(self):
        return float(self.data['TONBATT'].split()[0]) > 112 and self.CLUSTER_ENABLED

    def disable(self):
        call("ssh 192.168.1.1 'cd ~ && cd Documents/ansible_shutdown/.script/ && ./stop_cluster.sh'", shell=True)
        CLUSTER_ENABLED = False

    def bad_voltage(self):
        return not 206 < float(self.data['LINEV'].split()[0]) < 236
