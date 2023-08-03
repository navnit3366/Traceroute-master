#!/urs/bin/python
# coding=UTF-8

import socket
import random
import struct
import time
import sys


def trace(destination, hops):
    # type: (str, int) -> None
    """
    Function that does the work previous to the tracert, such as choosing a port,
        finding the destination_ip and printing basic info about the command it
        was given.
    It also calls the function that does the tracert.
    :param destination: destination selected
    :param hops: max number of hops
    :return: None
    """

    port = random.choice(range(33434, 33535))

    try:
        # get the ip of the input destination
        destination_ip = socket.gethostbyname(destination)
    except socket.error as e:
        print('Unable to find ' + str(destination) + ': ' + str(e))
        return

    # print the traceroute command details
    print('traceroute to ' + str(destination) + ' ( ' + str(destination_ip) + ' ), ' + str(hops) + ' hops max\n')

    # print the header
    print_formatted('Hop', 'Address', 'Host Name', 'Time', True)

    # call the tracert
    aux_trace(destination, destination_ip, port, hops, 1)


def aux_trace(destination, destination_ip, port, hops, ttl):
    # type: (str, str, int, int, int) -> None
    """
    Recursive function that does the tracert
    :param destination: destination input by user
    :param destination_ip: ip of param destination
    :param port: port randomly chosen in trace
    :param hops: max number of hops
    :param ttl: count of hops that already happened
    :return: None
    """
    # create sockets
    receiver = create_receiver(port)
    sender = create_sender(ttl)

    # send data to socket
    sender.sendto(b'', (destination, port))

    # starting time
    start = time.time()

    address = None
    try:
        # receive data and address of the socket that sent the data
        data, address = receiver.recvfrom(1024)
    except socket.error:
        pass

    # ending time
    end = time.time()
    # calculate the response time
    response_time = round((end - start) * 1000, 2)

    if address:  # if recvfrom was successful
        addr = address[0]

        try:  # if possible it will get the host name
            host = socket.gethostbyaddr(addr)[0]
        except socket.error:  # otherwise it will just assume the host name is the ip itself
            host = addr

        print_formatted(ttl, addr, host, str(response_time) + 'ms', False)

        if address[0] == destination_ip:  # if it reached the desired destination
            print('\nreached destination\n')
            return

    else:  # if recvfrom was unsuccessful
        print_formatted(ttl, '*'*20, '*'*45, str(response_time) + 'ms', False)

    if ttl > hops:  # if it reached max number of hops
        print('\nreached max number of hops\n')
        return

    # recursive call
    aux_trace(destination, destination_ip, port, hops, ttl + 1)


def print_formatted(ttl, addr, host, resp_time, header):
    if header:
        print ('|{:<5}+{:<20}+{:<45}+{:<10}|'.format('-'*5, '-'*20, '-'*45, '-'*10))

    print ('|{:<5}|{:<20}|{:<45}|{:<10}|'.format(ttl, addr, host, resp_time))
    print ('|{:<5}+{:<20}+{:<45}+{:<10}|'.format('-'*5, '-'*20, '-'*45, '-'*10))


def create_receiver(port):
    """
    creating receiver socket
    """
    s = socket.socket(
        family=socket.AF_INET,  # indicates the address family used(ipv4)
        type=socket.SOCK_RAW,  # bypass OS TCP/IP
        proto=socket.IPPROTO_ICMP  # Internet Control Message Protocol
                                   # Used to send error messages and operational information
    )

    # how long it will wait until stops trying
    timeout = struct.pack('ll', 5, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
    # params(family, type, timeout)
    # SOL_SOCKET: Sets the socket protocol level
    # SO_RCVTIMEO: Specify the receiving or sending timeouts until reporting an error.

    try:
        s.bind(('', port))
    except socket.error as e:
        raise IOError('Unable to bind receiver socket: {}'.format(e))

    return s


def create_sender(ttl):
    """
    creating sender socket
    """
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM,  # Sets UDP protocol instead of TCP(SOCK_STREAM)
        proto=socket.IPPROTO_UDP  # Sets UDP protocol instead of TCP
    )

    # Changes the default value set by TCP/IP in TTL field of the IP header
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    return s


destination_input = sys.argv[1]
hops_input = int(sys.argv[2])
trace(destination_input, hops_input)
