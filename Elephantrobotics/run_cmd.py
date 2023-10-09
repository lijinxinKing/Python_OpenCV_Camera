import subprocess
def run_cmd_Popen_PIPE(cmd_string):
    """
    执行cmd命令，并得到执行后的返回值,python调试界面不输出返回值
    :param cmd_string: cmd命令，如：'adb devices"'
    :return:
    """
    print('运行cmd指令：{}'.format(cmd_string))
    return subprocess.Popen(cmd_string, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='gbk').communicate()[0]
