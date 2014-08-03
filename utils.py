import urllib2
import time


def attempts(max_attempts, default_value, wait=4):  # F is func or method without instance
    def wrap(function):

        def wrapper(*args, **kwargs):  # class instance in args[0] for method
            curr_attempts = 0
            return_value = default_value
            while curr_attempts < max_attempts:
                try:
                    return_value = function(*args, **kwargs)
                    break
                except urllib2.HTTPError as inst:
                    print "HTTPError. Attempts: {0} Error: {1}".format(curr_attempts, inst)
                    curr_attempts += 1
                    time.sleep(wait)
            return return_value

        return wrapper

    return wrap