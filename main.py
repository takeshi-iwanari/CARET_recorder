import sys
import os
import subprocess
import pexpect
import time
import PySimpleGUI as sg


class Value():
    is_local = True
    autoware_ecu_ip = '192.168.1.1'
    user = 'my_user'
    password = 'my_password'
    caret_dir = '~/ros2_caret_ws'
    trace_data_dir = '~/.ros/tracing'
    copy_dir = '~/computing_ws/tracing'


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

    tooltip_reset = 'Click if recording can\'t be started or trace data file size is too small'
    tooltip_check_ctf = 'Check if "Tracer discarded" warning doesn\'t exist'
    tooltip_trace_data_dir = 'trace data to be checked'
    tooltip_copy_dir = 'destination directory in local PC'

    sg.theme('dark')
    layout = [
                [sg.Text('Connection'),
                sg.Checkbox('Local', key=key_cb_local, default=Value.is_local, enable_events=True)],
                [sg.Text('IP Address: '),
                sg.Input(Value.autoware_ecu_ip, key=key_input_ip, s=20, enable_events=True)],
                [sg.Text('User: '),
                sg.Input(Value.user, key=key_input_user, s=12, enable_events=True),
                sg.Text('   Password: '),
                sg.Input(Value.password, key=key_input_password, password_char='*', s=12, enable_events=True)],
                [sg.Button('Test Connection', key=key_btn_test),
                sg.Text('', key=key_text_test)],
                [sg.HSep()],
                [sg.Text('CARET Dir: '), sg.Input(Value.caret_dir, key=key_input_caret_dir, enable_events=True)],
                [sg.Text('Record')],
                [sg.Button('Start Recording', key=key_btn_record),
                sg.Text('REC (please stop recording before closing this app)', key=key_text_record, text_color='RED', visible=False)],
                [sg.Button('!!! Reset (?)', key=key_btn_reset, tooltip=tooltip_reset)],
                [sg.HSep()],
                [sg.Text('Check')],
                [sg.Button('list', key=key_btn_list)],
                [sg.Button('check_ctf (?)', key=key_btn_check_ctf, tooltip=tooltip_check_ctf),
                sg.Input('', key=key_input_trace_data_dir, tooltip=tooltip_trace_data_dir, enable_events=True)],
                [sg.Button('trace_point_summary', key=key_btn_trace_point_summary),
                sg.Button('node_summary', key=key_btn_node_summary),
                sg.Button('topic_summary', key=key_btn_topic_summary)],
                [sg.HSep()],
                [sg.Text('Trace Data File')],
                [sg.Button('Copy to local', key=key_btn_copy),
                sg.Checkbox("Only today's log", key=key_cb_copy_today, default=True),
                sg.Input(Value.copy_dir, key=key_input_copy_dir, tooltip=tooltip_copy_dir, enable_events=True)],
                [sg.Button('!!! Remove All Trace Data', key=key_btn_remove)],
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
            for elem in cls.window.element_list():
                if elem.Type == sg.ELEM_TYPE_BUTTON and elem != cls.window[cls.key_btn_record]:
                    elem.update(disabled=True)
        elif status == 'recording':
            cls.window[cls.key_btn_record].update('Stop Recording')
            cls.window[cls.key_text_record].update('REC (please stop recording before closing this app)', visible=True)
        elif status == 'stoping':
            cls.window[cls.key_btn_record].update('Stoping')
        elif status == 'not recording':
            cls.window[cls.key_btn_record].update('Start Recording')
            cls.window[cls.key_text_record].update(visible=False)
            for elem in cls.window.element_list():
                if elem.Type == sg.ELEM_TYPE_BUTTON and elem != cls.window[cls.key_btn_record]:
                    elem.update(disabled=False)
            cls.update_connection_components()
        else:
            print(f'coding error !!!! {status}')


def run_command(cmd: str):
    # proc = subprocess.run([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Gui.output_text(proc.stdout)
    # return proc.stdout
    proc = subprocess.Popen([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = ''
    while True:
        buf = proc.stdout.readline()
        if buf == '':
            break
        text += buf
        # Gui.output_text(text)
        print(buf.strip())
    return text


def caret_record(no_wait=False):
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret record -v'
    Gui.update_record_components('starting')
    child = pexpect.spawn('/bin/bash', ['-c', cmd], logfile=sys.stdout, encoding='utf-8')
    time.sleep(0.1)
    child.sendline('')
    try:
        child.expect('press enter to stop')
    except:
        msg = f'Error: Please check if CARET is installed in {Value.caret_dir}'
        if not Value.is_local:
            msg = msg + ' in ' + Value.autoware_ecu_ip
        print(msg)
        sg.popup(msg)
        child.close()
        Gui.update_record_components('not recording')
        return False
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
            child.close()
            Gui.update_record_components('not recording')
            break
    return True

def test_connection():
    print('test_connection() is not yet implemented')


def record():
    caret_record()
    print('Done')


def get_latest_trace_data_path():
    cmd = f'cd {Value.trace_data_dir} && ls -rtd1 */ | tail -n 1'
    latest_file = run_command(cmd)
    if latest_file != '':
        latest_file = Value.trace_data_dir + '/' + latest_file.strip()
    return latest_file


def reset():
    if sg.PopupYesNo('Do you really want to reset LTTng session?') != 'Yes':
        print('canceled')
        return
    cmd = 'ps aux | grep -e lttng -e "ros2 caret record" | grep -v grep | awk \'{ print "kill -9", $2 }\' | sh'
    run_command(cmd)
    cmd = 'rm -rf ~/.lttng'
    run_command(cmd)
    if caret_record(True):
        latest_file = get_latest_trace_data_path()
        cmd = f'rm -rf {latest_file}'
        run_command(cmd)
    print('Done')


def trace_data_list():
    latest_file = get_latest_trace_data_path()
    Gui.update_value(Gui.key_input_trace_data_dir, latest_file)
    Gui.output_text('')
    cmd = f'cd {Value.trace_data_dir} && ls -rt1d */ | xargs du -sh'
    run_command(cmd)


def check_ctf():
    if sg.PopupYesNo('Do you really want to run check_ctf? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret check_ctf -d {Gui.get_value(Gui.key_input_trace_data_dir)}'
    run_command(cmd)


def trace_point_summary():
    if sg.PopupYesNo('Do you really want to run trace_point_summary? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret trace_point_summary -d {Gui.get_value(Gui.key_input_trace_data_dir)}'
    run_command(cmd)


def node_summary():
    if sg.PopupYesNo('Do you really want to run node_summary? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret node_summary -d {Gui.get_value(Gui.key_input_trace_data_dir)}'
    run_command(cmd)


def topic_summary():
    if sg.PopupYesNo('Do you really want to run topic_summary? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret topic_summary -d {Gui.get_value(Gui.key_input_trace_data_dir)}'
    run_command(cmd)


def copy_to_local():
    if sg.PopupYesNo('Do you really want to copy trace data?') != 'Yes':
        print('canceled')
        return
    option = ''
    if Gui.get_value(Gui.key_cb_copy_today):
        option = '-newermt `date "+%Y-%m-%d"` ! -newermt `date "+%Y-%m-%d"`" 23:59:59.9999"'
    cmd = f'mkdir -p {Value.copy_dir} &&' + \
        f'cd {Value.trace_data_dir} &&' + \
        f'find ./ -maxdepth 1 -mindepth 1 -type d {option} | xargs -I[] tar czvf [].tgz [] &&' + \
        f'mv *.tgz {Value.copy_dir}/.'
    run_command(cmd)
    print('Done')


def remove_trace_data():
    if sg.PopupYesNo('Do you really want to remove all trace data?') != 'Yes':
        print('canceled')
        return
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
        elif event == Gui.key_btn_test:
            test_connection()
        elif event == Gui.key_btn_record:
            record()
        elif event == Gui.key_btn_reset:
            reset()
        elif event == Gui.key_btn_list:
            trace_data_list()
        elif event == Gui.key_btn_check_ctf:
            check_ctf()
        elif event == Gui.key_btn_trace_point_summary:
            trace_point_summary()
        elif event == Gui.key_btn_node_summary:
            node_summary()
        elif event == Gui.key_btn_topic_summary:
            topic_summary()
        elif event == Gui.key_btn_copy:
            copy_to_local()
        elif event == Gui.key_btn_remove:
            remove_trace_data()

        Value.is_local = values[Gui.key_cb_local]
        Value.autoware_ecu_ip = values[Gui.key_input_ip]
        Value.user = values[Gui.key_input_user]
        Value.password = values[Gui.key_input_password]
        Value.caret_dir = values[Gui.key_input_caret_dir]
        Value.copy_dir = values[Gui.key_input_copy_dir]

    Gui.window.close()
    exit(0)


if __name__ == '__main__':
    main()
