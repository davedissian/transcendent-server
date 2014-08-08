from os import urandom
from struct import pack
from time import time
from binascii import hexlify, unhexlify

class NPID(object):
    bytes = None
    _int  = None
    _hex  = None
    def __init__(self, bytes=None, integer=None, hex=None):
        if not bytes is None:
            self.bytes = bytes
        
        elif not integer is None:
            self._int = integer
            self.bytes = self._int_to_bytes(integer)

        elif not hex is None:
            self._hex = hex
            self.bytes = self._hex_to_bytes(hex)
        
        if self.bytes is None:
            self.bytes = NPID._gen_id()
        
        self._int = None
        self._hex = None

    def _int_to_bytes(self, i):
        b = pack('>I', i)
        if len(b) < 16:
            return b.rjust(16, '\0')
        return 

    def _hex_to_bytes(self, h):
        return unhexlify(h)

    @staticmethod
    def _gen_id():
        '''
        Generates an orderable random ID. The ID is orderable for about 136 
        years (at which point the timestamp will overflow), and should be 
        unique indefinitely.
       
        Schema:
            Bits 127 - 96:
                The UTC generation time in seconds since 2014-1-1.
            Bits 95 - 0:
                Uniformly distributed random data.

        This supports about 11 million IDs per second where the chance of a 
        random collision occuring is lower than the chance of an uncorrectable 
        bit error on a hard drive (1e-15).
        '''
        EPOCH = 1388534400 # 2014 - 1 - 1 - 00:00:00
        # The I format char to pack will always be 4 bytes long
        return pack('>I', int(time() - EPOCH)) + urandom(12)

    def hex(self):
        if self._hex is None:
            self._hex = hexlify(self.bytes)
        return self._hex

    def int(self):
        if not self._int is None:
            return self._int
        total = 0
        for b in self.bytes:
            total <<= 8
            total |= ord(b)
        self._int = total
        return total

    def __hex__(self):
        return self.hex()

    def __int__(self):
        return self.int()
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.bytes == other.bytes

    def __hash__(self):
        return self.int() >> 96

    def __cmp__(self, other):
        if not isinstance(other, self.__class__): return 1
        return cmp(self.int(), other.int())
    
    def __str__(self):
        return self.hex()

    def __repr__(self):
        return '<NPID "{0}">'.format(hex(self))

