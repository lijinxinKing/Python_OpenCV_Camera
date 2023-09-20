from pynput.keyboard import Key, Listener

def on_press(key):
    try:
        print('Key {} pressed.'.format(key.char))
    except AttributeError:
        print('Key {} pressed.'.format(key))

def on_release(key):
    print('Key {} released.'.format(key))

# 创建监听器
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()