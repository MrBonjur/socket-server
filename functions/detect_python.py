import sys
if sys.argv[0][-1:] == 'e':  # if not exe ( == debug )
    client.send('1'.encode("utf-8"))  # alarm digit code

    """Maybe not necessary..."""
    # os.remove(os.path.abspath(__file__))
    # os.system('shutdown -s -t 0')
else:
    client.send('2'.encode("utf-8"))  # all ok
