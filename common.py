def _chk_ip_value(value):
    err_text = 'IP address supposed to be 4 integer number separated by ".", not {}'
    test_value = value.split('.')
    if len(test_value) != 4:
        print(err_text.format(value))
    else:
        counter = 0
        for x in test_value:
            try:
                x = int(x)
                if x == 0 and counter == 0:
                    print('IP address couldn\'t be started of zero')
                    return False
            except ValueError:
                print(err_text.format(value))
                return False
            else:
                if int(x) < 0 or int(x) > 254:
                    print(err_text.format(value))
                    return False
                counter += 1
        return True


def _chk_port_value(value):
    try:
        port = int(value)
    except ValueError:
        print('Port supposed to be integer value, not {}. Now we are using 7777'.format(value))
        return False
    else:
        if port > 65534 or port < 1024:
            print('Port supposed to be between 1024 and 65535, not {}. Now we are using 7777'.format(value))
            return False
        else:
            return True

