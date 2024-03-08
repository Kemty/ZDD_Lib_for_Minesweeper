### タイムアウト機能 ###

# 下記Qiita記事からお借りしました. 御礼申し上げます.
# https://qiita.com/Jacomb/items/92503b11aef68ec4748a#%E3%82%BF%E3%82%A4%E3%83%A0%E3%82%A2%E3%82%A6%E3%83%88%E3%81%AE%E3%82%B3%E3%83%B3%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%83%9E%E3%83%8D%E3%83%BC%E3%82%B8%E3%83%A3%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%82%8B

import errno
import contextlib
import ctypes
import threading

class TimeoutException(IOError):
    errno = errno.EINTR

@contextlib.contextmanager
def time_limit_with_thread(timeout_secs):
    thread_id = ctypes.c_long(threading.get_ident())
    def raise_exception():
        modified_thread_state_nums = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(TimeoutException))
        if modified_thread_state_nums == 0:
            raise ValueError('Invalid thread id. thread_id:{}'.format(thread_id))
        elif modified_thread_state_nums > 1:
            # 通常このパスを通ることはないが、念のため保留中のExceptionをクリアしておく
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            raise SystemError('PyThreadState_SetAsyncExc failure.')

    timer = threading.Timer(timeout_secs, raise_exception)
    timer.setDaemon(True)
    timer.start()
    try:
        yield
    finally:
        timer.cancel()
        timer.join()