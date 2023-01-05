import sys
import os
import subprocess
import pexpect
import time
import PySimpleGUI as sg


class Value():
    autoware_ecu_ip = '192.168.1.1'
    trace_data_dir = '~/.ros/tracing'
    caret_dir = '~/ros2_caret_ws'
    copy_dir = '~/computing_ws/tracing'
    user = 'my_user'
    password = 'my_password'


class Gui():
    key_cb_local = '-local-'
    key_input_ip = '-IP Address-'
    key_input_user = '-user-'
    key_input_password = '-password-'
    key_btn_test = '-test-'
    key_text_test = '-test_text-'
    key_input_caret_dir = '-CARET dir-'
    key_btn_record = '-record-'
    key_text_record = '-record_text-'
    key_btn_reset = '-reset-'
    key_btn_list = '-trace_data_list-'
    key_btn_check_ctf = '-check_ctf-'
    key_btn_trace_point_summary = '-trace_point_summary-'
    key_btn_node_summary = '-node_summary-'
    key_btn_topic_summary = '-topic_summary-'
    key_btn_copy = '-copy-'
    key_input_trace_data_dir = '-trace_data_dir-'
    key_btn_remove = '-remove-'
    key_cb_copy_today = '-copy_today-'
    key_input_copy_dir = '-copy_dir-'
    key_text_output = '-output-'

    layout = [
                [sg.Text('Connection'),
                sg.Checkbox('Local', key=key_cb_local, enable_events=True, default=True)],
                [sg.Text('IP Address: '),
                sg.Input(Value.autoware_ecu_ip, key=key_input_ip, s=20)],
                [sg.Text('User: '),
                sg.Input(Value.user, key=key_input_user, s=12),
                sg.Text('   Password: '),
                sg.Input(Value.password, key=key_input_password, s=12)],
                [sg.Button('Test Connection', key=key_btn_test),
                sg.Text('', key=key_text_test)],
                [sg.HSep()],
                [sg.Text('CARET Dir: '), sg.Input(Value.caret_dir, key=key_input_caret_dir)],
                [sg.Text('Record')],
                [sg.Button('Start Recording', key=key_btn_record),
                sg.Text('REC (please stop recording before closing this app)', key=key_text_record, text_color='RED', visible=False)],
                [sg.Button('Reset', key=key_btn_reset)],
                [sg.HSep()],
                [sg.Text('Check')],
                [sg.Button('list', key=key_btn_list)],
                [sg.Button('check_ctf', key=key_btn_check_ctf),
                sg.Input('', key=key_input_trace_data_dir)],
                [sg.Button('trace_point_summary', key=key_btn_trace_point_summary),
                sg.Button('node_summary', key=key_btn_node_summary),
                sg.Button('topic_summary', key=key_btn_topic_summary)],
                [sg.HSep()],
                [sg.Text('Trace Data File')],
                [sg.Button('Copy to local', key=key_btn_copy),
                sg.Checkbox("Only today's log", key=key_cb_copy_today, default=True),
                sg.Input(Value.copy_dir, key=key_input_copy_dir)],
                [sg.Button('Remove All Trace Data', key=key_btn_remove)],
                [sg.HSep()],
                [sg.Multiline(size=(60,15), key=key_text_output, expand_x=True, expand_y=True, write_only=True,
                              reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True,  auto_refresh=True)],
            ]

    window = sg.Window('CARET Record', layout, resizable=True, finalize=True)

    @classmethod
    def get_value(cls, key: str):
        return Gui.window[key].get()

    @classmethod
    def update_value(cls, key: str, args: str):
        Gui.window[key].update(args)

    @classmethod
    def output_text(cls, text: str):
        cls.window[cls.key_text_output].update(text)
        cls.window.Refresh()

    @classmethod
    def update_connection_components(cls):
        disable = cls.get_value(cls.key_cb_local)
        connection_keys = [cls.key_input_ip, cls.key_input_user, cls.key_input_password, cls.key_btn_test]
        for key in connection_keys:
            cls.window[key].update(disabled=disable)

    @classmethod
    def update_record_components(cls, status: str):
        if status == 'starting':
            cls.window[cls.key_btn_record].update('Starting')
            cls.window[cls.key_text_record].update('Please wait until recording is started', visible=True)
        elif status == 'recording':
            cls.window[cls.key_btn_record].update('Stop Recording')
            cls.window[cls.key_text_record].update('REC (please stop recording before closing this app)', visible=True)
        elif status == 'stoping':
            cls.window[cls.key_btn_record].update('Stoping')
        elif status == 'not recording':
            cls.window[cls.key_btn_record].update('Start Recording')
            cls.window[cls.key_text_record].update(visible=False)
        else:
            print(f'coding error !!!! {status}')


def run_command(cmd: str):
    # proc = subprocess.run([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Gui.output_text(proc.stdout)
    # return proc.stdout
    proc = subprocess.Popen([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = ''
    while True:
        buf = proc.stdout.readline()
        if buf == '':
            break
        text += buf
        Gui.output_text(text)
    return text


def caret_record(no_wait=False):
    caret_dir = Gui.get_value(Gui.key_input_caret_dir)
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret record -v'
    Gui.update_record_components('starting')
    child = pexpect.spawn('/bin/bash', ['-c', cmd], logfile=sys.stdout, encoding='utf-8')
    time.sleep(0.1)
    child.sendline('')
    child.expect('press enter to stop')
    Gui.update_record_components('recording')
    while True:
        time.sleep(0.1)
        if no_wait:
            event = Gui.key_btn_record
        else:
            event, values = Gui.window.read()
        if event == Gui.key_btn_record:
            Gui.update_record_components('stoping')
            child.sendline('')
            child.expect('destroying tracing session')
            Gui.update_record_components('not recording')
            break


def record():
    caret_record()
    print('Done')


def reset():
    # todo: msg box to ask are you sure?
    cmd = 'ps aux | grep -e lttng -e "ros2 caret record" | grep -v grep | awk \'{ print "kill -9", $2 }\' | sh'
    run_command(cmd)
    cmd = 'rm -rf ~/.lttng'
    run_command(cmd)
    caret_record(True)
    print('Done')


def trace_data_list():
    Gui.output_text('')
    cmd = f'cd {Value.trace_data_dir} && ls -rtd ./* | tail -n 1'
    latest_file = run_command(cmd)
    if latest_file != '':
        latest_file = Value.trace_data_dir + '/' + latest_file
    Gui.update_value(Gui.key_input_trace_data_dir, latest_file)
    cmd = f'du -sh {Value.trace_data_dir}/*'
    run_command(cmd)


def copy_to_local():
    cmd = f'mkdir -p {Value.copy_dir} &&' + \
        f'cd {Value.trace_data_dir} &&' + \
        f'ls -d * | xargs -I[] tar czvf [].tgz [] &&' + \
        f'mv *.tgz {Value.copy_dir}/.'
    run_command(cmd)
    print('Done')


def remove_trace_data():
    cmd = f'rm -rf {Value.trace_data_dir}/*'
    run_command(cmd)
    print('Done')


def main():
    Gui.update_connection_components()
    Gui.update_record_components('not recording')

    while True:
        event, values = Gui.window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == Gui.key_cb_local:
            Gui.update_connection_components()
        elif event == Gui.key_btn_record:
            record()
        elif event == Gui.key_btn_reset:
            reset()
        elif event == Gui.key_btn_list:
            trace_data_list()
        elif event == Gui.key_btn_copy:
            copy_to_local()
        elif event == Gui.key_btn_remove:
            remove_trace_data()

    Gui.window.close()
    exit(0)


if __name__ == '__main__':
    main()
